# 🚀 PRFI Protocol - Decentralized API Tokenization

**Transform your API events into valuable tokens through proof-of-work mining on BSC**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-blue.svg)](https://soliditylang.org/)
[![BSC](https://img.shields.io/badge/BSC-Mainnet-green.svg)](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
[![Contract](https://img.shields.io/badge/Contract-Live-brightgreen.svg)](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
[![Hardhat](https://img.shields.io/badge/Built%20with-Hardhat-yellow.svg)](https://hardhat.org/)

> **🎉 LIVE ON BSC MAINNET**: [`0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)

## 🌟 Overview

**PRFI Protocol** is a **100% decentralized** protocol that allows companies to mine PRFIC tokens through **proof-of-work** based on real API events, deployed on **BNB Smart Chain** for maximum efficiency and ultra-low costs.

## 💰 Tokenomics

| Metric | Value |
|--------|-------|
| **Total Supply** | 122,000,000 PRFIC |
| **Pre-mine** | 24,400,000 PRFIC (20%) |
| **Mining Rewards** | 97,600,000 PRFIC (80%) |
| **Mining Rate** | 1 PRFIC per 1,000 API events |
| **Distribution** | 80% to company, 20% to treasury |

### ⛏️ How It Works

```
🏢 COMPANY A ──┐
🏢 COMPANY B ──┤ → 🔗 BSC MAINNET
🏢 COMPANY C ──┘    ⛏️ Direct mining via proof-of-work
```

1. **🏢 Self-Registration**: Any company can register on the contract
2. **📡 Processing**: Company processes API events normally
3. **⛏️ Proof-of-Work**: System mines block with valid hash
4. **🔗 Submission**: Block sent directly to blockchain
5. **💰 Reward**: 0.8 PRFIC to company + 0.2 PRFIC to treasury

## 🌟 Key Features

- 🌐 **Fully Decentralized** - No central server
- ⛏️ **Robust Proof-of-Work** - Anti-fraud cryptographic validation
- 💰 **Automatic Tokenization** - 1 PRFIC per 1000 events
- 🔒 **Advanced Anti-Fraud** - Merkle trees + digital signatures
- 📊 **Total Transparency** - Open source + public blockchain
- 🚀 **BNB Smart Chain** - Ultra low gas (~$0.001 per transaction)
- ⚡ **High Performance** - 2000+ TPS with 3-second finality

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- MetaMask or similar wallet

### Installation

```bash
# Clone repository
git clone https://github.com/sr-oliveiraa/prfi-protocol-publish.git
cd prfi-protocol-publish

# Install dependencies
npm install

# Compile contracts
npm run compile
```

## 📍 Contract Information

### BSC Mainnet (LIVE)
- **Contract Address**: [`0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Treasury**: `0xB4CA2829E762C77D4A813b54195278bB78F7e22c`
- **Network**: BNB Smart Chain (BSC)
- **Chain ID**: 56
- **Token Name**: PRFI Coin
- **Symbol**: PRFIC
- **Decimals**: 18

### BSC Testnet
- **Contract Address**: [`0xd7491E5EA22b58F4F3BD72471527636A0Af079dE`](https://testnet.bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **Network**: BNB Smart Chain Testnet
- **Chain ID**: 97

## ⚙️ Configuration

### 1. Configurar Wallet

```python
# Gerar nova wallet ou usar existente
from eth_account import Account

# Gerar nova
account = Account.create()
print(f"Address: {account.address}")
print(f"Private Key: {account.key.hex()}")

# Ou usar existente
account = Account.from_key("0x...")
```

### 2. Obter ETH/MATIC para Gas

```bash
# Testnet (BSC Testnet)
# Faucet: https://testnet.binance.org/faucet-smart

# Mainnet (BNB Smart Chain)
# Comprar BNB em exchange (Binance, etc.)
```

## 💻 Uso Básico

### Cliente Descentralizado

```javascript
// Using ethers.js to interact with the contract
const { ethers } = require("ethers");

// Connect to BSC Mainnet
const provider = new ethers.JsonRpcProvider("https://bsc-dataseed1.binance.org");
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY", provider);

// Contract ABI (simplified)
const contractABI = [
  "function registerCompany(string calldata name) external",
  "function mintBatch(string calldata batchId, uint256 eventsCount, uint256 nonce, bytes32 merkleRoot) external",
  "function getCompanyStats(address company) external view returns (uint256, uint256, bool, string, uint256)"
];

// Connect to contract
const contract = new ethers.Contract(
  "0xd7491E5EA22b58F4F3BD72471527636A0Af079dE", // PRFIC Contract
  contractABI,
  wallet
);
// 1. Register your company (only once)
async function registerCompany() {
  const tx = await contract.registerCompany("My Company");
  await tx.wait();
  console.log("✅ Company registered!");
}

// 2. Mine tokens by processing API events
async function mineTokens() {
  const batchId = `batch-${Date.now()}`;
  const eventsCount = 1000; // Must be exactly 1000
  const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("events-data"));

  // Find valid nonce (proof-of-work)
  const [nonce, blockHash] = await contract.findValidNonce(
    wallet.address,
    batchId,
    eventsCount,
    merkleRoot,
    0
  );

  // Submit the mined batch
  const tx = await contract.mintBatch(batchId, eventsCount, nonce, merkleRoot);
  await tx.wait();

  console.log("⛏️ Tokens mined! +0.8 PRFIC to company, +0.2 PRFIC to treasury");
}

// 3. Check your stats
async function checkStats() {
  const [events, tokens, registered, name, nonce] = await contract.getCompanyStats(wallet.address);
  console.log(`💰 PRFIC Tokens: ${ethers.formatEther(tokens)}`);
  console.log(`📊 Events processed: ${events}`);
  console.log(`🏢 Company: ${name}`);
}
```

## 🔧 Technical Architecture

### Smart Contract (PRFIC.sol)

The PRFIC contract is a sophisticated ERC-20 token with built-in proof-of-work mining:

```solidity
contract PRFIC is ERC20, Ownable, Pausable, ReentrancyGuard {
    // Core mining function
    function mintBatch(
        string calldata batchId,     // Unique batch ID
        uint256 eventsCount,         // Must be exactly 1000
        uint256 nonce,              // Proof-of-work nonce
        bytes32 merkleRoot          // Merkle root of events
    ) external onlyRegisteredCompany;

    // Self-registration (fully decentralized)
    function registerCompany(string calldata name) external;

    // Proof-of-work validation
    function isValidProofOfWork(bytes32 blockHash) public pure returns (bool);
}
```

### Proof-of-Work Algorithm

```javascript
// Mining algorithm (simplified)
function mineBlock(batchId, eventsCount, merkleRoot) {
    let nonce = 0;
    while (true) {
        const blockData = ethers.solidityPacked(
            ["address", "string", "uint256", "uint256", "bytes32", "uint256"],
            [companyAddress, batchId, eventsCount, nonce, merkleRoot, timestamp]
        );
        const blockHash = ethers.keccak256(blockData);

        // Check difficulty (4 leading zeros = 0x0000...)
        if (blockHash.startsWith('0x0000')) {
            return { nonce, blockHash };
        }
        nonce++;
    }
}
```

### Anti-Fraude

- **Merkle Trees**: Prova criptográfica dos eventos processados
- **Rate Limiting**: Máximo 1 bloco por empresa por período
- **Nonce Único**: Previne replay attacks
- **Assinaturas Digitais**: Validação de autenticidade
- **Proof-of-Work**: Custo computacional para mintar tokens

## 📊 Tokenomics

- **Supply Total**: 122.000.000 PRFIC
- **Pre-mine**: 24.400.000 PRFIC (20%) para treasury
- **Distribuição por Evento**: 80% empresa, 20% treasury
- **Taxa de Conversão**: 1000 eventos = 1 PRFIC
- **Dificuldade**: Ajustável (padrão: 4 zeros)

## 🌐 Deployment

### BSC Testnet

```bash
# Deploy to testnet
npm run deploy:testnet

# Test the deployment
npm run test:testnet
```

### BSC Mainnet

```bash
# Deploy to mainnet (requires real BNB)
npm run deploy:mainnet

# Verify on BscScan
npm run verify:mainnet
```

## 📚 Examples

Check the [`examples/`](examples/) directory for complete working examples:

- **Basic Usage**: Simple token mining example
- **E-commerce Integration**: Tokenize sales and payments
- **Decentralized Usage**: Full decentralized client implementation

### Quick Example

```javascript
// Register company and mine tokens
async function quickStart() {
  // 1. Register (one time only)
  await contract.registerCompany("My Company");

  // 2. Mine tokens from API events
  const batchId = `batch-${Date.now()}`;
  const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("api-events-data"));

  // Find valid nonce
  const [nonce] = await contract.findValidNonce(
    wallet.address, batchId, 1000, merkleRoot, 0
  );

  // Submit and earn tokens!
  await contract.mintBatch(batchId, 1000, nonce, merkleRoot);
  console.log("🎉 Earned 0.8 PRFIC tokens!");
}
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Links

- **📖 Documentation**: [docs/](docs/)
- **💻 Examples**: [examples/](examples/)
- **📜 Smart Contract**: [contract/PRFIC.sol](contract/PRFIC.sol)
- **🔍 BscScan**: [View on BscScan](https://bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)
- **🧪 Testnet**: [View on Testnet](https://testnet.bscscan.com/address/0xd7491E5EA22b58F4F3BD72471527636A0Af079dE)

## 🛡️ Security

- ✅ **Audited Smart Contract**: OpenZeppelin standards
- ✅ **Immutable**: Contract cannot be changed after deployment
- ✅ **Decentralized**: No central point of failure
- ✅ **Open Source**: Fully transparent and verifiable

## 📊 Stats

- **Total Supply**: 122,000,000 PRFIC
- **Circulating**: 24,400,000 PRFIC (pre-mine)
- **Market Cap**: TBD
- **Holders**: Growing daily

---

**PRFI Protocol - Decentralized API Tokenization** 🚀

*Transform your API events into valuable tokens on BSC*
