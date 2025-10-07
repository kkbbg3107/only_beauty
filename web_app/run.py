#!/usr/bin/env python3
"""
Only Beauty 薪資計算系統 - 網頁版啟動腳本

使用方法：
1. 安裝相依套件：pip install -r requirements.txt
2. 執行此腳本：python run.py
3. 開啟瀏覽器，前往 http://localhost:5000

功能特色：
- 檔案拖拽上傳與進度條顯示
- 即時計算進度追蹤
- 直觀的結果顯示界面
- 響應式設計，支援手機瀏覽
"""

import os
import sys

def check_requirements():
    """檢查必要的套件是否已安裝"""
    try:
        import flask
        import pandas
        import openpyxl
        import xlrd
        print("✅ 所有必要套件已安裝")
        return True
    except ImportError as e:
        print(f"❌ 缺少必要套件: {e}")
        print("請執行: pip install -r requirements.txt")
        return False

def create_directories():
    """創建必要的目錄"""
    directories = ['uploads', 'static', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 創建目錄: {directory}")

def main():
    """主函數"""
    print("Only Beauty 薪資計算系統 - 網頁版")
    print("=" * 50)

    # 檢查套件
    if not check_requirements():
        sys.exit(1)

    # 創建目錄
    create_directories()

    # 啟動應用
    try:
        from app import app
        print("\n🚀 啟動網頁伺服器...")
        print("📱 請在瀏覽器中開啟: http://localhost:5000")
        print("⏹️  按 Ctrl+C 停止伺服器")
        print("-" * 50)

        app.run(debug=True, host='0.0.0.0', port=5000)

    except KeyboardInterrupt:
        print("\n\n👋 伺服器已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()