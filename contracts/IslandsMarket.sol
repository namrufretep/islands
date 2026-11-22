// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IslandsFees} from "./IslandsFees.sol";

/// @notice Draft KEY-only marketplace. Requires NFT and KEY approvals.
contract IslandsMarket is ReentrancyGuard {
    using SafeERC20 for IERC20;
    IERC721 public immutable collection;
    IERC20 public immutable key;
    uint256 public immutable swapFee;
    struct Sale { address seller; uint256 price; uint256 deadline; }
    struct Swap { address maker; address taker; uint256 offered; uint256 wanted; uint256 deadline; }
    mapping(uint256 => Sale) public sales;
    mapping(uint256 => Swap) public swaps;
    uint256 public nextSwap;
    event Sold(uint256 indexed id,address indexed seller,address indexed buyer,uint256 price,uint256 royalty);
    event Swapped(uint256 indexed offerId,address indexed maker,address indexed taker);
    constructor(address nft) {
        require(nft.code.length > 0,"Invalid NFT");
        collection = IERC721(nft);
        key = IERC20(IslandsFees.KEY);
        uint8 decimals = IERC20Metadata(IslandsFees.KEY).decimals();
        require(decimals <= 30,"Invalid decimals");
        swapFee = IslandsFees.SWAP_KEY_PER_PARTICIPANT * 10 ** uint256(decimals);
    }
    function list(uint256 id,uint256 price,uint256 deadline) external {
        require(collection.ownerOf(id)==msg.sender && price>=10 && deadline>block.timestamp,"Invalid listing");
        sales[id]=Sale(msg.sender,price,deadline);
    }
    function cancelSale(uint256 id) external {
        require(sales[id].seller==msg.sender,"Not seller");
        delete sales[id];
    }
    function buy(uint256 id,address expectedSeller,uint256 expectedPrice) external nonReentrant {
        Sale memory s=sales[id];
        require(s.seller!=address(0) && s.seller==expectedSeller && s.price==expectedPrice && s.deadline>=block.timestamp,"Listing changed");
        require(msg.sender!=s.seller && collection.ownerOf(id)==s.seller,"Invalid owner");
        delete sales[id];
        uint256 fee=IslandsFees.royalty(s.price);
        key.safeTransferFrom(msg.sender,IslandsFees.CREATOR,fee);
        key.safeTransferFrom(msg.sender,s.seller,s.price-fee);
        collection.safeTransferFrom(s.seller,msg.sender,id);
        emit Sold(id,s.seller,msg.sender,s.price,fee);
    }
    function offerSwap(address taker,uint256 offered,uint256 wanted,uint256 deadline) external returns(uint256 id) {
        require(taker!=msg.sender && taker!=address(0) && offered!=wanted && deadline>block.timestamp,"Invalid offer");
        require(collection.ownerOf(offered)==msg.sender && collection.ownerOf(wanted)==taker,"Invalid owners");
        id=++nextSwap;
        swaps[id]=Swap(msg.sender,taker,offered,wanted,deadline);
    }
    function cancelSwap(uint256 id) external {
        require(swaps[id].maker==msg.sender,"Not maker");
        delete swaps[id];
    }
    function acceptSwap(uint256 id) external nonReentrant {
        Swap memory s=swaps[id];
        require(s.taker==msg.sender && s.deadline>=block.timestamp,"Invalid offer");
        require(collection.ownerOf(s.offered)==s.maker && collection.ownerOf(s.wanted)==msg.sender,"Owner changed");
        delete swaps[id];
        delete sales[s.offered];
        delete sales[s.wanted];
        key.safeTransferFrom(s.maker,IslandsFees.CREATOR,swapFee);
        key.safeTransferFrom(msg.sender,IslandsFees.CREATOR,swapFee);
        collection.safeTransferFrom(s.maker,msg.sender,s.offered);
        collection.safeTransferFrom(msg.sender,s.maker,s.wanted);
        emit Swapped(id,s.maker,msg.sender);
    }
}
