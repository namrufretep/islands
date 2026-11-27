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
        assertEq(suite.collection().owner(),buyer);
        assertEq(suite.key().balanceOf(buyer),1000000 ether);
        assertEq(suite.collection().KEY(),address(suite.key()));
        assertEq(suite.collection().MINT_PROCEEDS_RECIPIENT(),address(suite.treasury()));
        assertTrue(suite.collection().keyMintEnabled());
        assertEq(suite.collection().name(),"ISLANDS TEST ONLY");
        assertTrue(address(suite.key()) != (new Islands()).KEY());
    }
    function testFullTestMintPaysTreasuryAndCreatesOnlyTestToken() public {
        IslandsTestSuite suite = makeSuite();
        vm.startPrank(buyer);
        suite.key().approve(address(suite.collection()),750000 ether);
        suite.collection().mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        vm.stopPrank();
        assertEq(suite.collection().ownerOf(1),buyer);
        assertEq(suite.collection().tokenURI(1),uri);
        assertEq(suite.key().balanceOf(buyer),250000 ether);
        assertEq(suite.key().balanceOf(address(suite.treasury())),750000 ether);
        vm.startPrank(buyer);
        suite.key().approve(address(suite.collection()),750000 ether);
        vm.expectRevert("Edition unavailable");
        suite.collection().mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        vm.stopPrank();
    }
    function testNoAllowanceCannotMintOrPay() public {
        IslandsTestSuite suite = makeSuite();
        vm.prank(buyer);vm.expectRevert();
        suite.collection().mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        assertEq(suite.key().balanceOf(buyer),1000000 ether);
        assertEq(suite.key().balanceOf(address(suite.treasury())),0);
    }
    function testWrongMetadataRollsBack() public {
        IslandsTestSuite suite = makeSuite();
        vm.startPrank(buyer);
        suite.key().approve(address(suite.collection()),750000 ether);
        vm.expectRevert("Mint offer changed");
        suite.collection().mintWithKey(1,750000 ether,bytes32(0),buyer);
        vm.stopPrank();
        assertEq(suite.key().balanceOf(buyer),1000000 ether);
    }
    function testSuiteRejectsMainnetAndOtherTestnets() public {
        vm.chainId(8453);vm.expectRevert("Base Sepolia only");new IslandsTestSuite();
        vm.chainId(11155111);vm.expectRevert("Base Sepolia only");new IslandsTestSuite();
    }
}
