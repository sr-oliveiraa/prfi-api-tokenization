const { ethers } = require("hardhat");
require("dotenv").config();

async function main() {
  console.log("🚀 Iniciando deploy do PRFI Protocol na BNB Testnet...");
  console.log("=" * 60);

  // Verificar configurações
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Rede: ${network.name} (Chain ID: ${network.chainId})`);
  
  if (network.chainId !== 97n && network.chainId !== 97) {
    console.log(`⚠️  Chain ID detectado: ${network.chainId} (esperado: 97)`);
    console.log("Continuando com o deploy...");
  }

  // Obter deployer
  const [deployer] = await ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  
  // Verificar saldo
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`💰 Saldo: ${ethers.formatEther(balance)} BNB`);
  
  if (balance < ethers.parseEther("0.1")) {
    console.log("⚠️  Saldo baixo! Obtenha BNB testnet em: https://testnet.binance.org/faucet-smart");
  }

  console.log("\n🔨 Compilando contratos...");
  
  // Deploy do contrato PRFIC
  console.log("\n📦 Fazendo deploy do contrato PRFIC...");
  
  const PRFIC = await ethers.getContractFactory("PRFIC");
  
  // Usar gas limit fixo para contratos complexos
  const gasLimit = 3000000; // 3M gas - suficiente para contratos ERC20 complexos
  
  console.log(`⛽ Gas limit: ${gasLimit}`);
  
  // Deploy com configurações otimizadas para testnet
  const prfic = await PRFIC.deploy({
    gasLimit: gasLimit,
    gasPrice: ethers.parseUnits("10", "gwei") // 10 gwei para testnet
  });
  
  console.log(`📤 Transação de deploy enviada: ${prfic.deploymentTransaction().hash}`);
  console.log("⏳ Aguardando confirmação...");
  
  await prfic.waitForDeployment();
  const contractAddress = await prfic.getAddress();
  
  console.log(`✅ Contrato PRFIC deployado em: ${contractAddress}`);
  
  // Verificar deploy
  console.log("\n🔍 Verificando deploy...");
  
  const name = await prfic.name();
  const symbol = await prfic.symbol();
  const totalSupply = await prfic.totalSupply();
  const maxSupply = await prfic.MAX_SUPPLY();
  const premineAmount = await prfic.PREMINE_AMOUNT();
  
  console.log(`📋 Nome: ${name}`);
  console.log(`🏷️  Símbolo: ${symbol}`);
  console.log(`📊 Supply Total: ${ethers.formatEther(totalSupply)} PRFIC`);
  console.log(`📈 Supply Máximo: ${ethers.formatEther(maxSupply)} PRFIC`);
  console.log(`🏦 Pre-mine: ${ethers.formatEther(premineAmount)} PRFIC`);
  
  // Verificar treasury
  const treasury = await prfic.treasury();
  const treasuryBalance = await prfic.balanceOf(treasury);
  console.log(`🏛️  Treasury: ${treasury}`);
  console.log(`💎 Saldo Treasury: ${ethers.formatEther(treasuryBalance)} PRFIC`);
  
  // Salvar informações do deploy
  const deployInfo = {
    network: "BSC Testnet",
    chainId: network.chainId.toString(),
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    transactionHash: prfic.deploymentTransaction().hash,
    blockNumber: prfic.deploymentTransaction().blockNumber?.toString(),
    gasUsed: gasLimit.toString(),
    timestamp: new Date().toISOString(),
    contractInfo: {
      name: name,
      symbol: symbol,
      totalSupply: ethers.formatEther(totalSupply),
      maxSupply: ethers.formatEther(maxSupply),
      premineAmount: ethers.formatEther(premineAmount),
      treasury: treasury,
      treasuryBalance: ethers.formatEther(treasuryBalance)
    }
  };
  
  // Salvar em arquivo
  const fs = require("fs");
  const path = require("path");
  
  const deploysDir = path.join(__dirname, "..", "deploys");
  if (!fs.existsSync(deploysDir)) {
    fs.mkdirSync(deploysDir, { recursive: true });
  }
  
  const deployFile = path.join(deploysDir, "bsc-testnet.json");
  fs.writeFileSync(deployFile, JSON.stringify(deployInfo, null, 2));
  
  console.log(`💾 Informações salvas em: ${deployFile}`);
  
  // Instruções finais
  console.log("\n" + "=" * 60);
  console.log("🎉 DEPLOY CONCLUÍDO COM SUCESSO!");
  console.log("=" * 60);
  console.log(`📍 Endereço do Contrato: ${contractAddress}`);
  console.log(`🔗 BscScan Testnet: https://testnet.bscscan.com/address/${contractAddress}`);
  console.log(`🏛️  Treasury: ${treasury}`);
  console.log(`💰 Pre-mine: ${ethers.formatEther(premineAmount)} PRFIC`);
  
  console.log("\n📋 Próximos passos:");
  console.log("1. Verificar contrato no BscScan Testnet");
  console.log("2. Testar registro de empresa");
  console.log("3. Testar mineração de tokens");
  console.log("4. Validar funcionamento completo");
  
  console.log("\n🧪 Para testar:");
  console.log(`node scripts/test-contract.js ${contractAddress}`);
  
  return {
    contractAddress,
    deployInfo
  };
}

// Executar deploy
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error("❌ Erro no deploy:", error);
      process.exit(1);
    });
}

module.exports = main;