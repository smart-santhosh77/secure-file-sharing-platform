// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AccessControl
 * @dev Manages fine-grained access control for files
 */
contract AccessControl {
    
    // Structs
    struct Permission {
        address user;
        uint256 grantedAt;
        uint256 expiresAt;
        string[] permissions; // "read", "download", "share", etc.
        bool active;
    }
    
    // State Variables
    mapping(bytes32 => mapping(address => Permission)) public filePermissions;
    mapping(address => bytes32[]) public userPermissions;
    
    // Events
    event PermissionGranted(
        bytes32 indexed fileHash,
        address indexed user,
        string[] permissions,
        uint256 expiresAt
    );
    
    event PermissionRevoked(
        bytes32 indexed fileHash,
        address indexed user,
        uint256 timestamp
    );
    
    event PermissionUpdated(
        bytes32 indexed fileHash,
        address indexed user,
        string[] newPermissions
    );
    
    // Modifiers
    modifier hasPermission(bytes32 fileHash, address user, string memory permission) {
        Permission memory perm = filePermissions[fileHash][user];
        require(perm.active, "Permission not found or revoked");
        require(block.timestamp < perm.expiresAt || perm.expiresAt == 0, "Permission expired");
        
        bool hasPerms = false;
        for (uint i = 0; i < perm.permissions.length; i++) {
            if (keccak256(bytes(perm.permissions[i])) == keccak256(bytes(permission))) {
                hasPerms = true;
                break;
            }
        }
        require(hasPerms, "User does not have required permission");
        _;
    }
    
    // Functions
    
    /**
     * @dev Grant permissions to a user for a file
     * @param fileHash Hash of the file
     * @param user Address of the user
     * @param permissions Array of permission strings
     * @param expiresAt Timestamp when permissions expire (0 for no expiry)
     */
    function grantPermission(
        bytes32 fileHash,
        address user,
        string[] memory permissions,
        uint256 expiresAt
    ) public {
        require(user != address(0), "Invalid user address");
        require(permissions.length > 0, "Must grant at least one permission");
        
        Permission memory newPerm = Permission({
            user: user,
            grantedAt: block.timestamp,
            expiresAt: expiresAt,
            permissions: permissions,
            active: true
        });
        
        filePermissions[fileHash][user] = newPerm;
        userPermissions[user].push(fileHash);
        
        emit PermissionGranted(fileHash, user, permissions, expiresAt);
    }
    
    /**
     * @dev Revoke permissions from a user
     * @param fileHash Hash of the file
     * @param user Address of the user
     */
    function revokePermission(bytes32 fileHash, address user) public {
        filePermissions[fileHash][user].active = false;
        emit PermissionRevoked(fileHash, user, block.timestamp);
    }
    
    /**
     * @dev Update permissions for a user
     * @param fileHash Hash of the file
     * @param user Address of the user
     * @param newPermissions New array of permission strings
     */
    function updatePermission(
        bytes32 fileHash,
        address user,
        string[] memory newPermissions
    ) public {
        require(filePermissions[fileHash][user].active, "Permission not found");
        filePermissions[fileHash][user].permissions = newPermissions;
        emit PermissionUpdated(fileHash, user, newPermissions);
    }
    
    /**
     * @dev Check if user has specific permission
     * @param fileHash Hash of the file
     * @param user Address of the user
     * @param permission Permission to check
     */
    function hasUserPermission(
        bytes32 fileHash,
        address user,
        string memory permission
    ) public view returns (bool) {
        Permission memory perm = filePermissions[fileHash][user];
        
        if (!perm.active) return false;
        if (block.timestamp > perm.expiresAt && perm.expiresAt != 0) return false;
        
        for (uint i = 0; i < perm.permissions.length; i++) {
            if (keccak256(bytes(perm.permissions[i])) == keccak256(bytes(permission))) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * @dev Get user permissions for a file
     * @param fileHash Hash of the file
     * @param user Address of the user
     */
    function getUserPermissions(
        bytes32 fileHash,
        address user
    ) public view returns (Permission memory) {
        return filePermissions[fileHash][user];
    }
    
    /**
     * @dev Get all files user has permissions for
     * @param user Address of the user
     */
    function getUserPermissionedFiles(address user) 
        public 
        view 
        returns (bytes32[] memory) 
    {
        return userPermissions[user];
    }
}
