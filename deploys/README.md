# 🚀 PRFI Protocol Deployments

This directory contains deployment information for the PRFI Protocol smart contracts.

## 📍 Live Deployments

### BSC Mainnet (PRODUCTION)
- **Contract Address**: `0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`
- **Network**: BNB Smart Chain
- **Chain ID**: 56
- **Explorer**: [View on BscScan](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Status**: ✅ LIVE
- **Deployed**: August 7, 2025

### BSC Testnet (TESTING)
- **Contract Address**: `0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`
- **Network**: BNB Smart Chain Testnet
- **Chain ID**: 97
- **Explorer**: [View on Testnet](https://testnet.bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Status**: ✅ LIVE
- **Purpose**: Testing and development

## 📊 Contract Details

### Token Information
- **Name**: PRFI Coin
- **Symbol**: PRFIC
- **Decimals**: 18
- **Total Supply**: 122,000,000 PRFIC
- **Pre-mine**: 24,400,000 PRFIC (20%)

### Treasury Information
- **Treasury Address**: `0xB4CA2829E762C77D4A813b54195278bB78F7e22c`
- **Pre-mine Balance**: 24,400,000 PRFIC
- **Mining Share**: 20% of all mined tokens

### Mining Configuration
- **Events per Token**: 1,000 API events = 1 PRFIC
- **Company Share**: 80% (0.8 PRFIC per batch)
- **Treasury Share**: 20% (0.2 PRFIC per batch)
- **Difficulty**: 4 leading zeros in hash
- **Max Supply**: 122,000,000 PRFIC

## 💰 Deployment Costs

### BSC Mainnet
- **Gas Used**: 3,000,000
- **Gas Price**: 1.2 gwei
- **Total Cost**: 0.0036 BNB (~$2.16 USD)
- **Transaction**: [View on BscScan](https://bscscan.com/tx/0xd6d218d4f105731fe29a4524cad3224a620d6fc18162f6918ddfde69a65becb7)

### BSC Testnet
- **Gas Used**: 3,000,000
- **Gas Price**: 10 gwei
- **Total Cost**: 0.03 BNB (Test BNB)
- **Transaction**: [View on Testnet](https://testnet.bscscan.com/tx/0x36dd94ae2f3f2c64db1878a62b7c81751ae5bfc90bd97fe5394a7427d5a53f85)

## 🔧 Deployment Scripts

### Deploy to Testnet
```bash
npm run deploy:testnet
```

### Deploy to Mainnet
```bash
npm run deploy:mainnet
```

### Test Deployment
```bash
npm run test:testnet  # Test on testnet
npm run test:mainnet  # Test on mainnet
```

## 📁 Files

- `bsc-mainnet.json` - Mainnet deployment information (excluded from git)
- `bsc-testnet.json` - Testnet deployment information (excluded from git)

**Note**: Deployment files contain sensitive information and are excluded from version control for security.

## 🛡️ Security

### Contract Security Features
- ✅ **OpenZeppelin Standards** - Industry-standard security
- ✅ **Reentrancy Protection** - Prevents reentrancy attacks
- ✅ **Pausable** - Emergency stop functionality
- ✅ **Access Control** - Owner-only functions
- ✅ **Input Validation** - Comprehensive parameter checking

### Deployment Security
- ✅ **Immutable Contract** - Cannot be changed after deployment
- ✅ **Verified Source Code** - Publicly auditable on BscScan
- ✅ **Testnet Validation** - Thoroughly tested before mainnet
- ✅ **Gas Optimization** - Minimal deployment costs

## 📈 Usage Statistics

### Mainnet (Live Data)
- **Total Supply**: 24,400,000 PRFIC (pre-mine)
- **Registered Companies**: 1 (Treasury)
- **Batches Processed**: 0
- **Events Processed**: 0
- **Tokens Mined**: 0 PRFIC

*Statistics update as companies start using the protocol*

## 🔗 Quick Links

- **Contract Source**: [PRFIC.sol](../contract/PRFIC.sol)
- **Examples**: [examples/](../examples/)
- **Documentation**: [docs/](../docs/)
- **Mainnet Explorer**: [BscScan](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Testnet Explorer**: [Testnet BscScan](https://testnet.bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)

## 🚀 Getting Started

1. **For Development**: Use BSC Testnet
   - Get test BNB from [faucet](https://testnet.binance.org/faucet-smart)
   - Use testnet contract address
   - Test all functionality before mainnet

2. **For Production**: Use BSC Mainnet
   - Ensure you have real BNB for gas
   - Use mainnet contract address
   - Start with small batches

## 📞 Support

If you encounter issues with deployments:
1. Check the [documentation](../docs/)
2. Review deployment scripts in [scripts/](../scripts/)
3. Open an issue on GitHub

---

**PRFI Protocol - Deployed and Ready!** 🎉
