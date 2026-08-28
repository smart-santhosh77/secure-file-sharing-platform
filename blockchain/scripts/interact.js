const SecureFileSharing = artifacts.require("SecureFileSharing");

module.exports = async function (callback) {
  try {
    const instance = await SecureFileSharing.deployed();
    
    // Get accounts
    const accounts = await web3.eth.getAccounts();
    const owner = accounts[0];
    const user1 = accounts[1];
    
    console.log("\n=== Secure File Sharing Contract Interaction ===");
    console.log(`Owner: ${owner}`);
    console.log(`User 1: ${user1}`);
    
    // Create a file hash
    const fileHash = web3.utils.keccak256("test-file-content");
    console.log(`\nFile Hash: ${fileHash}`);
    
    // Log file upload
    console.log("\nLogging file upload...");
    await instance.logFileUpload(
      fileHash,
      "test-document.pdf",
      1024000,
      "AES-256-GCM",
      true,
      { from: owner }
    );
    console.log("✓ File upload logged");
    
    // Get file details
    console.log("\nRetrieving file details...");
    const fileDetails = await instance.getFileDetails(fileHash);
    console.log("File Details:", {
      owner: fileDetails.owner,
      fileName: fileDetails.fileName,
      fileSize: fileDetails.fileSize.toString(),
      encrypted: fileDetails.isEncrypted,
      accessCount: fileDetails.accessCount.toString()
    });
    
    // Log access
    console.log("\nLogging file access...");
    await instance.logAccess(fileHash, "download", true, { from: user1 });
    console.log("✓ File access logged");
    
    // Share file
    console.log("\nSharing file with user...");
    const expiresAt = Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60); // 7 days
    await instance.shareFile(fileHash, user1, expiresAt, false, { from: owner });
    console.log("✓ File shared");
    
    // Get share records
    console.log("\nRetrieving share records...");
    const shareRecords = await instance.getShareRecords(fileHash);
    console.log(`Share Records: ${shareRecords.length}`);
    
    // Get stats
    console.log("\nContract Statistics:");
    const stats = await instance.getStats();
    console.log(`Total Files: ${stats[0]}`);
    console.log(`Total Accesses: ${stats[1]}`);
    
    console.log("\n=== Interaction Complete ===");
    callback();
  } catch (error) {
    console.error(error);
    callback(error);
  }
};
