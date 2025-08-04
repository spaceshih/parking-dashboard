# IP白名單配置說明

## 🔧 設定步驟

### 1. 修改IP白名單
編輯 `index.html` 中的 `IP_WHITELIST` 設定：

```javascript
const IP_WHITELIST = {
    allowedIPs: [
        '192.168.1.100',        // 特定IP地址
        '192.168.1.0/24',       // IP範圍 (整個子網)
        '10.0.0.0/8',           // 更大的IP範圍
        '203.75.xxx.xxx',       // 您的公司IP
    ],
    developmentMode: false      // 設為false啟用IP白名單
};
```

### 2. 如何取得您的IP地址

**方法1 - 線上查詢**
- 訪問：https://whatismyipaddress.com/
- 或：https://ipinfo.io/ip

**方法2 - 命令列**
```bash
# Windows
curl ipinfo.io/ip

# Mac/Linux
curl ipinfo.io/ip
```

### 3. IP格式說明

| 格式 | 說明 | 範例 |
|------|------|------|
| `192.168.1.100` | 單一IP地址 | 只允許這個IP |
| `192.168.1.0/24` | IP範圍 | 允許192.168.1.1-192.168.1.254 |
| `10.0.0.0/8` | 大範圍 | 允許10.0.0.1-10.255.255.254 |

### 4. 常用IP範圍

```javascript
// 企業內網常用範圍
'192.168.0.0/16',     // 192.168.x.x
'10.0.0.0/8',         // 10.x.x.x
'172.16.0.0/12',      // 172.16.x.x - 172.31.x.x

// 開發測試
'127.0.0.1',          // 本機
'localhost',          // 本機
```

## 🚀 啟用IP白名單

將 `developmentMode` 設為 `false`：

```javascript
const IP_WHITELIST = {
    allowedIPs: [
        // 您的IP地址
    ],
    developmentMode: false  // 啟用IP檢查
};
```

## 🔍 測試方法

1. **允許的IP**：正常顯示儀表板
2. **不允許的IP**：顯示「訪問受限」頁面
3. **檢查控制台**：可看到IP檢查日誌

## ⚠️ 注意事項

- **動態IP**：家用網路IP可能會變化，建議使用IP範圍
- **公司網路**：通常有固定對外IP，可使用單一IP
- **手機網路**：IP經常變化，不建議加入白名單
- **VPN**：使用VPN時IP會改變

## 🛠️ 故障排除

### 無法訪問
1. 檢查 `developmentMode` 是否為 `false`
2. 確認IP地址格式正確
3. 檢查瀏覽器控制台錯誤訊息

### 取得實際IP
打開瀏覽器控制台，執行：
```javascript
fetch('https://api.ipify.org?format=json')
  .then(r => r.json())
  .then(d => console.log('您的IP:', d.ip));
```