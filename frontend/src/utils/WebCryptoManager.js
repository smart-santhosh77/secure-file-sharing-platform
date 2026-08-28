// Web Crypto API utilities for client-side encryption

class WebCryptoManager {
  /**
   * Generate RSA-OAEP keypair
   */
  static async generateRSAKeypair(keySize = 2048) {
    const keyPair = await window.crypto.subtle.generateKey(
      {
        name: 'RSA-OAEP',
        modulusLength: keySize,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: 'SHA-256',
      },
      true, // extractable
      ['encrypt', 'decrypt']
    );

    // Export keys to JWK format
    const publicKey = await window.crypto.subtle.exportKey('jwk', keyPair.publicKey);
    const privateKey = await window.crypto.subtle.exportKey('jwk', keyPair.privateKey);

    return {
      publicKey,
      privateKey,
      keySize,
      algorithm: 'RSA-OAEP',
    };
  }

  /**
   * Generate AES-GCM key
   */
  static async generateAESKey(keyLength = 256) {
    const key = await window.crypto.subtle.generateKey(
      {
        name: 'AES-GCM',
        length: keyLength,
      },
      true, // extractable
      ['encrypt', 'decrypt']
    );

    // Export key to raw format (base64)
    const rawKey = await window.crypto.subtle.exportKey('raw', key);
    const base64Key = btoa(String.fromCharCode.apply(null, new Uint8Array(rawKey)));

    return {
      key,
      rawKey,
      base64Key,
      keyLength,
      algorithm: 'AES-GCM',
    };
  }

  /**
   * Encrypt file using AES-GCM
   */
  static async encryptFileWithAES(file, aesKey, iv = null) {
    // Generate IV if not provided (96 bits for GCM)
    if (!iv) {
      iv = window.crypto.getRandomValues(new Uint8Array(12));
    }

    // Read file content
    const fileBuffer = await file.arrayBuffer();

    // Encrypt
    const encryptedData = await window.crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      aesKey,
      fileBuffer
    );

    return {
      encryptedData,
      iv,
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      algorithm: 'AES-256-GCM',
    };
  }

  /**
   * Decrypt file using AES-GCM
   */
  static async decryptFileWithAES(encryptedData, aesKey, iv) {
    const decryptedData = await window.crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      aesKey,
      encryptedData
    );

    return decryptedData;
  }

  /**
   * Encrypt AES key with RSA public key
   */
  static async encryptAESKeyWithRSA(aesKey, rsaPublicKey) {
    // Import RSA public key
    const importedPublicKey = await window.crypto.subtle.importKey(
      'jwk',
      rsaPublicKey,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256',
      },
      false,
      ['encrypt']
    );

    // Export AES key to raw format
    const rawAESKey = await window.crypto.subtle.exportKey('raw', aesKey);

    // Encrypt AES key
    const encryptedKey = await window.crypto.subtle.encrypt(
      {
        name: 'RSA-OAEP',
      },
      importedPublicKey,
      rawAESKey
    );

    // Convert to base64
    const base64EncryptedKey = btoa(
      String.fromCharCode.apply(null, new Uint8Array(encryptedKey))
    );

    return base64EncryptedKey;
  }

  /**
   * Decrypt AES key with RSA private key
   */
  static async decryptAESKeyWithRSA(encryptedKeyBase64, rsaPrivateKey) {
    // Import RSA private key
    const importedPrivateKey = await window.crypto.subtle.importKey(
      'jwk',
      rsaPrivateKey,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256',
      },
      false,
      ['decrypt']
    );

    // Decode base64 encrypted key
    const encryptedKeyBinary = atob(encryptedKeyBase64);
    const encryptedKey = new Uint8Array(encryptedKeyBinary.length);
    for (let i = 0; i < encryptedKeyBinary.length; i++) {
      encryptedKey[i] = encryptedKeyBinary.charCodeAt(i);
    }

    // Decrypt AES key
    const decryptedKey = await window.crypto.subtle.decrypt(
      {
        name: 'RSA-OAEP',
      },
      importedPrivateKey,
      encryptedKey
    );

    // Import as AES key
    const aesKey = await window.crypto.subtle.importKey(
      'raw',
      decryptedKey,
      {
        name: 'AES-GCM',
        length: 256,
      },
      true,
      ['decrypt']
    );

    return aesKey;
  }

  /**
   * Derive key from password using PBKDF2
   */
  static async deriveKeyFromPassword(password, salt = null, iterations = 100000) {
    // Generate salt if not provided
    if (!salt) {
      salt = window.crypto.getRandomValues(new Uint8Array(16));
    }

    // Encode password
    const encodedPassword = new TextEncoder().encode(password);

    // Import password as key
    const baseKey = await window.crypto.subtle.importKey(
      'raw',
      encodedPassword,
      { name: 'PBKDF2' },
      false,
      ['deriveKey']
    );

    // Derive key
    const derivedKey = await window.crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: iterations,
        hash: 'SHA-256',
      },
      baseKey,
      { name: 'AES-GCM', length: 256 },
      true,
      ['encrypt', 'decrypt']
    );

    return { derivedKey, salt };
  }

  /**
   * Convert ArrayBuffer to Base64
   */
  static arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convert Base64 to ArrayBuffer
   */
  static base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Generate hash of file content (SHA-256)
   */
  static async hashFile(file) {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', buffer);
    return this.arrayBufferToBase64(hashBuffer);
  }
}

export default WebCryptoManager;
