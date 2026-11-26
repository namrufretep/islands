// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Test} from "forge-std/Test.sol";
import {Islands} from "../contracts/Islands.sol";
import {MintTestKey,MintFalseKey,MintFeeKey,MintSenderFeeKey,MintRejectingReceiver,MintReenteringReceiver} from "./KeyMintMocks.sol";

contract IslandsMintTest is Test {
    address constant KEY=address(bytes20(hex"b0ca1e094a1779018b194ac6151ece8d6f05db07"));
    address constant CREATOR=address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1"));
    address alice=address(0xA11CE);
    address bob=address(0xB0B);
    uint256 constant PRICE=500000 ether;
    string constant URI="https://islands-kappa.vercel.app/nft/000056-N.json";
    Islands nft;
    MintTestKey key;
    function setUp() public {
        MintTestKey template=new MintTestKey();
        vm.etch(KEY,address(template).code);
        key=MintTestKey(KEY);
        nft=new Islands();
        key.mint(alice,1000000 ether);
        vm.prank(alice);key.approve(address(nft),PRICE);
        vm.prank(CREATOR);nft.setMintOffer(9001,URI,PRICE);
    }
    function enable() internal { vm.prank(CREATOR);nft.setKeyMintEnabled(true); }
    function mint(address recipient) internal {
        vm.prank(alice);nft.mintWithKey(9001,PRICE,keccak256(bytes(URI)),recipient);
    }
    function assertUnpaidAndAvailable() internal view {
        assertEq(key.balanceOf(CREATOR),0);
        assertEq(key.balanceOf(alice),1000000 ether);
        assertEq(key.balanceOf(address(nft)),0);
        assertEq(key.allowance(alice,address(nft)),PRICE);
        (uint256 price,string memory uri)=nft.mintOffers(9001);
        assertEq(price,PRICE);assertEq(uri,URI);
    }
    function testMintStartsDisabled() public {
        vm.expectRevert("KEY mint disabled");mint(alice);
        assertUnpaidAndAvailable();
    }
    function testOnlyOwnerCanReleaseEnableOrCancel() public {
        vm.startPrank(alice);
        vm.expectRevert();nft.setMintOffer(9002,URI,1);
        vm.expectRevert();nft.setKeyMintEnabled(true);
        vm.expectRevert();nft.cancelMintOffer(9001);
        vm.stopPrank();
        assertUnpaidAndAvailable();
    }
    function testFullPriceGoesToCreatorAndNFTToBuyer() public {
        enable();mint(bob);
        assertEq(key.balanceOf(CREATOR),PRICE);
        assertEq(key.balanceOf(alice),500000 ether);
        assertEq(key.balanceOf(address(nft)),0);
        assertEq(key.balanceOf(address(this)),0);
        assertEq(nft.ownerOf(9001),bob);
        assertEq(nft.owner(),CREATOR);
        assertEq(nft.tokenURI(9001),URI);
        (uint256 price,)=nft.mintOffers(9001);assertEq(price,0);
        (address recipient,uint256 fee)=nft.royaltyInfo(9001,PRICE);
        assertEq(recipient,CREATOR);assertEq(fee,PRICE/10);
    }
    function testConfirmedLowerPriceIsEntirelyPaidToCreator() public {
        uint256 approvedPrice=375000 ether;
        vm.prank(CREATOR);nft.setMintOffer(9001,URI,approvedPrice);
        enable();
        vm.prank(alice);nft.mintWithKey(9001,approvedPrice,keccak256(bytes(URI)),alice);
        assertEq(key.balanceOf(CREATOR),approvedPrice);
        assertEq(key.balanceOf(alice),1000000 ether-approvedPrice);
    }
    function testChangedPriceCannotChargeOldQuote() public {
        enable();vm.prank(CREATOR);nft.setMintOffer(9001,URI,PRICE+1);
        vm.expectRevert("Mint offer changed");mint(alice);
        assertEq(key.balanceOf(CREATOR),0);assertEq(key.balanceOf(alice),1000000 ether);
    }
    function testChangedMetadataCannotDeliverDifferentArtwork() public {
        enable();vm.prank(CREATOR);nft.setMintOffer(9001,"ipfs://different",PRICE);
        vm.expectRevert("Mint offer changed");mint(alice);
        assertEq(key.balanceOf(CREATOR),0);assertEq(key.balanceOf(alice),1000000 ether);
    }
    function testPaymentRequiresAllowance() public {
        enable();vm.prank(alice);key.approve(address(nft),0);
        vm.expectRevert();mint(alice);
        assertEq(key.balanceOf(CREATOR),0);
        vm.expectRevert();nft.ownerOf(9001);
        (uint256 price,)=nft.mintOffers(9001);assertEq(price,PRICE);
    }
    function testInsufficientBalanceDoesNotMint() public {
        enable();vm.prank(alice);key.transfer(bob,600000 ether);
        vm.expectRevert();mint(alice);
        assertEq(key.balanceOf(CREATOR),0);
        assertEq(key.balanceOf(alice),400000 ether);
        vm.expectRevert();nft.ownerOf(9001);
    }
    function testReceiverFailureRollsBackPaymentAndAllowance() public {
        enable();MintRejectingReceiver receiver=new MintRejectingReceiver();
        vm.expectRevert();mint(address(receiver));
        assertUnpaidAndAvailable();
        vm.expectRevert();nft.ownerOf(9001);
    }
    function testFalseReturningKEYRollsBack() public {
        MintFalseKey template=new MintFalseKey();vm.etch(KEY,address(template).code);
        enable();vm.expectRevert();mint(alice);assertUnpaidAndAvailable();
    }
    function testUnderpaymentFromTokenFeeRollsBack() public {
        MintFeeKey template=new MintFeeKey();vm.etch(KEY,address(template).code);
        enable();vm.expectRevert("Incomplete mint payout");mint(alice);assertUnpaidAndAvailable();
    }
    function testUnexpectedExtraBuyerDebitRollsBack() public {
        MintSenderFeeKey template=new MintSenderFeeKey();vm.etch(KEY,address(template).code);
        enable();vm.expectRevert("Unexpected mint debit");mint(alice);assertUnpaidAndAvailable();
    }
    function testDuplicateMintCannotChargeAgain() public {
        enable();mint(alice);
        vm.prank(alice);key.approve(address(nft),PRICE);
        vm.expectRevert("Edition unavailable");mint(alice);
        assertEq(key.balanceOf(CREATOR),PRICE);
        assertEq(key.balanceOf(alice),500000 ether);
    }
    function testCancelledOrUnreleasedEditionCannotCharge() public {
        enable();vm.prank(CREATOR);nft.cancelMintOffer(9001);
        vm.expectRevert("Edition unavailable");mint(alice);
        vm.startPrank(alice);
        vm.expectRevert("Edition unavailable");nft.mintWithKey(9002,PRICE,keccak256(bytes(URI)),alice);
        vm.stopPrank();
        assertEq(key.balanceOf(CREATOR),0);
    }
    function testInvalidOffersAndMintedEditionCannotBeReleased() public {
        vm.startPrank(CREATOR);
        vm.expectRevert();nft.setMintOffer(0,URI,PRICE);
        vm.expectRevert();nft.setMintOffer(9002,"",PRICE);
        vm.expectRevert();nft.setMintOffer(9002,URI,0);
        vm.stopPrank();
        enable();mint(alice);
        vm.prank(CREATOR);vm.expectRevert("Already minted");nft.setMintOffer(9001,URI,PRICE);
    }
    function testOwnerIssueRemovesExistingPaidOffer() public {
        vm.prank(CREATOR);nft.issue(bob,9001,URI);
        enable();vm.expectRevert("Edition unavailable");mint(alice);
        assertEq(nft.ownerOf(9001),bob);assertEq(key.balanceOf(CREATOR),0);
    }
    function testCollectionOwnershipTransferDoesNotRedirectProceeds() public {
        vm.prank(CREATOR);nft.transferOwnership(bob);
        vm.prank(bob);nft.setKeyMintEnabled(true);
        mint(alice);
        assertEq(nft.owner(),bob);
        assertEq(key.balanceOf(CREATOR),PRICE);
        assertEq(key.balanceOf(bob),0);
    }
    function testReceiverCannotReenterMint() public {
        vm.prank(CREATOR);nft.setMintOffer(9002,URI,PRICE);
        MintReenteringReceiver receiver=new MintReenteringReceiver(nft,9002,PRICE,keccak256(bytes(URI)));
        key.mint(address(receiver),PRICE);
        vm.prank(address(receiver));key.approve(address(nft),PRICE);
        enable();mint(address(receiver));
        assertFalse(receiver.nestedMintSucceeded());
        assertEq(nft.ownerOf(9001),address(receiver));
        vm.expectRevert();nft.ownerOf(9002);
        assertEq(key.balanceOf(CREATOR),PRICE);
        assertEq(key.balanceOf(address(receiver)),PRICE);
    }
    function testPauseStopsNewPayment() public {
        enable();vm.prank(CREATOR);nft.setKeyMintEnabled(false);
        vm.expectRevert("KEY mint disabled");mint(alice);assertUnpaidAndAvailable();
    }
}
