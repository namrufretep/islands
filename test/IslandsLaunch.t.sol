// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Test} from "forge-std/Test.sol";
import {IslandsLaunch} from "../contracts/IslandsLaunch.sol";
import {MintTestKey,MintRejectingReceiver,MintFeeKey} from "./KeyMintMocks.sol";

contract IslandsLaunchTest is Test {
    address constant CREATOR=address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1"));
    address constant KEY=address(bytes20(hex"b0ca1e094a1779018b194ac6151ece8d6f05db07"));
    uint256 constant SIGNER_KEY=0xBEEF;
    string constant URI="https://islands-kappa.vercel.app/nft/000001-N.json";
    address alice=address(0xA11CE);
    address bob=address(0xB0B);
    IslandsLaunch nft;
    MintTestKey key;
    function setUp() public {
        vm.chainId(8453);vm.warp(1000);vm.roll(1000);
        MintTestKey template=new MintTestKey();vm.etch(KEY,address(template).code);key=MintTestKey(KEY);
        nft=new IslandsLaunch();key.mint(alice,1000000 ether);
        vm.prank(alice);key.approve(address(nft),750000 ether);
        vm.startPrank(CREATOR);
        nft.registerEdition(1,false,URI,bytes32(uint256(123)));
        nft.setMintOffer(1,URI,750000 ether);
        vm.stopPrank();
    }
    function enable() internal {
        vm.startPrank(CREATOR);nft.setDiscountVerifier(vm.addr(SIGNER_KEY));nft.setKeyMintEnabled(true);vm.stopPrank();
    }
    function quote() internal view returns(IslandsLaunch.MintQuote memory) {
        return IslandsLaunch.MintQuote(alice,bob,1,750000 ether,50,999,1000,1300,0,nft.verifierVersion(),keccak256(bytes(URI)));
    }
    function sign(IslandsLaunch.MintQuote memory q) internal view returns(bytes memory) {
        (uint8 v,bytes32 r,bytes32 s)=vm.sign(SIGNER_KEY,nft.quoteDigest(q));return abi.encodePacked(r,s,v);
    }
    function mint(IslandsLaunch.MintQuote memory q,bytes memory sig,uint256 price) internal {
        vm.prank(alice);nft.mintWithStakingQuote(q,sig,price);
    }
    function testLaunchStartsClosedAndVerifierUnset() public view {
        assertFalse(nft.keyMintEnabled());assertEq(nft.discountVerifier(),address(0));
        assertEq(nft.owner(),CREATOR);assertEq(nft.MINT_PROCEEDS_RECIPIENT(),CREATOR);
    }
    function testRejectOtherNetwork() public {
        vm.chainId(84532);vm.expectRevert("Base mainnet only");new IslandsLaunch();
    }
    function testStableNorthSouthAllocation() public view {
        assertEq(nft.editionTokenId(1,false),1);assertEq(nft.editionTokenId(1,true),2);
        assertEq(nft.editionTokenId(100,false),199);assertEq(nft.editionTokenId(100,true),200);
        assertEq(nft.editionTokenId(500,true),1000);
    }
    function testCannotRebindEditionOrUseUnregisteredURI() public {
        vm.startPrank(CREATOR);
        vm.expectRevert("Edition already registered");nft.registerEdition(1,false,URI,bytes32(uint256(4)));
        vm.expectRevert("Wrong canonical metadata URI");nft.registerEdition(1,true,URI,bytes32(uint256(4)));
        vm.expectRevert("Unregistered or changed edition");nft.setMintOffer(1,"ipfs://other",750000 ether);
        vm.expectRevert("Unregistered or changed edition");nft.issue(bob,2,URI);
        vm.expectRevert("Direct price must be 750000 KEY");nft.setMintOffer(1,URI,1);
        vm.stopPrank();
    }
    function testOnlyOwnerMayRegisterOrConfigureVerifier() public {
        vm.startPrank(alice);vm.expectRevert();nft.registerEdition(2,false,URI,bytes32(uint256(4)));
        vm.expectRevert();nft.setDiscountVerifier(alice);vm.stopPrank();
    }
    function testDirectFullPriceAndCanonicalMetadata() public {
        enable();vm.prank(alice);nft.mintWithKey(1,750000 ether,keccak256(bytes(URI)),alice);
        assertEq(key.balanceOf(CREATOR),750000 ether);assertEq(nft.ownerOf(1),alice);assertEq(nft.tokenURI(1),URI);
    }
    function testDiscountTiers() public view {
        uint256[12] memory counts=[uint256(0),1,4,5,14,15,29,30,49,50,51,100];
        uint256[12] memory prices=[uint256(750000),712500,712500,675000,675000,637500,637500,600000,600000,562500,562500,562500];
        for(uint256 i;i<counts.length;i++)assertEq(nft.directPriceForStake(counts[i]),prices[i]*1 ether);
    }
    function testEIP712StructMatchesViem() public view {
        IslandsLaunch.MintQuote memory q=quote();q.verifierVersion=1;q.metadataHash=bytes32(uint256(0x1212121212121212121212121212121212121212121212121212121212121212));
        assertEq(keccak256(abi.encode(nft.QUOTE_TYPEHASH(),q)),0x470b84afacb328be86f0a5fdf0737b5bb0b622a4901e0f75c5affe03fbe5e3c5);
    }
    function testFuzzCanonicalSlotsDoNotCollide(uint64 island) public view {
        vm.assume(island>0);
        assertEq(nft.editionTokenId(island,true),nft.editionTokenId(island,false)+1);
        assertEq(nft.editionTokenId(uint256(island)+1,false),nft.editionTokenId(island,true)+1);
    }
    function testFuzzMaximumDiscount(uint256 count) public view {
        uint256 price=nft.directPriceForStake(count);assertGe(price,562500 ether);assertLe(price,750000 ether);
    }
    function testSignedDiscountPaysExactlyAndDeliversNFT() public {
        enable();IslandsLaunch.MintQuote memory q=quote();mint(q,sign(q),562500 ether);
        assertEq(nft.ownerOf(1),bob);assertEq(key.balanceOf(CREATOR),562500 ether);
        assertEq(key.balanceOf(alice),437500 ether);assertEq(nft.quoteNonces(alice),1);
        assertEq(key.allowance(alice,address(nft)),187500 ether);
    }
    function testSelfReportedStakeIsRejected() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);q.stakedKeys=500;
        vm.expectRevert("Invalid staking proof");mint(q,sig,562500 ether);assertEq(key.balanceOf(CREATOR),0);
    }
    function testQuoteBindsRecipientTokenAndPrice() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        q.recipient=alice;vm.expectRevert("Invalid staking proof");mint(q,sig,562500 ether);
        q.recipient=bob;q.tokenId=2;vm.expectRevert("Invalid staking proof");mint(q,sig,562500 ether);
        q.tokenId=1;vm.expectRevert("Discount price changed");mint(q,sig,562500 ether-1);
        assertEq(key.balanceOf(CREATOR),0);
    }
    function testReplayAndBuyerCancellation() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        vm.prank(alice);nft.invalidateMyQuotes();vm.expectRevert("Quote nonce changed");mint(q,sig,562500 ether);
        q.nonce=1;sig=sign(q);mint(q,sig,562500 ether);
        vm.expectRevert("Quote nonce changed");mint(q,sig,562500 ether);
    }
    function testExpiredFutureAndOversizedValidityRejected() public {
        enable();IslandsLaunch.MintQuote memory q=quote();q.deadline=999;
        bytes memory sig=sign(q);vm.expectRevert("Expired or invalid quote");mint(q,sig,562500 ether);
        q=quote();q.issuedAt=1001;sig=sign(q);vm.expectRevert("Expired or invalid quote");mint(q,sig,562500 ether);
        q=quote();q.deadline=1601;sig=sign(q);vm.expectRevert("Expired or invalid quote");mint(q,sig,562500 ether);
    }
    function testStaleOrFutureStakeSnapshotRejected() public {
        enable();IslandsLaunch.MintQuote memory q=quote();q.stakeBlock=699;
        bytes memory sig=sign(q);vm.expectRevert("Invalid stake snapshot");mint(q,sig,562500 ether);
        q.stakeBlock=1001;sig=sign(q);vm.expectRevert("Invalid stake snapshot");mint(q,sig,562500 ether);
    }
    function testVerifierRotationAndDisableInvalidateQuote() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        vm.prank(CREATOR);nft.setDiscountVerifier(vm.addr(SIGNER_KEY));
        vm.expectRevert("Discount verifier unavailable");mint(q,sig,562500 ether);
        q=quote();sig=sign(q);vm.prank(CREATOR);nft.setDiscountVerifier(address(0));
        vm.expectRevert("Discount verifier unavailable");mint(q,sig,562500 ether);
    }
    function testQuoteCannotBeUsedOnDifferentContractOrChain() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        IslandsLaunch other=new IslandsLaunch();assertTrue(other.quoteDigest(q)!=nft.quoteDigest(q));
        vm.chainId(84532);vm.expectRevert("Invalid staking proof");mint(q,sig,562500 ether);
    }
    function testReceiverFailureRollsBackPaymentNonceAndOffer() public {
        enable();IslandsLaunch.MintQuote memory q=quote();q.recipient=address(new MintRejectingReceiver());
        bytes memory sig=sign(q);vm.expectRevert();mint(q,sig,562500 ether);
        assertEq(key.balanceOf(CREATOR),0);assertEq(nft.quoteNonces(alice),0);
        (uint256 price,)=nft.mintOffers(1);assertEq(price,750000 ether);
    }
    function testPauseStopsDiscountPayment() public {
        enable();IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        vm.prank(CREATOR);nft.setKeyMintEnabled(false);vm.expectRevert("KEY mint disabled");mint(q,sig,562500 ether);
    }
    function testTaxedTokenCannotUnderpayCreator() public {
        enable();MintFeeKey template=new MintFeeKey();vm.etch(KEY,address(template).code);
        IslandsLaunch.MintQuote memory q=quote();bytes memory sig=sign(q);
        vm.expectRevert("Incomplete mint payout");mint(q,sig,562500 ether);
        assertEq(nft.quoteNonces(alice),0);assertEq(key.balanceOf(CREATOR),0);
    }
}
