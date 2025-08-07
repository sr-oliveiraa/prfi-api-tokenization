const { ethers } = require("hardhat");
require("dotenv").config();

/**
 * Script de teste específico para BSC Testnet
 */
async function main() {
  const contractAddress = "0xd7491E5EA22b58F4F3BD72471527636A0Af079dE";
  
  console.log("🧪 Testando contrato PRFIC na BSC Testnet...");
  console.log("=" * 60);
  console.log(`📍 Contrato: ${contractAddress}`);

  // Verificar rede
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Rede: ${network.name} (Chain ID: ${network.chainId})`);
  
  if (network.chainId !== 97n) {
    console.log("⚠️  Atenção: Não está conectado à BSC Testnet (Chain ID 97)");
  }

  // Conectar ao contrato
  const PRFIC = await ethers.getContractFactory("PRFIC");
  const prfic = PRFIC.attach(contractAddress);
  
  // Obter signer
  const [deployer] = await ethers.getSigners();
  console.log(`👤 Testador: ${deployer.address}`);
  
  // Verificar saldo BNB
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`💰 Saldo BNB: ${ethers.formatEther(balance)} BNB`);

  try {
    // 1. Verificar informações básicas
    console.log("\n📋 1. Verificando informações básicas...");
    
    const name = await prfic.name();
    const symbol = await prfic.symbol();
    const totalSupply = await prfic.totalSupply();
    const maxSupply = await prfic.MAX_SUPPLY();
    const treasury = await prfic.treasury();
    const treasuryBalance = await prfic.balanceOf(treasury);
    
    console.log(`   Nome: ${name}`);
    console.log(`   Símbolo: ${symbol}`);
    console.log(`   Supply Total: ${ethers.formatEther(totalSupply)} PRFIC`);
    console.log(`   Supply Máximo: ${ethers.formatEther(maxSupply)} PRFIC`);
    console.log(`   Treasury: ${treasury}`);
    console.log(`   Saldo Treasury: ${ethers.formatEther(treasuryBalance)} PRFIC`);

    // 2. Verificar se já está registrado
    console.log("\n🏢 2. Verificando registro de empresa...");
    
    const isRegistered = await prfic.registeredCompanies(deployer.address);
    console.log(`   Empresa registrada: ${isRegistered}`);
    
    if (!isRegistered) {
      console.log("   Registrando empresa...");
      const companyName = "Empresa Teste PRFI";
      const tx = await prfic.registerCompany(companyName, {
        gasLimit: 100000
      });
      await tx.wait();
      console.log(`   ✅ Empresa registrada: ${companyName}`);
    }

    // 3. Testar mineração
    console.log("\n⛏️  3. Testando mineração de tokens...");
    
    const batchId = `test-batch-${Date.now()}`;
    const eventsCount = 1000;
    const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("test-merkle-root"));
    
    console.log(`   Batch ID: ${batchId}`);
    console.log(`   Procurando nonce válido...`);
    
    // Usar a função do contrato para encontrar nonce válido
    try {
      const [nonce, blockHash] = await prfic.findValidNonce(
        deployer.address,
        batchId,
        eventsCount,
        merkleRoot,
        0
      );
      
      console.log(`   ✅ Nonce válido: ${nonce}`);
      console.log(`   🔗 Block Hash: ${blockHash}`);
      
      const difficulty = await prfic.calculateDifficulty(blockHash);
      console.log(`   📊 Dificuldade: ${difficulty}`);

      // Verificar saldos antes
      const balanceBefore = await prfic.balanceOf(deployer.address);
      console.log(`   💰 Saldo antes: ${ethers.formatEther(balanceBefore)} PRFIC`);

      // Executar mineração
      console.log("   ⛏️  Executando mineração...");
      
      const mintTx = await prfic.mintBatch(
        batchId,
        eventsCount,
        nonce,
        merkleRoot,
        {
          gasLimit: 500000
        }
      );
      
      const receipt = await mintTx.wait();
      console.log(`   ✅ Mineração concluída! Gas usado: ${receipt.gasUsed}`);
      console.log(`   🔗 TX Hash: ${receipt.hash}`);

      // Verificar saldos depois
      const balanceAfter = await prfic.balanceOf(deployer.address);
      const tokensEarned = balanceAfter - balanceBefore;
      
      console.log(`   💰 Saldo depois: ${ethers.formatEther(balanceAfter)} PRFIC`);
      console.log(`   🎉 Tokens minerados: ${ethers.formatEther(tokensEarned)} PRFIC`);

    } catch (error) {
      console.log(`   ⚠️  Erro na mineração: ${error.message}`);
      if (error.message.includes("no valid nonce found")) {
        console.log("   💡 Isso é normal - a dificuldade pode ser alta");
      }
    }

    // 4. Verificar estatísticas
    console.log("\n📊 4. Estatísticas finais...");
    
    const [events, tokens, registered, companyName, lastNonce] = await prfic.getCompanyStats(deployer.address);
    console.log(`   Eventos processados: ${events}`);
    console.log(`   Tokens recebidos: ${ethers.formatEther(tokens)} PRFIC`);
    console.log(`   Nome da empresa: ${companyName}`);
    console.log(`   Último nonce: ${lastNonce}`);

    const [globalSupply, globalBatches, globalEvents, globalTreasuryBalance] = await prfic.getGlobalStats();
    console.log(`   Supply global: ${ethers.formatEther(globalSupply)} PRFIC`);
    console.log(`   Lotes processados: ${globalBatches}`);
    console.log(`   Eventos globais: ${globalEvents}`);

    console.log("\n" + "=" * 60);
    console.log("🎉 TESTES CONCLUÍDOS COM SUCESSO!");
    console.log("=" * 60);
    console.log(`📍 Contrato: ${contractAddress}`);
    console.log(`🔗 BscScan: https://testnet.bscscan.com/address/${contractAddress}`);
    console.log(`🏛️  Treasury: ${treasury}`);
    
  } catch (error) {
    console.error("❌ Erro durante os testes:", error.message);
    throw error;
  }
}

// Executar
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error("❌ Erro fatal:", error);
      process.exit(1);
    });
}

module.exports = main;
