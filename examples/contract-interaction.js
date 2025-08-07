/**
 * PRFI Protocol - Contract Interaction Example
 * 
 * This example shows how to interact with the PRFIC contract
 * deployed on BSC Mainnet to mine tokens through proof-of-work.
 */

const { ethers } = require("ethers");
require("dotenv").config();

// Contract configuration
const CONTRACT_ADDRESS = "0xd7491E5EA22b58F4F3BD72471527636A0Af079dE"; // BSC Mainnet
const BSC_RPC_URL = "https://bsc-dataseed1.binance.org";

// Simplified ABI for main functions
const CONTRACT_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function registerCompany(string calldata name) external",
  "function registeredCompanies(address) view returns (bool)",
  "function mintBatch(string calldata batchId, uint256 eventsCount, uint256 nonce, bytes32 merkleRoot) external",
  "function findValidNonce(address company, string calldata batchId, uint256 eventsCount, bytes32 merkleRoot, uint256 startNonce) view returns (uint256, bytes32)",
  "function getCompanyStats(address company) view returns (uint256, uint256, bool, string, uint256)",
  "function getGlobalStats() view returns (uint256, uint256, uint256, uint256)",
  "function calculateDifficulty(bytes32 blockHash) pure returns (uint256)",
  "function isValidProofOfWork(bytes32 blockHash) pure returns (bool)"
];

class PRFIContract {
  constructor(privateKey, rpcUrl = BSC_RPC_URL) {
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    this.wallet = new ethers.Wallet(privateKey, this.provider);
    this.contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, this.wallet);
  }

  async getContractInfo() {
    console.log("📋 Contract Information:");
    console.log(`   Address: ${CONTRACT_ADDRESS}`);
    console.log(`   Name: ${await this.contract.name()}`);
    console.log(`   Symbol: ${await this.contract.symbol()}`);
    console.log(`   Total Supply: ${ethers.formatEther(await this.contract.totalSupply())} PRFIC`);
    console.log(`   Your Address: ${this.wallet.address}`);
    console.log(`   Your Balance: ${ethers.formatEther(await this.contract.balanceOf(this.wallet.address))} PRFIC`);
  }

  async registerCompany(companyName) {
    console.log(`🏢 Registering company: ${companyName}`);
    
    const isRegistered = await this.contract.registeredCompanies(this.wallet.address);
    if (isRegistered) {
      console.log("   ✅ Company already registered!");
      return true;
    }

    try {
      const tx = await this.contract.registerCompany(companyName, {
        gasLimit: 150000
      });
      await tx.wait();
      console.log("   ✅ Company registered successfully!");
      return true;
    } catch (error) {
      console.error("   ❌ Registration failed:", error.message);
      return false;
    }
  }

  async mineTokens(batchId, eventsData) {
    console.log(`⛏️  Mining tokens for batch: ${batchId}`);
    
    const eventsCount = 1000; // Must be exactly 1000
    const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes(JSON.stringify(eventsData)));
    
    console.log(`   Events count: ${eventsCount}`);
    console.log(`   Merkle root: ${merkleRoot}`);
    
    try {
      // Find valid nonce using contract function
      console.log("   🔍 Finding valid nonce...");
      const [nonce, blockHash] = await this.contract.findValidNonce(
        this.wallet.address,
        batchId,
        eventsCount,
        merkleRoot,
        0
      );
      
      const difficulty = await this.contract.calculateDifficulty(blockHash);
      console.log(`   ✅ Valid nonce found: ${nonce}`);
      console.log(`   📊 Difficulty: ${difficulty}`);
      console.log(`   🔗 Block hash: ${blockHash}`);

      // Get balance before mining
      const balanceBefore = await this.contract.balanceOf(this.wallet.address);

      // Submit the mined batch
      console.log("   📤 Submitting mined batch...");
      const tx = await this.contract.mintBatch(batchId, eventsCount, nonce, merkleRoot, {
        gasLimit: 600000
      });
      
      const receipt = await tx.wait();
      console.log(`   ✅ Mining successful! Gas used: ${receipt.gasUsed}`);
      console.log(`   🔗 Transaction: https://bscscan.com/tx/${receipt.hash}`);

      // Check balance after mining
      const balanceAfter = await this.contract.balanceOf(this.wallet.address);
      const tokensEarned = balanceAfter - balanceBefore;
      
      console.log(`   🎉 Tokens earned: ${ethers.formatEther(tokensEarned)} PRFIC`);
      
      return {
        success: true,
        tokensEarned: ethers.formatEther(tokensEarned),
        transactionHash: receipt.hash,
        nonce,
        blockHash
      };

    } catch (error) {
      console.error("   ❌ Mining failed:", error.message);
      return { success: false, error: error.message };
    }
  }

  async getStats() {
    console.log("📊 Company Statistics:");
    
    const [events, tokens, registered, name, nonce] = await this.contract.getCompanyStats(this.wallet.address);
    console.log(`   Events processed: ${events}`);
    console.log(`   Tokens earned: ${ethers.formatEther(tokens)} PRFIC`);
    console.log(`   Registered: ${registered}`);
    console.log(`   Company name: ${name}`);
    console.log(`   Last nonce: ${nonce}`);

    const [totalSupply, totalBatches, totalEvents, treasuryBalance] = await this.contract.getGlobalStats();
    console.log(`   Global supply: ${ethers.formatEther(totalSupply)} PRFIC`);
    console.log(`   Total batches: ${totalBatches}`);
    console.log(`   Global events: ${totalEvents}`);
  }
}

// Example usage
async function main() {
  // Initialize with your private key
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error("❌ Please set PRIVATE_KEY in .env file");
    return;
  }

  const prfi = new PRFIContract(privateKey);

  try {
    // 1. Show contract info
    await prfi.getContractInfo();

    // 2. Register company (if not already registered)
    await prfi.registerCompany("My Company");

    // 3. Mine tokens from API events
    const batchId = `batch-${Date.now()}`;
    const eventsData = {
      events: Array.from({length: 1000}, (_, i) => ({
        id: i,
        type: "api_call",
        timestamp: Date.now(),
        data: `event-${i}`
      }))
    };

    const result = await prfi.mineTokens(batchId, eventsData);
    
    if (result.success) {
      console.log("🎉 Mining completed successfully!");
    }

    // 4. Check updated stats
    await prfi.getStats();

  } catch (error) {
    console.error("❌ Error:", error.message);
  }
}

// Run example
if (require.main === module) {
  main().catch(console.error);
}

module.exports = PRFIContract;
