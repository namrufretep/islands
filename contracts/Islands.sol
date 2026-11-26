// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC2981} from "@openzeppelin/contracts/token/common/ERC2981.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IslandsFees} from "./IslandsFees.sol";

/// @notice Draft collection foundation. Public paid minting is not enabled.
contract Islands is ERC721, ERC2981, Ownable {
    address public constant CREATOR = IslandsFees.CREATOR;
    // Routing policy for the future paid mint, not an active payment method.
    address public constant MINT_PROCEEDS_RECIPIENT = IslandsFees.MINT_PROCEEDS_RECIPIENT;
    uint96 public constant CREATOR_FEE_BPS = 1000;
    string private collectionMetadataURI = "https://islands-kappa.vercel.app/nft/collection.json";
    event ContractURIUpdated();
    mapping(uint256 => string) private metadata;
    // The deployment sender cannot accidentally become the collection owner.
    constructor() ERC721("ISLANDS", "ISLANDS") Ownable(CREATOR) {
        _setDefaultRoyalty(CREATOR, CREATOR_FEE_BPS);
    }
    function contractURI() external view returns (string memory) {
        return collectionMetadataURI;
    }
    function setContractURI(string calldata uri) external onlyOwner {
        require(bytes(uri).length != 0, "Empty collection URI");
        collectionMetadataURI = uri;
        emit ContractURIUpdated();
    }
    function issue(address recipient, uint256 islandId, string calldata uri) external onlyOwner {
        require(islandId != 0 && bytes(uri).length != 0, "Invalid island");
        metadata[islandId] = uri;
        _safeMint(recipient, islandId);
    }
    function tokenURI(uint256 islandId) public view override returns (string memory) {
        _requireOwned(islandId);
        return metadata[islandId];
    }
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
