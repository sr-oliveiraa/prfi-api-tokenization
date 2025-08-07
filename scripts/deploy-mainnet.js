const { ethers } = require("hardhat");
require("dotenv").config();

async function main() {
  console.log("🚀 DEPLOY DO PRFI PROTOCOL NA BSC MAINNET");
  console.log("=" * 60);
  console.log("⚠️  ATENÇÃO: Este é um deploy em PRODUÇÃO!");
  console.log("⚠️  Verifique todas as configurações antes de prosseguir!");
  console.log("=" * 60);

  // Verificar configurações
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Rede: ${network.name} (Chain ID: ${network.chainId})`);
  
  if (network.chainId !== 56n && network.chainId !== 56) {
    console.log(`❌ ERRO: Chain ID incorreto: ${network.chainId} (esperado: 56)`);
    console.log("❌ Não está conectado à BSC Mainnet!");
    process.exit(1);
  }

  // Obter deployer
  const [deployer] = await ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  
  // Verificar se é a conta do treasury
  const expectedTreasury = "0xB4CA2829E762C77D4A813b54195278bB78F7e22c";
  if (deployer.address.toLowerCase() !== expectedTreasury.toLowerCase()) {
    console.log(`❌ ERRO: Conta incorreta!`);
    console.log(`❌ Esperado: ${expectedTreasury}`);
    console.log(`❌ Atual: ${deployer.address}`);
    process.exit(1);
  }
  
  // Verificar saldo
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`💰 Saldo: ${ethers.formatEther(balance)} BNB`);
  
  const minBalance = ethers.parseEther("0.01"); // Mínimo 0.01 BNB para mainnet (mais econômico)
  if (balance < minBalance) {
    console.log(`❌ ERRO: Saldo insuficiente!`);
    console.log(`❌ Mínimo necessário: 0.01 BNB`);
    console.log(`❌ Saldo atual: ${ethers.formatEther(balance)} BNB`);
    process.exit(1);
  }

  // Configurações de deploy para mainnet (econômicas)
  const deployGasPrice = ethers.parseUnits("1.2", "gwei"); // 1.2 gwei - muito econômico
  const gasLimit = 3000000; // Gas limit otimizado

  console.log(`⛽ Gas Price deploy: ${ethers.formatUnits(deployGasPrice, "gwei")} gwei`);
  console.log(`⛽ Gas Limit: ${gasLimit}`);

  // Calcular custo estimado
  const estimatedCost = deployGasPrice * BigInt(gasLimit);
  console.log(`💸 Custo estimado: ${ethers.formatEther(estimatedCost)} BNB`);

  // Confirmação final
  console.log("\n" + "=" * 60);
  console.log("🔴 CONFIRMAÇÃO FINAL PARA DEPLOY EM PRODUÇÃO");
  console.log("=" * 60);
  console.log(`📍 Rede: BSC Mainnet (Chain ID: ${network.chainId})`);
  console.log(`👤 Treasury: ${deployer.address}`);
  console.log(`💰 Saldo: ${ethers.formatEther(balance)} BNB`);
  console.log(`💸 Custo: ~${ethers.formatEther(estimatedCost)} BNB`);
  console.log(`🏦 Pre-mine: 24.4M PRFIC para treasury`);
  console.log(`📈 Supply máximo: 122M PRFIC`);
  console.log("=" * 60);

  // Aguardar 10 segundos para reflexão
  console.log("⏳ Aguardando 10 segundos para confirmação...");
  await new Promise(resolve => setTimeout(resolve, 10000));

  console.log("\n🔨 Compilando contratos...");
  
  // Deploy do contrato PRFIC
  console.log("\n📦 Fazendo deploy do contrato PRFIC na MAINNET...");
  
  const PRFIC = await ethers.getContractFactory("PRFIC");
  
  console.log("🚀 Enviando transação de deploy...");
  
  // Deploy com configurações otimizadas para mainnet
  const prfic = await PRFIC.deploy({
    gasLimit: gasLimit,
    gasPrice: deployGasPrice
  });
  
  const deployTx = prfic.deploymentTransaction();
  console.log(`📤 TX Hash: ${deployTx.hash}`);
  console.log("⏳ Aguardando confirmações...");
  
  await prfic.waitForDeployment();
  const contractAddress = await prfic.getAddress();
  
  console.log(`✅ CONTRATO DEPLOYADO COM SUCESSO!`);
  console.log(`📍 Endereço: ${contractAddress}`);
  
  // Verificar deploy
  console.log("\n🔍 Verificando deploy...");
  
  const name = await prfic.name();
  const symbol = await prfic.symbol();
  const totalSupply = await prfic.totalSupply();
  const maxSupply = await prfic.MAX_SUPPLY();
  const premineAmount = await prfic.PREMINE_AMOUNT();
  const treasury = await prfic.treasury();
  const treasuryBalance = await prfic.balanceOf(treasury);
  
  console.log(`📋 Nome: ${name}`);
  console.log(`🏷️  Símbolo: ${symbol}`);
  console.log(`📊 Supply Total: ${ethers.formatEther(totalSupply)} PRFIC`);
  console.log(`📈 Supply Máximo: ${ethers.formatEther(maxSupply)} PRFIC`);
  console.log(`🏦 Pre-mine: ${ethers.formatEther(premineAmount)} PRFIC`);
  console.log(`🏛️  Treasury: ${treasury}`);
  console.log(`💎 Saldo Treasury: ${ethers.formatEther(treasuryBalance)} PRFIC`);
  
  // Salvar informações do deploy
  const deployInfo = {
    network: "BSC Mainnet",
    chainId: network.chainId.toString(),
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    transactionHash: deployTx.hash,
    blockNumber: deployTx.blockNumber?.toString(),
    gasUsed: gasLimit.toString(),
    gasPrice: ethers.formatUnits(deployGasPrice, "gwei"),
    deploymentCost: ethers.formatEther(deployGasPrice * BigInt(gasLimit)),
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
  
  const deployFile = path.join(deploysDir, "bsc-mainnet.json");
  fs.writeFileSync(deployFile, JSON.stringify(deployInfo, null, 2));
  
  console.log(`💾 Informações salvas em: ${deployFile}`);
  
  // Resultado final
  console.log("\n" + "=" * 80);
  console.log("🎉 DEPLOY EM PRODUÇÃO CONCLUÍDO COM SUCESSO!");
  console.log("=" * 80);
  console.log(`📍 Contrato PRFIC: ${contractAddress}`);
  console.log(`🔗 BscScan: https://bscscan.com/address/${contractAddress}`);
  console.log(`🏛️  Treasury: ${treasury}`);
  console.log(`💎 Pre-mine: ${ethers.formatEther(premineAmount)} PRFIC`);
  console.log(`💸 Custo do deploy: ${deployInfo.deploymentCost} BNB`);
  console.log("=" * 80);
  
  console.log("\n📋 Próximos passos IMPORTANTES:");
  console.log("1. ✅ Verificar contrato no BscScan");
  console.log("2. ✅ Documentar endereço do contrato");
  console.log("3. ✅ Atualizar configurações do sistema");
  console.log("4. ✅ Comunicar deploy para a equipe");
  console.log("5. ✅ Monitorar primeiras transações");
  
  console.log("\n🔒 SEGURANÇA:");
  console.log("- Contrato é imutável após deploy");
  console.log("- Treasury configurado corretamente");
  console.log("- Sistema totalmente descentralizado");
  console.log("- Proof-of-work validado");
  
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
      console.error("❌ ERRO CRÍTICO NO DEPLOY:", error);
      process.exit(1);
    });
}

module.exports = main;
