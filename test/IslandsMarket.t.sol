// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Test} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Islands} from "../contracts/Islands.sol";
import {IslandsMarket} from "../contracts/IslandsMarket.sol";
contract MockKey is ERC20 {
    constructor() ERC20("Mock KEY","KEY") {}
    function mint(address to,uint256 amount) external { _mint(to,amount); }
}
contract IslandsMarketTest is Test {
    address constant KEY=address(bytes20(hex"b0ca1e094a1779018b194ac6151ece8d6f05db07"));
    address constant CREATOR=address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1"));
    address alice=address(0xA11CE);
    address bob=address(0xB0B);
    Islands nft;
    IslandsMarket market;
    MockKey key;
    function setUp() public {
        MockKey template=new MockKey();
        vm.etch(KEY,address(template).code);
        key=MockKey(KEY);
        nft=new Islands(address(this));
        market=new IslandsMarket(address(nft));
        nft.issue(alice,1,"ipfs://one");
        nft.issue(bob,2,"ipfs://two");
        key.mint(alice,1000000 ether);
        key.mint(bob,2000000 ether);
        vm.startPrank(alice);
        nft.setApprovalForAll(address(market),true);
        key.approve(address(market),type(uint256).max);
        vm.stopPrank();
        vm.startPrank(bob);
        nft.setApprovalForAll(address(market),true);
        key.approve(address(market),type(uint256).max);
        vm.stopPrank();
    }
    function testSaleRoyalty() public {
        vm.prank(alice); market.list(1,500000 ether,block.timestamp+1 days);
        vm.prank(bob); market.buy(1,alice,500000 ether);
        assertEq(nft.ownerOf(1),bob);
        assertEq(key.balanceOf(CREATOR),50000 ether);
        assertEq(key.balanceOf(alice),1450000 ether);
        assertEq(key.balanceOf(bob),1500000 ether);
    }
    function testSwap() public {
        vm.prank(alice); uint256 id=market.offerSwap(bob,1,2,block.timestamp+1 days);
        vm.prank(bob); market.acceptSwap(id);
        assertEq(nft.ownerOf(1),bob);
        assertEq(nft.ownerOf(2),alice);
        assertEq(key.balanceOf(CREATOR),50000 ether);
        assertEq(key.balanceOf(alice),975000 ether);
        assertEq(key.balanceOf(bob),1975000 ether);
    }
    function testSwapRollback() public {
        vm.prank(alice); uint256 id=market.offerSwap(bob,1,2,block.timestamp+1 days);
        vm.prank(bob); nft.setApprovalForAll(address(market),false);
        vm.startPrank(bob);
        vm.expectRevert(); market.acceptSwap(id);
        vm.stopPrank();
        assertEq(nft.ownerOf(1),alice);
        assertEq(nft.ownerOf(2),bob);
        assertEq(key.balanceOf(CREATOR),0);
        assertEq(key.balanceOf(alice),1000000 ether);
        assertEq(key.balanceOf(bob),2000000 ether);
    }
    function testChangedPriceRejected() public {
        vm.prank(alice); market.list(1,500000 ether,block.timestamp+1 days);
        vm.startPrank(bob);
        vm.expectRevert(); market.buy(1,alice,400000 ether);
        vm.stopPrank();
    }
    function testExpiredSaleRejected() public {
        vm.prank(alice); market.list(1,500000 ether,block.timestamp+1 days);
        vm.warp(block.timestamp+2 days);
        vm.startPrank(bob);
        vm.expectRevert(); market.buy(1,alice,500000 ether);
        vm.stopPrank();
    }
}
