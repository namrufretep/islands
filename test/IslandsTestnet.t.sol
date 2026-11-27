// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Test} from "forge-std/Test.sol";
import {IslandsTestSuite,IslandsTestKey,IslandsTestCollection} from "../contracts/IslandsTestnet.sol";
import {Islands} from "../contracts/Islands.sol";
contract IslandsTestnetTest is Test {
    address buyer = address(0xB0B);
    string uri = "https://islands-kappa.vercel.app/testnet/edition.json";
    function makeSuite() internal returns(IslandsTestSuite suite) { vm.chainId(84532);vm.prank(buyer);suite = new IslandsTestSuite(); }
    function testTestSuiteIsSeparatedAndReady() public {
        IslandsTestSuite suite = makeSuite();
        IslandsTestCollection nft = suite.collection();
        IslandsTestKey key = suite.key();
        assertEq(nft.owner(),buyer);
        assertEq(key.balanceOf(buyer),1000000 ether);
        assertEq(nft.KEY(),address(key));
        assertEq(nft.MINT_PROCEEDS_RECIPIENT(),address(suite.treasury()));
        assertTrue(nft.keyMintEnabled());
        assertEq(nft.name(),"ISLANDS TEST ONLY");
        assertTrue(address(key) != (new Islands()).KEY());
    }
    function testFullTestMintPaysTreasuryAndCreatesOnlyTestToken() public {
        IslandsTestSuite suite = makeSuite();
        IslandsTestCollection nft = suite.collection();
        IslandsTestKey key = suite.key();
        vm.startPrank(buyer);
        key.approve(address(nft),750000 ether);
        nft.mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        vm.stopPrank();
        assertEq(nft.ownerOf(1),buyer);
        assertEq(nft.tokenURI(1),uri);
        assertEq(key.balanceOf(buyer),250000 ether);
        assertEq(key.balanceOf(address(suite.treasury())),750000 ether);
        vm.startPrank(buyer);
        key.approve(address(nft),750000 ether);
        vm.expectRevert("Edition unavailable");
        nft.mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        vm.stopPrank();
    }
    function testNoAllowanceCannotMintOrPay() public {
        IslandsTestSuite suite = makeSuite();
        IslandsTestCollection nft = suite.collection();
        IslandsTestKey key = suite.key();
        vm.prank(buyer);vm.expectRevert();
        nft.mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        assertEq(key.balanceOf(buyer),1000000 ether);
        assertEq(key.balanceOf(address(suite.treasury())),0);
    }
    function testWrongMetadataRollsBack() public {
        IslandsTestSuite suite = makeSuite();
        IslandsTestCollection nft = suite.collection();
        IslandsTestKey key = suite.key();
        vm.startPrank(buyer);
        key.approve(address(nft),750000 ether);
        vm.expectRevert("Mint offer changed");
        nft.mintWithKey(1,750000 ether,bytes32(0),buyer);
        vm.stopPrank();
        assertEq(key.balanceOf(buyer),1000000 ether);
    }
    function testSuiteRejectsMainnetAndOtherTestnets() public {
        vm.chainId(8453);vm.expectRevert("Base Sepolia only");new IslandsTestSuite();
        vm.chainId(11155111);vm.expectRevert("Base Sepolia only");new IslandsTestSuite();
    }
}
