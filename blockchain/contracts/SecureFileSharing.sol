// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SecureFileSharing
 * @dev Main contract for logging file operations on blockchain
 */
contract SecureFileSharing {
    
    // Structs
    struct FileRecord {
        bytes32 fileHash;
        address owner;
        uint256 uploadTime;
        string fileName;
        uint256 fileSize;
        string encryptionAlgorithm;
        bool isEncrypted;
        uint256 accessCount;
    }
    
    struct AccessLog {
        bytes32 fileHash;
        address accessor;
        uint256 timestamp;
        string action; // "upload", "download", "share", "delete"
        bool success;
    }
    
    struct ShareRecord {
        bytes32 fileHash;
        address owner;
        address recipient;
        uint256 sharedAt;
        uint256 expiresAt;
        bool oneTimeAccess;
        bool accessed;
    }
    
    // State Variables
    mapping(bytes32 => FileRecord) public files;
    mapping(address => bytes32[]) public userFiles;
    mapping(bytes32 => AccessLog[]) public accessLogs;
    mapping(bytes32 => ShareRecord[]) public shareRecords;
    
    uint256 public totalFiles;
    uint256 public totalAccesses;
    
    // Events
    event FileUploaded(
        bytes32 indexed fileHash,
        address indexed owner,
        string fileName,
        uint256 fileSize,
        uint256 timestamp
    );
    
    event FileAccessed(
        bytes32 indexed fileHash,
        address indexed accessor,
        string action,
        uint256 timestamp
    );
    
    event FileShared(
        bytes32 indexed fileHash,
        address indexed owner,
        address indexed recipient,
        uint256 expiresAt
    );
    
    event FileDeleted(
        bytes32 indexed fileHash,
        address indexed owner,
        uint256 timestamp
    );
    
    event AccessRevoked(
        bytes32 indexed fileHash,
        address indexed recipient,
        uint256 timestamp
    );
    
    // Modifiers
    modifier fileExists(bytes32 fileHash) {
        require(files[fileHash].owner != address(0), "File does not exist");
        _;
    }
    
    modifier onlyFileOwner(bytes32 fileHash) {
        require(files[fileHash].owner == msg.sender, "Only file owner can perform this action");
        _;
    }
    
    // Core Functions
    
    /**
     * @dev Log file upload
     * @param fileHash Hash of the file
     * @param fileName Name of the file
     * @param fileSize Size of the file
     * @param encryptionAlgorithm Encryption algorithm used
     * @param isEncrypted Whether file is encrypted
     */
    function logFileUpload(
        bytes32 fileHash,
        string memory fileName,
        uint256 fileSize,
        string memory encryptionAlgorithm,
        bool isEncrypted
    ) public {
        require(files[fileHash].owner == address(0), "File already exists");
        require(fileSize > 0, "File size must be greater than 0");
        
        FileRecord memory newFile = FileRecord({
            fileHash: fileHash,
            owner: msg.sender,
            uploadTime: block.timestamp,
            fileName: fileName,
            fileSize: fileSize,
            encryptionAlgorithm: encryptionAlgorithm,
            isEncrypted: isEncrypted,
            accessCount: 0
        });
        
        files[fileHash] = newFile;
        userFiles[msg.sender].push(fileHash);
        totalFiles++;
        
        // Log access
        logAccess(fileHash, "upload", true);
        
        emit FileUploaded(fileHash, msg.sender, fileName, fileSize, block.timestamp);
    }
    
    /**
     * @dev Log file access (download, view, etc.)
     * @param fileHash Hash of the file
     * @param action Type of access action
     * @param success Whether the action was successful
     */
    function logAccess(
        bytes32 fileHash,
        string memory action,
        bool success
    ) public fileExists(fileHash) {
        AccessLog memory log = AccessLog({
            fileHash: fileHash,
            accessor: msg.sender,
            timestamp: block.timestamp,
            action: action,
            success: success
        });
        
        accessLogs[fileHash].push(log);
        
        if (success) {
            files[fileHash].accessCount++;
            totalAccesses++;
        }
        
        emit FileAccessed(fileHash, msg.sender, action, block.timestamp);
    }
    
    /**
     * @dev Share file with another user
     * @param fileHash Hash of the file
     * @param recipient Address of the recipient
     * @param expiresAt Timestamp when access expires (0 for no expiry)
     * @param oneTimeAccess Whether access is limited to one use
     */
    function shareFile(
        bytes32 fileHash,
        address recipient,
        uint256 expiresAt,
        bool oneTimeAccess
    ) public fileExists(fileHash) onlyFileOwner(fileHash) {
        require(recipient != address(0), "Invalid recipient address");
        require(recipient != msg.sender, "Cannot share with yourself");
        
        ShareRecord memory share = ShareRecord({
            fileHash: fileHash,
            owner: msg.sender,
            recipient: recipient,
            sharedAt: block.timestamp,
            expiresAt: expiresAt,
            oneTimeAccess: oneTimeAccess,
            accessed: false
        });
        
        shareRecords[fileHash].push(share);
        
        emit FileShared(fileHash, msg.sender, recipient, expiresAt);
    }
    
    /**
     * @dev Delete file from blockchain record
     * @param fileHash Hash of the file
     */
    function deleteFile(bytes32 fileHash) public fileExists(fileHash) onlyFileOwner(fileHash) {
        delete files[fileHash];
        emit FileDeleted(fileHash, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Revoke access to shared file
     * @param fileHash Hash of the file
     * @param recipient Address of the recipient whose access is revoked
     */
    function revokeAccess(
        bytes32 fileHash,
        address recipient
    ) public fileExists(fileHash) onlyFileOwner(fileHash) {
        ShareRecord[] storage shares = shareRecords[fileHash];
        for (uint i = 0; i < shares.length; i++) {
            if (shares[i].recipient == recipient) {
                shares[i].expiresAt = block.timestamp; // Immediately expire
                emit AccessRevoked(fileHash, recipient, block.timestamp);
                break;
            }
        }
    }
    
    // Query Functions
    
    /**
     * @dev Get file details
     * @param fileHash Hash of the file
     */
    function getFileDetails(bytes32 fileHash) 
        public 
        view 
        fileExists(fileHash) 
        returns (FileRecord memory) 
    {
        return files[fileHash];
    }
    
    /**
     * @dev Get access logs for a file
     * @param fileHash Hash of the file
     */
    function getAccessLogs(bytes32 fileHash) 
        public 
        view 
        returns (AccessLog[] memory) 
    {
        return accessLogs[fileHash];
    }
    
    /**
     * @dev Get number of access logs for a file
     * @param fileHash Hash of the file
     */
    function getAccessLogCount(bytes32 fileHash) 
        public 
        view 
        returns (uint256) 
    {
        return accessLogs[fileHash].length;
    }
    
    /**
     * @dev Get share records for a file
     * @param fileHash Hash of the file
     */
    function getShareRecords(bytes32 fileHash) 
        public 
        view 
        returns (ShareRecord[] memory) 
    {
        return shareRecords[fileHash];
    }
    
    /**
     * @dev Get all files owned by user
     * @param owner Address of the file owner
     */
    function getUserFiles(address owner) 
        public 
        view 
        returns (bytes32[] memory) 
    {
        return userFiles[owner];
    }
    
    /**
     * @dev Get number of files owned by user
     * @param owner Address of the file owner
     */
    function getUserFileCount(address owner) 
        public 
        view 
        returns (uint256) 
    {
        return userFiles[owner].length;
    }
    
    /**
     * @dev Check if file exists
     * @param fileHash Hash of the file
     */
    function fileExists_(bytes32 fileHash) public view returns (bool) {
        return files[fileHash].owner != address(0);
    }
    
    /**
     * @dev Get contract statistics
     */
    function getStats() public view returns (uint256, uint256) {
        return (totalFiles, totalAccesses);
    }
}
