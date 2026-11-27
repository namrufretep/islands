// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {Test} from "forge-std/Test.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IslandsLaunch} from "../contracts/IslandsLaunch.sol";

/// @notice Executes the actual deployed KEY transfer code on a LOCAL Base fork only.
contract IslandsLaunchForkTest is Test {
    function testRealKEYPaymentOnLocalBaseFork() public {
        string memory url=vm.envOr("ISLANDS_BASE_FORK_URL",string(""));
        if(bytes(url).length==0){vm.skip(true);return;}
        vm.createSelectFork(url);
        assertEq(block.chainid,8453);
        address creator=address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1"));
        IERC20 key=IERC20(address(bytes20(hex"b0ca1e094a1779018b194ac6151ece8d6f05db07")));
        address buyer=address(0xABCD1234);
        IslandsLaunch nft=new IslandsLaunch();
        string memory uri="https://islands-kappa.vercel.app/nft/000001-N.json";
        vm.startPrank(creator);
        nft.registerEdition(1,false,uri,bytes32(uint256(123)));
        nft.setMintOffer(1,uri,750000 ether);nft.setKeyMintEnabled(true);
        vm.stopPrank();
        uint256 beforeBalance=key.balanceOf(creator);
        deal(address(key),buyer,1000000 ether);
        vm.startPrank(buyer);
        key.approve(address(nft),750000 ether);
        nft.mintWithKey(1,750000 ether,keccak256(bytes(uri)),buyer);
        vm.stopPrank();
        assertEq(key.balanceOf(creator)-beforeBalance,750000 ether);
        assertEq(key.balanceOf(buyer),250000 ether);
        assertEq(nft.ownerOf(1),buyer);
        assertEq(nft.tokenURI(1),uri);
    }
}
