const { ethers } = require("hardhat");
require("dotenv").config();

/**
 * Script de teste completo para o contrato PRFIC na BSC Testnet
 * Testa: registro de empresa, mineração de tokens, validação de proof-of-work
 */
async function testContract(contractAddress) {
  console.log("🧪 Iniciando testes do contrato PRFIC...");
  console.log("=" * 60);

  // Conectar ao contrato
  const PRFIC = await ethers.getContractFactory("PRFIC");
  const prfic = PRFIC.attach(contractAddress);
  
  // Obter signers
  const [deployer] = await ethers.getSigners();
  console.log(`👤 Testador: ${deployer.address}`);
  
  // Verificar rede
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Rede: ${network.name} (Chain ID: ${network.chainId})`);

  try {
    // 1. Verificar informações básicas do contrato
    console.log("\n📋 1. Verificando informações básicas...");
    
    const name = await prfic.name();
    const symbol = await prfic.symbol();
    const totalSupply = await prfic.totalSupply();
    const maxSupply = await prfic.MAX_SUPPLY();
    const treasury = await prfic.treasury();
    
    console.log(`   Nome: ${name}`);
    console.log(`   Símbolo: ${symbol}`);
    console.log(`   Supply Total: ${ethers.formatEther(totalSupply)} PRFIC`);
    console.log(`   Supply Máximo: ${ethers.formatEther(maxSupply)} PRFIC`);
    console.log(`   Treasury: ${treasury}`);

    // 2. Testar registro de empresa
    console.log("\n🏢 2. Testando registro de empresa...");
    
    const companyName = "Empresa Teste PRFI";
    const isRegistered = await prfic.registeredCompanies(deployer.address);
    
    if (!isRegistered) {
      console.log("   Registrando empresa...");
      const tx = await prfic.registerCompany(companyName);
      await tx.wait();
      console.log(`   ✅ Empresa registrada: ${companyName}`);
    } else {
      console.log("   ✅ Empresa já registrada");
    }

    // 3. Testar mineração de tokens
    console.log("\n⛏️  3. Testando mineração de tokens...");
    
    const batchId = `test-batch-${Date.now()}`;
    const eventsCount = 1000; // 1000 eventos = 1 PRFIC
    const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("test-merkle-root"));
    
    console.log(`   Batch ID: ${batchId}`);
    console.log(`   Eventos: ${eventsCount}`);
    console.log(`   Merkle Root: ${merkleRoot}`);
    
    // Encontrar nonce válido
    console.log("   🔍 Procurando nonce válido...");
    
    let nonce = 0;
    let blockHash;
    let validNonce = false;
    
    // Tentar encontrar nonce válido (máximo 100.000 tentativas)
    for (let i = 0; i < 100000; i++) {
      blockHash = await prfic.generateBlockHash(
        deployer.address,
        batchId,
        eventsCount,
        i,
        merkleRoot
      );
      
      const isValid = await prfic.isValidProofOfWork(blockHash);
      if (isValid) {
        nonce = i;
        validNonce = true;
        const difficulty = await prfic.calculateDifficulty(blockHash);
        console.log(`   ✅ Nonce válido encontrado: ${nonce}`);
        console.log(`   📊 Dificuldade: ${difficulty}`);
        console.log(`   🔗 Block Hash: ${blockHash}`);
        break;
      }
    }
    
    if (!validNonce) {
      throw new Error("Não foi possível encontrar nonce válido");
    }

    // Verificar saldos antes da mineração
    const balanceBefore = await prfic.balanceOf(deployer.address);
    const treasuryBalanceBefore = await prfic.balanceOf(treasury);
    
    console.log(`   💰 Saldo antes: ${ethers.formatEther(balanceBefore)} PRFIC`);
    console.log(`   🏛️  Treasury antes: ${ethers.formatEther(treasuryBalanceBefore)} PRFIC`);

    // Executar mineração
    console.log("   ⛏️  Executando mineração...");
    
    const mintTx = await prfic.mintBatch(
      batchId,
      eventsCount,
      nonce,
      merkleRoot,
      {
        gasLimit: 500000 // Gas limit alto para mineração
      }
    );
    
    const receipt = await mintTx.wait();
    console.log(`   ✅ Mineração concluída! Gas usado: ${receipt.gasUsed}`);

    // Verificar saldos após mineração
    const balanceAfter = await prfic.balanceOf(deployer.address);
    const treasuryBalanceAfter = await prfic.balanceOf(treasury);
    
    console.log(`   💰 Saldo depois: ${ethers.formatEther(balanceAfter)} PRFIC`);
    console.log(`   🏛️  Treasury depois: ${ethers.formatEther(treasuryBalanceAfter)} PRFIC`);
    
    const tokensEarned = balanceAfter - balanceBefore;
    const treasuryEarned = treasuryBalanceAfter - treasuryBalanceBefore;
    
    console.log(`   🎉 Tokens minerados: ${ethers.formatEther(tokensEarned)} PRFIC`);
    console.log(`   🏦 Treasury recebeu: ${ethers.formatEther(treasuryEarned)} PRFIC`);

    // 4. Verificar estatísticas
    console.log("\n📊 4. Verificando estatísticas...");
    
    const [events, tokens, registered, name_stored, lastNonce] = await prfic.getCompanyStats(deployer.address);
    console.log(`   Eventos processados: ${events}`);
    console.log(`   Tokens recebidos: ${ethers.formatEther(tokens)} PRFIC`);
    console.log(`   Registrada: ${registered}`);
    console.log(`   Nome: ${name_stored}`);
    console.log(`   Último nonce: ${lastNonce}`);

    // 5. Verificar estatísticas globais
    const [globalSupply, globalBatches, globalEvents, globalTreasuryBalance] = await prfic.getGlobalStats();
    console.log(`   Supply global: ${ethers.formatEther(globalSupply)} PRFIC`);
    console.log(`   Lotes processados: ${globalBatches}`);
    console.log(`   Eventos globais: ${globalEvents}`);
    console.log(`   Saldo treasury: ${ethers.formatEther(globalTreasuryBalance)} PRFIC`);

    console.log("\n" + "=" * 60);
    console.log("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!");
    console.log("=" * 60);
    
    return {
      success: true,
      contractAddress,
      tokensEarned: ethers.formatEther(tokensEarned),
      treasuryEarned: ethers.formatEther(treasuryEarned),
      batchId,
      nonce,
      blockHash
    };

  } catch (error) {
    console.error("❌ Erro durante os testes:", error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Executar testes se chamado diretamente
if (require.main === module) {
  const contractAddress = process.argv[2];
  
  if (!contractAddress) {
    console.error("❌ Uso: node scripts/test-contract.js <CONTRACT_ADDRESS>");
    process.exit(1);
  }
  
  testContract(contractAddress)
    .then((result) => {
      if (result.success) {
        console.log("✅ Testes concluídos com sucesso!");
        process.exit(0);
      } else {
        console.error("❌ Testes falharam:", result.error);
        process.exit(1);
      }
    })
    .catch((error) => {
      console.error("❌ Erro fatal:", error);
      process.exit(1);
    });
}

module.exports = testContract;
