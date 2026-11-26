// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Islands} from "../contracts/Islands.sol";
import {IslandsFees} from "../contracts/IslandsFees.sol";
import {Test} from "forge-std/Test.sol";
contract IslandsTest is Test {
    Islands collection;
    address alice = address(0xA11CE);
    function setUp() public { collection = new Islands(address(this)); }
    function testRoyalty() public view {
        (address recipient,uint256 amount)=collection.royaltyInfo(1,500000);
        assertEq(recipient,address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1")));
        assertEq(amount,50000);
    }
    function testIssue() public {
        collection.issue(alice,1,"ipfs://test");
        assertEq(collection.ownerOf(1),alice);
        assertEq(collection.tokenURI(1),"ipfs://test");
        vm.expectRevert();
        collection.issue(alice,1,"ipfs://duplicate");
    }
    function testCollectionMetadata() public {
        assertEq(collection.contractURI(),"https://islands-kappa.vercel.app/nft/collection.json");
        collection.setContractURI("ipfs://collection-metadata");
        assertEq(collection.contractURI(),"ipfs://collection-metadata");
        vm.expectRevert();
        collection.setContractURI("");
        vm.prank(alice);
        vm.expectRevert();
        collection.setContractURI("ipfs://unauthorized");
    }
    function testMarketplaceInterfaces() public view {
        assertTrue(collection.supportsInterface(0x80ac58cd));
        assertTrue(collection.supportsInterface(0x5b5e139f));
        assertTrue(collection.supportsInterface(0x2a55205a));
        assertEq(collection.CREATOR_FEE_BPS(),1000);
    }
    function testUnauthorizedIssue() public {
        vm.prank(alice);
        vm.expectRevert();
        collection.issue(alice,1,"ipfs://test");
    }
    function testPrices() public pure {
        uint256[12] memory keys=[uint256(0),1,4,5,14,15,29,30,49,50,51,100];
        uint256[12] memory prices=[uint256(500000),475000,475000,450000,450000,425000,425000,400000,400000,375000,375000,375000];
        for(uint256 i=0;i<keys.length;i++) assertEq(IslandsFees.mintWholeKey(keys[i]),prices[i]);
        assertEq(IslandsFees.royalty(500000),50000);
    }
}
