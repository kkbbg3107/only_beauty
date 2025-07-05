#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def create_test_excel():
    """創建測試用的Excel檔案"""
    
    # 建立空的DataFrame，大小足夠包含所需的儲存格
    df = pd.DataFrame(index=range(20), columns=range(15))
    
    # 填入測試數據
    df.iloc[4, 4] = 5000000  # E5 - 總業績
    df.iloc[6, 4] = 4000000  # E7 - 總消耗
    
    # 顧問資料（A9開始）
    consultants = [
        ("王顧問", 2000000, 1800000),  # A9, C9, G9
        ("李顧問", 1500000, 1200000),  # A10, C10, G10
        ("張顧問", 1000000, 800000),   # A11, C11, G11
        ("公司", 500000, 200000),      # A12, C12, G12 (會被排除)
    ]
    
    for i, (name, performance, consumption) in enumerate(consultants):
        row = 8 + i  # 從第9行開始（index 8）
        df.iloc[row, 0] = name          # A欄
        df.iloc[row, 2] = performance   # C欄
        df.iloc[row, 6] = consumption   # G欄
    
    # 保存為Excel檔案
    filename = "test_salary_data.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 創建多個工作表，包含數字和非數字的
        df.to_excel(writer, sheet_name='202412', index=False, header=False)  # 數字最大的工作表
        df.to_excel(writer, sheet_name='202411', index=False, header=False)
        df.to_excel(writer, sheet_name='202410', index=False, header=False)
        
        # 創建一些非數字工作表（應該被過濾掉）
        empty_df = pd.DataFrame()
        empty_df.to_excel(writer, sheet_name='Summary', index=False)
        empty_df.to_excel(writer, sheet_name='Data', index=False)
    
    print(f"測試Excel檔案已創建: {filename}")
    print("測試數據:")
    print(f"總業績(E5): {df.iloc[4, 4]:,.0f}")
    print(f"總消耗(E7): {df.iloc[6, 4]:,.0f}")
    print("顧問資料:")
    for i, (name, performance, consumption) in enumerate(consultants):
        print(f"  {name}: 業績 {performance:,.0f}, 消耗 {consumption:,.0f}")
    
    return filename

if __name__ == "__main__":
    create_test_excel()
