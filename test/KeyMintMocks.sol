// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IERC721Receiver} from "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import {Islands} from "../contracts/Islands.sol";

// Local tests only. Never deploy these unrestricted test currencies as real KEY.
contract MintTestKey is ERC20 {
    constructor() ERC20("Test KEY","TESTKEY") {}
    function mint(address to,uint256 value) external { _mint(to,value); }
}
contract MintFalseKey is MintTestKey {
    function transferFrom(address,address,uint256) public pure override returns(bool) { return false; }
}
contract MintFeeKey is MintTestKey {
    function _update(address from,address to,uint256 value) internal override {
        if(from != address(0) && to != address(0)) {
            uint256 fee=value/100;
            super._update(from,address(0),fee);
            super._update(from,to,value-fee);
        } else super._update(from,to,value);
    }
}
contract MintSenderFeeKey is MintTestKey {
    function _update(address from,address to,uint256 value) internal override {
        super._update(from,to,value);
        if(from != address(0) && to != address(0)) super._update(from,address(0),value/100);
    }
}
contract MintRejectingReceiver { }
contract MintReenteringReceiver is IERC721Receiver {
    Islands public immutable collection;
    uint256 public immutable otherId;
    uint256 public immutable otherPrice;
    bytes32 public immutable otherMetadataHash;
    bool public nestedMintSucceeded;
    constructor(Islands nft,uint256 id,uint256 price,bytes32 metadataHash) {
        collection=nft;otherId=id;otherPrice=price;otherMetadataHash=metadataHash;
    }
    function onERC721Received(address,address,uint256,bytes calldata) external returns(bytes4) {
        (nestedMintSucceeded,)=address(collection).call(abi.encodeCall(collection.mintWithKey,(otherId,otherPrice,otherMetadataHash,address(this))));
        return IERC721Receiver.onERC721Received.selector;
    }
}
