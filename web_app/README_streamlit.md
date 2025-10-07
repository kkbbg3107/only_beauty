# Only Beauty 薪資計算系統 - Streamlit 版

## 部署到 Streamlit Cloud

這是 Only Beauty 薪資計算系統的 Streamlit 版本，專為雲端部署而設計。

### 🚀 快速部署

#### 方法 1: 使用 Streamlit Cloud (推薦)

1. **上傳到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Only Beauty Salary Calculator"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/only-beauty-salary-calculator.git
   git push -u origin main
   ```

2. **在 Streamlit Cloud 部署**
   - 前往 [share.streamlit.io](https://share.streamlit.io)
   - 使用 GitHub 帳號登入
   - 點擊 "New app"
   - 選擇你的 repository: `YOUR_USERNAME/only-beauty-salary-calculator`
   - 主文件路徑設為: `streamlit_app.py`
   - 點擊 "Deploy!"

#### 方法 2: 本地運行

```bash
# 安裝相依套件
pip install -r requirements.txt

# 運行應用
streamlit run streamlit_app.py
```

### 📁 檔案結構

```
web_app/
├── streamlit_app.py          # Streamlit 主應用程式
├── requirements.txt          # Python 相依套件
├── README_streamlit.md       # 部署說明文件
├── .streamlit/
│   └── config.toml          # Streamlit 配置
├── .gitignore               # Git 忽略檔案
└── uploads/                 # 上傳檔案暫存目錄 (本地用)
```

### 🎯 主要功能

1. **📊 檔案上傳與解析**
   - 支援 Excel (.xlsx, .xls) 檔案上傳
   - 自動檢測和解析數字工作表
   - 即時進度顯示

2. **💰 薪資計算**
   - 產品銷售統計和達標獎金
   - 團體業績/消耗獎金 (累進制)
   - 個人業績/消耗獎金計算
   - 美容師/護理師/櫃檯薪資明細
   - 高標達標獎金計算

3. **📈 結果展示**
   - 互動式分頁界面
   - 詳細的薪資明細表格
   - 統計摘要和圖表
   - JSON 格式結果下載

### ⚙️ 配置說明

#### Streamlit 配置 (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#667eea"        # 主色調
backgroundColor = "#FFFFFF"     # 背景色
secondaryBackgroundColor = "#f0f2f6"  # 次要背景色
textColor = "#262730"          # 文字色

[server]
maxUploadSize = 50             # 最大上傳檔案大小 (MB)
enableCORS = false             # 跨域設定
enableXsrfProtection = false   # XSRF 保護

[browser]
gatherUsageStats = false       # 關閉使用統計
```

### 🔧 環境需求

- Python 3.7+
- Streamlit >= 1.28.0
- pandas >= 1.5.3
- openpyxl >= 3.1.2
- xlrd >= 2.0.1
- numpy >= 1.24.3

### 📋 使用說明

1. **步驟 1: 上傳 Excel 檔案**
   - 拖拽或點擊上傳包含薪資資料的 Excel 檔案
   - 系統會自動檢測數字工作表並解析

2. **步驟 2: 設定基本參數**
   - 員工人數: 美容師和護理師總人數
   - 店長名稱: 可選，用於個人獎金計算
   - 高標金額: 可選，設定高標達標獎金門檻

3. **步驟 3: 開始計算**
   - 點擊「開始計算薪資」按鈕
   - 系統會顯示計算進度

4. **步驟 4: 查看結果**
   - 分頁查看不同類型的計算結果
   - 可下載 JSON 格式的完整結果

### 🚨 注意事項

1. **檔案格式**: 僅支援 Excel 格式 (.xlsx, .xls)
2. **檔案大小**: 最大上傳檔案大小為 50MB
3. **資料隱私**: 上傳的檔案僅在記憶體中處理，不會永久儲存
4. **工作表格式**: Excel 檔案必須包含數字命名的工作表

### 🔒 安全性

- 所有檔案處理都在記憶體中進行
- 不會在伺服器上永久儲存任何上傳檔案
- 使用臨時檔案進行處理，計算完成後自動清理
- 不收集任何使用者個人資料

### 📊 效能最佳化

- 使用 pandas 高效率處理 Excel 檔案
- 記憶體管理：及時清理臨時檔案
- 響應式介面：支援各種螢幕尺寸
- 快取機制：避免重複計算

### 🐛 故障排除

#### 常見問題

1. **檔案上傳失敗**
   - 檢查檔案格式是否為 .xlsx 或 .xls
   - 確認檔案大小不超過 50MB
   - 檢查檔案是否損壞

2. **計算錯誤**
   - 確認 Excel 檔案包含數字工作表
   - 檢查資料格式是否符合預期
   - 查看錯誤訊息詳情

3. **部署問題**
   - 確認 requirements.txt 中的套件版本
   - 檢查 Python 版本相容性
   - 查看 Streamlit Cloud 部署日誌

### 📞 支援

如有問題或建議，請聯繫系統管理員。

### 📜 授權

此專案為 Only Beauty 內部使用工具。