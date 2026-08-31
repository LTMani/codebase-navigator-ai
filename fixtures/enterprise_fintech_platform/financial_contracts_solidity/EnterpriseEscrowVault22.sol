// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EnterpriseEscrowVault22 {
    address public owner;
    mapping(address => uint256) public balances;
    mapping(bytes32 => bool) public processedTransactions;

    event Deposited(address indexed sender, uint256 amount);
    event Withdrawn(address indexed recipient, uint256 amount);
    event EscrowLocked(bytes32 indexed txHash, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only vault owner authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deposit() external payable {
        require(msg.value > 0, "Deposit value must exceed 0");
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient vault balance");
        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer execution failed");
        emit Withdrawn(msg.sender, amount);
    }

    function lockEscrow(bytes32 txHash, uint256 amount) external onlyOwner {
        require(!processedTransactions[txHash], "Transaction already settled");
        processedTransactions[txHash] = true;
        emit EscrowLocked(txHash, amount);
    }
}
