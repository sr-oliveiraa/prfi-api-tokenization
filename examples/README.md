# 📚 PRFI Protocol Examples

This directory contains practical examples showing how to interact with the PRFI Protocol smart contract deployed on BSC Mainnet.

## 🎯 Available Examples

### 1. Contract Interaction (`contract-interaction.js`)
Complete example showing how to:
- Connect to the PRFIC contract
- Register your company
- Mine tokens through proof-of-work
- Check statistics and balances

### 2. Basic Usage (`basic_usage.py`)
Python example for basic API tokenization workflow.

### 3. E-commerce Integration (`ecommerce_integration.py`)
Example showing how to integrate PRFI Protocol with an e-commerce platform.

### 4. Decentralized Usage (`descentralizado_usage.py`)
Advanced example using the decentralized client.

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
npm install ethers dotenv

# Create .env file with your private key
echo "PRIVATE_KEY=your_private_key_here" > .env
```

### Run Contract Interaction Example
```bash
node examples/contract-interaction.js
```

## 📋 Contract Information

### BSC Mainnet
- **Contract**: `0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`
- **Network**: BNB Smart Chain
- **Chain ID**: 56
- **Explorer**: [View on BscScan](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)

### BSC Testnet
- **Contract**: `0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`
- **Network**: BNB Smart Chain Testnet
- **Chain ID**: 97
- **Explorer**: [View on Testnet](https://testnet.bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Faucet**: [Get Test BNB](https://testnet.binance.org/faucet-smart)

## 💰 How Mining Works

1. **Register Company**: One-time registration on the contract
2. **Process Events**: Collect 1,000 API events
3. **Create Batch**: Generate unique batch ID and Merkle root
4. **Mine Nonce**: Find valid proof-of-work nonce (4 leading zeros)
5. **Submit Batch**: Send to contract for validation
6. **Earn Tokens**: Receive 0.8 PRFIC (company) + 0.2 PRFIC (treasury)

## 🔧 Configuration

### Environment Variables
```bash
# Required
PRIVATE_KEY=your_private_key_here

# Optional (defaults to BSC Mainnet)
BSC_RPC_URL=https://bsc-dataseed1.binance.org
CONTRACT_ADDRESS=0xd7491E5EA22b58F4F3BD72471527636A0Af079dE
```

### Gas Costs (BSC Mainnet)
- **Company Registration**: ~0.00012 BNB
- **Token Mining**: ~0.0006 BNB  
- **Token Transfer**: ~0.000025 BNB

## 📊 Example Output

```
📋 Contract Information:
   Address: 0xd7491E5EA22b58F4F3BD72471527636A0Af079dE
   Name: PRFI Coin
   Symbol: PRFIC
   Total Supply: 24400000.0 PRFIC
   Your Address: 0x...
   Your Balance: 0.0 PRFIC

🏢 Registering company: My Company
   ✅ Company registered successfully!

⛏️ Mining tokens for batch: batch-1691234567890
   Events count: 1000
   Merkle root: 0x...
   🔍 Finding valid nonce...
   ✅ Valid nonce found: 12345
   📊 Difficulty: 4
   🔗 Block hash: 0x0000...
   📤 Submitting mined batch...
   ✅ Mining successful! Gas used: 456789
   🔗 Transaction: https://bscscan.com/tx/0x...
   🎉 Tokens earned: 0.8 PRFIC

📊 Company Statistics:
   Events processed: 1000
   Tokens earned: 0.8 PRFIC
   Registered: true
   Company name: My Company
   Last nonce: 12345
```

## 🛡️ Security Notes

- **Never share your private key**
- **Use testnet for development**
- **Verify contract address before transactions**
- **Check gas prices before submitting**
- **Keep your .env file secure**

## 🔗 Useful Links

- **Contract Source**: [PRFIC.sol](../contract/PRFIC.sol)
- **Documentation**: [docs/](../docs/)
- **BscScan**: [Contract Explorer](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **BSC Faucet**: [Get Test BNB](https://testnet.binance.org/faucet-smart)

## 🤝 Support

If you need help with the examples:
1. Check the [documentation](../docs/)
2. Review the [smart contract](../contract/PRFIC.sol)
3. Open an issue on GitHub

---

**Happy Mining!** ⛏️💰
