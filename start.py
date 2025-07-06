#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Only Beauty 薪資計算系統啟動器
解決 Python 環境和 pandas 模組問題
"""

def main():
    print("=== Only Beauty 薪資計算系統 ===")
    print("正在檢查環境...")
    
    # 檢查 pandas
    try:
        import pandas as pd
        print(f"✅ pandas 已安裝，版本: {pd.__version__}")
    except ImportError:
        print("❌ pandas 未安裝，請執行以下命令:")
        print("   pip install pandas openpyxl xlrd")
        return
    
    # 檢查 openpyxl
    try:
        import openpyxl
        print("✅ openpyxl 已安裝")
    except ImportError:
        print("❌ openpyxl 未安裝，請執行: pip install openpyxl")
        return
    
    print("✅ 所有模組已就緒")
    print("正在啟動薪資計算系統...\n")
    
    # 導入並執行主程式
    try:
        from salary_calculator import OnlyBeautySalaryCalculator
        calculator = OnlyBeautySalaryCalculator()
        calculator.run()
    except Exception as e:
        print(f"❌ 程式執行錯誤: {e}")
        print("請檢查程式檔案是否完整")

if __name__ == "__main__":
    main()
