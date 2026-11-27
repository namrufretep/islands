// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IslandsCore} from "./IslandsCore.sol";
import {IslandsFees} from "./IslandsFees.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {SignatureChecker} from "@openzeppelin/contracts/utils/cryptography/SignatureChecker.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

/// @notice Base launch candidate: canonical editions and authenticated direct-mint discounts.
/// @dev Not a blind/regional mint. Discount assertions trust the owner-appointed verifier.
contract IslandsLaunch is IslandsCore, EIP712 {
    uint256 public constant CHAIN_ID = 8453;
    uint256 public constant DIRECT_PRICE = 750000 ether;
    uint256 public constant MAX_QUOTE_AGE = 600;
    bytes32 public constant QUOTE_TYPEHASH = keccak256("MintQuote(address payer,address recipient,uint256 tokenId,uint256 basePrice,uint256 stakedKeys,uint256 stakeBlock,uint256 issuedAt,uint256 deadline,uint256 nonce,uint256 verifierVersion,bytes32 metadataHash)");

    struct Edition { bytes32 metadataHash; bytes32 imageSha256; }
    struct MintQuote {
        address payer;
        address recipient;
        uint256 tokenId;
        uint256 basePrice;
        uint256 stakedKeys;
        uint256 stakeBlock;
        uint256 issuedAt;
        uint256 deadline;
        uint256 nonce;
        uint256 verifierVersion;
        bytes32 metadataHash;
    }
    mapping(uint256 => Edition) public editions;
    mapping(address => uint256) public quoteNonces;
    address public discountVerifier;
    uint256 public verifierVersion;
    event EditionRegistered(uint256 indexed tokenId,uint256 indexed islandId,bool southUp,string metadataURI,bytes32 imageSha256);
    event DiscountVerifierChanged(address indexed verifier,uint256 version);
    event StakingDiscountApplied(address indexed payer,uint256 indexed tokenId,uint256 stakedKeys,uint256 stakeBlock,uint256 price);

    constructor() IslandsCore(IslandsFees.KEY,IslandsFees.CREATOR,IslandsFees.MINT_PROCEEDS_RECIPIENT,"ISLANDS","ISLANDS") EIP712("ISLANDS Mint","1") {
        require(block.chainid == CHAIN_ID,"Base mainnet only");
    }

    /// @notice North-Up = 2*islandId-1; South-Up = 2*islandId. No launch supply cap.
    function editionTokenId(uint256 islandId,bool southUp) public pure returns(uint256) {
        require(islandId != 0 && islandId <= type(uint256).max / 2,"Invalid geographic ID");
        return islandId * 2 - (southUp ? 0 : 1);
    }
    function editionMetadataURI(uint256 islandId,bool southUp) public pure returns(string memory) {
        require(islandId != 0,"Invalid geographic ID");
        string memory id=Strings.toString(islandId);
        while(bytes(id).length<6) id=string.concat("0",id);
        return string.concat("https://islands-kappa.vercel.app/nft/",id,southUp ? "-S.json" : "-N.json");
    }
    /// @notice Permanently binds a canonical slot; registering does not release or mint it.
    function registerEdition(uint256 islandId,bool southUp,string calldata uri,bytes32 imageSha256) external onlyOwner {
        uint256 tokenId=editionTokenId(islandId,southUp);
        require(bytes(uri).length != 0 && imageSha256 != bytes32(0),"Invalid edition metadata");
        require(keccak256(bytes(uri)) == keccak256(bytes(editionMetadataURI(islandId,southUp))),"Wrong canonical metadata URI");
        require(editions[tokenId].metadataHash == bytes32(0),"Edition already registered");
        editions[tokenId]=Edition(keccak256(bytes(uri)),imageSha256);
        emit EditionRegistered(tokenId,islandId,southUp,uri,imageSha256);
    }
    function _validateEdition(uint256 tokenId,string memory uri) internal view override {
        bytes32 registered=editions[tokenId].metadataHash;
        require(registered != bytes32(0) && registered == keccak256(bytes(uri)),"Unregistered or changed edition");
    }
    function _validateMintPrice(uint256 price) internal pure override {
        require(price == DIRECT_PRICE,"Direct price must be 750000 KEY");
    }
    /// @notice Zero disables discounts; changing verifier also invalidates all outstanding quotes.
    function setDiscountVerifier(address verifier) external onlyOwner {
        discountVerifier=verifier;
        verifierVersion++;
        emit DiscountVerifierChanged(verifier,verifierVersion);
    }
    function directPriceForStake(uint256 verifiedStakedKeys) public pure returns(uint256) {
        return DIRECT_PRICE * (10000 - IslandsFees.discountBps(verifiedStakedKeys)) / 10000;
    }
    function quoteDigest(MintQuote calldata quote) public view returns(bytes32) {
        // The struct contains only static ABI types, in QUOTE_TYPEHASH field order.
        return _hashTypedDataV4(keccak256(abi.encode(QUOTE_TYPEHASH,quote)));
    }
    function invalidateMyQuotes() external { quoteNonces[msg.sender]++; }

    /// @notice A short-lived, buyer-bound verifier signature is required for a discount.
    /// @dev The signing service must independently verify the designated creator's staked keys.
    /// Holding liquid keys, a UI slider or self-reported counts are not eligibility proofs.
    function mintWithStakingQuote(MintQuote calldata quote,bytes calldata signature,uint256 expectedPrice) external nonReentrant {
        require(keyMintEnabled,"KEY mint disabled");
        require(quote.payer == msg.sender && quote.recipient != address(0) && msg.sender != MINT_PROCEEDS_RECIPIENT,"Invalid recipient or payer");
        require(discountVerifier != address(0) && quote.verifierVersion == verifierVersion,"Discount verifier unavailable");
        require(quote.issuedAt <= block.timestamp && quote.deadline >= block.timestamp && quote.deadline > quote.issuedAt && quote.deadline - quote.issuedAt <= MAX_QUOTE_AGE,"Expired or invalid quote");
        require(quote.stakeBlock != 0 && quote.stakeBlock <= block.number && block.number - quote.stakeBlock <= 300,"Invalid stake snapshot");
        require(quote.nonce == quoteNonces[msg.sender],"Quote nonce changed");
        require(SignatureChecker.isValidSignatureNow(discountVerifier,quoteDigest(quote),signature),"Invalid staking proof");
        MintOffer memory offer=mintOffers[quote.tokenId];
        require(offer.price != 0 && _ownerOf(quote.tokenId) == address(0),"Edition unavailable");
        require(offer.price == DIRECT_PRICE && quote.basePrice == offer.price && quote.metadataHash == keccak256(bytes(offer.metadataURI)),"Mint offer changed");
        uint256 price=directPriceForStake(quote.stakedKeys);
        require(price == expectedPrice,"Discount price changed");
        quoteNonces[msg.sender]++;
        _settleMint(quote.tokenId,quote.recipient,offer.metadataURI,price);
        emit StakingDiscountApplied(msg.sender,quote.tokenId,quote.stakedKeys,quote.stakeBlock,price);
    }
}
