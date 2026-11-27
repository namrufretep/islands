// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC2981} from "@openzeppelin/contracts/token/common/ERC2981.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @notice Shared mint implementation; deployment wrappers fix network-specific settings.
abstract contract IslandsCore is ERC721, ERC2981, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    address public immutable CREATOR;
    address public immutable MINT_PROCEEDS_RECIPIENT;
    address public immutable KEY;
    uint96 public constant CREATOR_FEE_BPS = 1000;
    string internal collectionMetadataURI = "https://islands-kappa.vercel.app/nft/collection.json";
    event ContractURIUpdated();
    event KeyMintEnabled(bool enabled);
    event MintOfferUpdated(uint256 indexed tokenId,uint256 price,bytes32 metadataHash);
    event MintedWithKey(uint256 indexed tokenId,address indexed payer,address indexed recipient,uint256 price,address payout);
    struct MintOffer { uint256 price; string metadataURI; }
    // Prices are in KEY base units. Never trust client-supplied staking counts.
    mapping(uint256 => MintOffer) public mintOffers;
    bool public keyMintEnabled;
    mapping(uint256 => string) private metadata;
    constructor(address key,address creator,address payout,string memory name_,string memory symbol_) ERC721(name_, symbol_) Ownable(creator) {
        require(key != address(0) && creator != address(0) && payout != address(0), "Invalid configuration");
        KEY = key;
        CREATOR = creator;
        MINT_PROCEEDS_RECIPIENT = payout;
        _setDefaultRoyalty(creator, CREATOR_FEE_BPS);
    }
    function contractURI() external view returns (string memory) {
        return collectionMetadataURI;
    }
    function setContractURI(string calldata uri) external onlyOwner {
        require(bytes(uri).length != 0, "Empty collection URI");
        collectionMetadataURI = uri;
        emit ContractURIUpdated();
    }
    function setKeyMintEnabled(bool enabled) external onlyOwner {
        keyMintEnabled = enabled;
        emit KeyMintEnabled(enabled);
    }
    function setMintOffer(uint256 tokenId,string calldata uri,uint256 price) external onlyOwner {
        _validateEdition(tokenId,uri);
        _validateMintPrice(price);
        require(tokenId != 0 && bytes(uri).length != 0 && price != 0,"Invalid mint offer");
        require(_ownerOf(tokenId) == address(0),"Already minted");
        mintOffers[tokenId] = MintOffer(price,uri);
        emit MintOfferUpdated(tokenId,price,keccak256(bytes(uri)));
    }
    function cancelMintOffer(uint256 tokenId) external onlyOwner {
        delete mintOffers[tokenId];
        emit MintOfferUpdated(tokenId,0,bytes32(0));
    }
    /// @notice One explicitly released edition. Payment and NFT delivery are atomic.
    /// @param expectedPrice Exact displayed price in KEY base units.
    /// @param expectedMetadataHash keccak256 of the displayed metadata URI.
    function mintWithKey(uint256 tokenId,uint256 expectedPrice,bytes32 expectedMetadataHash,address recipient) external nonReentrant {
        require(keyMintEnabled,"KEY mint disabled");
        require(recipient != address(0) && msg.sender != MINT_PROCEEDS_RECIPIENT,"Invalid recipient or payer");
        MintOffer memory offer = mintOffers[tokenId];
        require(offer.price != 0 && _ownerOf(tokenId) == address(0),"Edition unavailable");
        require(offer.price == expectedPrice && keccak256(bytes(offer.metadataURI)) == expectedMetadataHash,"Mint offer changed");
        _settleMint(tokenId,recipient,offer.metadataURI,offer.price);
    }
    /// @dev Additional mint routes share the exact same atomic settlement.
    function _settleMint(uint256 tokenId,address recipient,string memory uri,uint256 price) internal {
        delete mintOffers[tokenId];
        IERC20 key = IERC20(KEY);
        uint256 payoutBefore = key.balanceOf(MINT_PROCEEDS_RECIPIENT);
        uint256 payerBefore = key.balanceOf(msg.sender);
        key.safeTransferFrom(msg.sender,MINT_PROCEEDS_RECIPIENT,price);
        // Reject transfer fees or unexpected debits; the creator receives the full price.
        require(key.balanceOf(MINT_PROCEEDS_RECIPIENT) == payoutBefore + price,"Incomplete mint payout");
        require(key.balanceOf(msg.sender) + price == payerBefore,"Unexpected mint debit");
        metadata[tokenId] = uri;
        _safeMint(recipient,tokenId);
        emit MintedWithKey(tokenId,msg.sender,recipient,price,MINT_PROCEEDS_RECIPIENT);
    }
    function issue(address recipient, uint256 islandId, string calldata uri) external onlyOwner nonReentrant {
        require(islandId != 0 && bytes(uri).length != 0, "Invalid island");
        _validateEdition(islandId,uri);
        delete mintOffers[islandId];
        metadata[islandId] = uri;
        _safeMint(recipient, islandId);
    }
    function _validateEdition(uint256,string memory) internal view virtual {}
    function _validateMintPrice(uint256) internal pure virtual {}
    function tokenURI(uint256 islandId) public view override returns (string memory) {
        _requireOwned(islandId);
        return metadata[islandId];
    }
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
