// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title PRFIC Token
 * @dev Token ERC-20 descentralizado para o protocolo PRFI
 *
 * Características:
 * - Supply máximo de 122.000.000 PRFIC tokens
 * - Pre-mine de 24.400.000 PRFIC (20% do supply) para treasury
 * - 1 PRFIC é gerado a cada 1.000 eventos processados
 * - 80% dos tokens vão para a empresa
 * - 20% dos tokens vão para o desenvolvedor (treasury)
 * - Empresas registradas podem mintar seus próprios tokens
 * - Validação criptográfica de prova de trabalho
 * - Sistema de pausa para emergências
 * - Proteção contra reentrância
 * - Totalmente descentralizado (sem minter central)
 */
contract PRFIC is ERC20, Ownable, Pausable, ReentrancyGuard {

    // Endereços importantes
    address public treasury;         // Endereço do desenvolvedor (20% dos tokens)

    // Configurações de supply
    uint256 public constant MAX_SUPPLY = 122000000 * 10**18;     // 122M tokens máximo
    uint256 public constant PREMINE_AMOUNT = 24400000 * 10**18;  // 24.4M tokens pre-mine (20%)

    // Configurações de distribuição
    uint256 public constant COMPANY_PERCENTAGE = 80;    // 80% para empresa
    uint256 public constant TREASURY_PERCENTAGE = 20;   // 20% para treasury
    uint256 public constant PERCENTAGE_BASE = 100;

    // Configurações de mint
    uint256 public constant EVENTS_PER_TOKEN = 1000;    // 1000 eventos = 1 PRFIC
    uint256 public constant TOKEN_DECIMALS = 18;
    uint256 public constant TOKENS_PER_BATCH = 1 * 10**TOKEN_DECIMALS; // 1 PRFIC por lote
    
    // Estatísticas
    uint256 public totalBatches;     // Total de lotes processados
    uint256 public totalEvents;      // Total de eventos processados
    
    // Mapeamento de lotes processados (evita duplicação)
    mapping(string => bool) public processedBatches;

    // Mapeamento de empresas registradas
    mapping(address => bool) public registeredCompanies;
    mapping(address => uint256) public companyEvents;
    mapping(address => uint256) public companyTokens;
    mapping(address => string) public companyNames;

    // Validação de blocos
    mapping(bytes32 => bool) public validatedBlocks;
    mapping(address => uint256) public companyNonces;

    // Configurações de validação
    uint256 public constant MIN_BLOCK_DIFFICULTY = 4; // Número mínimo de zeros no hash
    uint256 public blockReward = 1 * 10**TOKEN_DECIMALS; // Recompensa por bloco válido

    // Eventos
    event TokensMinted(
        string indexed batchId,
        address indexed company,
        uint256 companyAmount,
        uint256 treasuryAmount,
        uint256 eventsCount,
        bytes32 blockHash
    );

    event CompanyRegistered(address indexed company, string name);
    event TreasuryChanged(address indexed oldTreasury, address indexed newTreasury);
    event BlockValidated(bytes32 indexed blockHash, address indexed company, uint256 difficulty);
    event ProofOfWorkSubmitted(address indexed company, string batchId, bytes32 blockHash);
    
    // Modificadores
    modifier onlyRegisteredCompany() {
        require(registeredCompanies[msg.sender], "PRFIC: company not registered");
        _;
    }

    modifier validAddress(address addr) {
        require(addr != address(0), "PRFIC: invalid address");
        _;
    }

    modifier validBatch(string calldata batchId) {
        require(bytes(batchId).length > 0, "PRFIC: batch ID cannot be empty");
        require(!processedBatches[batchId], "PRFIC: batch already processed");
        _;
    }
    
    /**
     * @dev Constructor - Sistema 100% descentralizado
     * Qualquer empresa pode se auto-registrar e mintar tokens via proof-of-work
     */
    constructor() ERC20("PRFI Coin", "PRFIC") Ownable(0xB4CA2829E762C77D4A813b54195278bB78F7e22c) {
        // Treasury fixo para pre-mine
        treasury = 0xB4CA2829E762C77D4A813b54195278bB78F7e22c;

        // Pre-mine de 24.4M tokens (20% do supply) para o treasury
        _mint(treasury, PREMINE_AMOUNT);

        // Registrar treasury como empresa (para testes e operações)
        registeredCompanies[treasury] = true;
        companyNames[treasury] = "PRFI Treasury";

        emit CompanyRegistered(treasury, "PRFI Treasury");
    }
    
    /**
     * @dev Minta tokens através de prova de trabalho descentralizada
     * @param batchId ID único do lote (evita duplicação)
     * @param eventsCount Número de eventos no lote (deve ser 1000)
     * @param nonce Número usado para gerar prova de trabalho
     * @param merkleRoot Raiz Merkle dos eventos processados
     */
    function mintBatch(
        string calldata batchId,
        uint256 eventsCount,
        uint256 nonce,
        bytes32 merkleRoot
    ) external onlyRegisteredCompany whenNotPaused nonReentrant validBatch(batchId) {
        require(eventsCount == EVENTS_PER_TOKEN, "PRFIC: invalid events count");

        // Gerar hash do bloco para validação
        bytes32 blockHash = generateBlockHash(msg.sender, batchId, eventsCount, nonce, merkleRoot);

        // Validar prova de trabalho
        require(isValidProofOfWork(blockHash), "PRFIC: invalid proof of work");
        require(!validatedBlocks[blockHash], "PRFIC: block already validated");

        // Calcular distribuição
        uint256 companyAmount = (TOKENS_PER_BATCH * COMPANY_PERCENTAGE) / PERCENTAGE_BASE;
        uint256 treasuryAmount = (TOKENS_PER_BATCH * TREASURY_PERCENTAGE) / PERCENTAGE_BASE;
        uint256 totalMintAmount = companyAmount + treasuryAmount;

        // Verificar se não excede o supply máximo
        require(
            totalSupply() + totalMintAmount <= MAX_SUPPLY,
            "PRFIC: minting would exceed max supply"
        );

        // Marcar lote e bloco como processados
        processedBatches[batchId] = true;
        validatedBlocks[blockHash] = true;
        companyNonces[msg.sender] = nonce;

        // Mintar tokens
        _mint(msg.sender, companyAmount);
        _mint(treasury, treasuryAmount);

        // Atualizar estatísticas
        totalBatches++;
        totalEvents += eventsCount;
        companyEvents[msg.sender] += eventsCount;
        companyTokens[msg.sender] += companyAmount;

        // Emitir eventos
        emit TokensMinted(batchId, msg.sender, companyAmount, treasuryAmount, eventsCount, blockHash);
        emit BlockValidated(blockHash, msg.sender, calculateDifficulty(blockHash));
        emit ProofOfWorkSubmitted(msg.sender, batchId, blockHash);
    }
    
    /**
     * @dev Auto-registro descentralizado - qualquer empresa pode se registrar
     * @param name Nome da empresa
     */
    function registerCompany(string calldata name) external {
        require(!registeredCompanies[msg.sender], "PRFIC: company already registered");
        require(bytes(name).length > 0, "PRFIC: company name cannot be empty");

        registeredCompanies[msg.sender] = true;
        companyNames[msg.sender] = name;

        emit CompanyRegistered(msg.sender, name);
    }

    /**
     * @dev Validar proof-of-work
     * @param data Dados para validação
     * @param nonce Nonce proposto
     * @param difficulty Dificuldade mínima
     * @return bool True se válido
     */
    function validateProofOfWork(
        bytes32 data,
        uint256 nonce,
        uint256 difficulty
    ) public pure returns (bool) {
        bytes32 hash = keccak256(abi.encodePacked(data, nonce));

        // Contar zeros à esquerda
        uint256 zeros = 0;
        for (uint256 i = 0; i < 32; i++) {
            uint8 b = uint8(hash[i]);
            if (b == 0) {
                zeros += 2;
            } else if (b < 16) {
                zeros += 1;
                break;
            } else {
                break;
            }
        }

        return zeros >= difficulty;
    }

    /**
     * @dev Auto-registro de empresa (qualquer um pode se registrar)
     * @param name Nome da empresa
     */
    function selfRegisterCompany(string calldata name) external {
        require(!registeredCompanies[msg.sender], "PRFIC: company already registered");
        require(bytes(name).length > 0, "PRFIC: company name cannot be empty");
        require(bytes(name).length <= 100, "PRFIC: company name too long");

        registeredCompanies[msg.sender] = true;
        companyNames[msg.sender] = name;

        emit CompanyRegistered(msg.sender, name);
    }

    /**
     * @dev Gera hash do bloco para validação de prova de trabalho
     * @param company Endereço da empresa
     * @param batchId ID do lote
     * @param eventsCount Número de eventos
     * @param nonce Número usado para mineração
     * @param merkleRoot Raiz Merkle dos eventos
     * @return Hash do bloco
     */
    function generateBlockHash(
        address company,
        string calldata batchId,
        uint256 eventsCount,
        uint256 nonce,
        bytes32 merkleRoot
    ) public view returns (bytes32) {
        return keccak256(abi.encodePacked(
            company,
            batchId,
            eventsCount,
            nonce,
            merkleRoot,
            block.timestamp / 3600 // Hora atual (para evitar replay attacks)
        ));
    }

    /**
     * @dev Valida se o hash atende aos requisitos de prova de trabalho
     * @param blockHash Hash do bloco a ser validado
     * @return true se a prova de trabalho é válida
     */
    function isValidProofOfWork(bytes32 blockHash) public pure returns (bool) {
        // Verificar se o hash tem pelo menos MIN_BLOCK_DIFFICULTY zeros à esquerda
        uint256 difficulty = calculateDifficulty(blockHash);
        return difficulty >= MIN_BLOCK_DIFFICULTY;
    }

    /**
     * @dev Calcula a dificuldade de um hash (número de zeros à esquerda)
     * @param blockHash Hash a ser analisado
     * @return Número de zeros à esquerda
     */
    function calculateDifficulty(bytes32 blockHash) public pure returns (uint256) {
        uint256 difficulty = 0;
        for (uint256 i = 0; i < 32; i++) {
            uint8 byte_value = uint8(blockHash[i]);
            if (byte_value == 0) {
                difficulty += 2;
            } else if (byte_value < 16) {
                difficulty += 1;
                break;
            } else {
                break;
            }
        }
        return difficulty;
    }
    
    /**
     * @dev Altera o endereço do treasury (apenas owner)
     * @param newTreasury Novo endereço do treasury
     */
    function setTreasury(address newTreasury) external onlyOwner validAddress(newTreasury) {
        address oldTreasury = treasury;
        treasury = newTreasury;

        emit TreasuryChanged(oldTreasury, newTreasury);
    }

    /**
     * @dev Atualiza a recompensa por bloco (apenas owner)
     * @param newReward Nova recompensa em tokens
     */
    function setBlockReward(uint256 newReward) external onlyOwner {
        require(newReward > 0, "PRFIC: reward must be greater than zero");
        blockReward = newReward;
    }
    
    /**
     * @dev Pausa o contrato (apenas owner)
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Despausa o contrato (apenas owner)
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Verifica se um lote já foi processado
     * @param batchId ID do lote
     * @return true se já foi processado
     */
    function isBatchProcessed(string calldata batchId) external view returns (bool) {
        return processedBatches[batchId];
    }
    
    /**
     * @dev Obtém estatísticas completas de uma empresa
     * @param company Endereço da empresa
     * @return events Total de eventos processados
     * @return tokens Total de tokens recebidos
     * @return registered Se a empresa está registrada
     * @return name Nome da empresa
     * @return nonce Último nonce usado
     */
    function getCompanyStats(address company) external view returns (
        uint256 events,
        uint256 tokens,
        bool registered,
        string memory name,
        uint256 nonce
    ) {
        return (
            companyEvents[company],
            companyTokens[company],
            registeredCompanies[company],
            companyNames[company],
            companyNonces[company]
        );
    }

    /**
     * @dev Verifica se um bloco foi validado
     * @param blockHash Hash do bloco
     * @return true se o bloco foi validado
     */
    function isBlockValidated(bytes32 blockHash) external view returns (bool) {
        return validatedBlocks[blockHash];
    }

    /**
     * @dev Simula mineração para encontrar nonce válido (view function para testes)
     * @param company Endereço da empresa
     * @param batchId ID do lote
     * @param eventsCount Número de eventos
     * @param merkleRoot Raiz Merkle dos eventos
     * @param startNonce Nonce inicial para busca
     * @return nonce Nonce válido encontrado
     * @return blockHash Hash do bloco válido
     */
    function findValidNonce(
        address company,
        string calldata batchId,
        uint256 eventsCount,
        bytes32 merkleRoot,
        uint256 startNonce
    ) external view returns (uint256 nonce, bytes32 blockHash) {
        for (uint256 i = startNonce; i < startNonce + 1000000; i++) {
            bytes32 hash = generateBlockHash(company, batchId, eventsCount, i, merkleRoot);
            if (isValidProofOfWork(hash)) {
                return (i, hash);
            }
        }
        revert("PRFIC: no valid nonce found in range");
    }
    
    /**
     * @dev Obtém estatísticas gerais do contrato
     * @return _totalSupply Supply total de tokens
     * @return _totalBatches Total de lotes processados
     * @return _totalEvents Total de eventos processados
     * @return _treasuryBalance Saldo do treasury
     */
    function getGlobalStats() external view returns (
        uint256 _totalSupply,
        uint256 _totalBatches,
        uint256 _totalEvents,
        uint256 _treasuryBalance
    ) {
        return (
            totalSupply(),
            totalBatches,
            totalEvents,
            balanceOf(treasury)
        );
    }

    /**
     * @dev Obtém informações sobre o supply do token
     * @return _maxSupply Supply máximo permitido
     * @return _totalSupply Supply atual
     * @return _remainingSupply Supply restante para mint
     * @return _premineAmount Quantidade de pre-mine
     */
    function getSupplyInfo() external view returns (
        uint256 _maxSupply,
        uint256 _totalSupply,
        uint256 _remainingSupply,
        uint256 _premineAmount
    ) {
        uint256 currentSupply = totalSupply();
        return (
            MAX_SUPPLY,
            currentSupply,
            MAX_SUPPLY - currentSupply,
            PREMINE_AMOUNT
        );
    }
    
    /**
     * @dev Override para adicionar verificação de pausa nas transferências
     */
    function _update(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._update(from, to, amount);
    }
    
    /**
     * @dev Função de emergência para retirar ETH acidentalmente enviado
     */
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "PRFIC: no ETH to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "PRFIC: ETH withdrawal failed");
    }
}
