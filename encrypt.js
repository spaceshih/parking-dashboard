const fs = require('fs');

// 與HTML中相同的加密金鑰和函數
const ENCRYPTION_KEY = 'PARKING_DASHBOARD_2024_SECURE_KEY_V1';

function encryptDecrypt(text, key) {
    let result = '';
    for (let i = 0; i < text.length; i++) {
        const keyChar = key.charCodeAt(i % key.length);
        const textChar = text.charCodeAt(i);
        result += String.fromCharCode(textChar ^ keyChar);
    }
    return result;
}

function encryptData(plaintext) {
    const encrypted = encryptDecrypt(plaintext, ENCRYPTION_KEY);
    return Buffer.from(encrypted).toString('base64');
}

function decryptData(ciphertext) {
    try {
        const encrypted = Buffer.from(ciphertext, 'base64').toString();
        return encryptDecrypt(encrypted, ENCRYPTION_KEY);
    } catch (error) {
        throw new Error('解密失敗');
    }
}

// 讀取並加密建物.csv
try {
    console.log('正在讀取建物.csv...');
    const csvContent = fs.readFileSync('建物.csv', 'utf8');
    console.log(`原始檔案大小: ${csvContent.length} 字元`);
    
    console.log('正在加密...');
    const encryptedContent = encryptData(csvContent);
    console.log(`加密後大小: ${encryptedContent.length} 字元`);
    
    console.log('正在寫入建物.encrypted...');
    fs.writeFileSync('建物.encrypted', encryptedContent);
    
    console.log('✅ 加密完成！');
    
    // 驗證解密
    console.log('正在驗證解密...');
    const testDecrypted = decryptData(encryptedContent);
    const isValid = testDecrypted === csvContent;
    console.log(`解密驗證: ${isValid ? '✅ 成功' : '❌ 失敗'}`);
    
    if (isValid) {
        console.log('\n🎉 檔案加密成功！');
        console.log('- 已生成: 建物.encrypted');
        console.log('- 原始檔案: 建物.csv (待移除)');
    }
    
} catch (error) {
    console.error('❌ 加密過程中發生錯誤:', error.message);
}