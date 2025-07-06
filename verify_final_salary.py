#!/usr/bin/env python3
"""
最終驗證腳本 - 確認所有底薪設定正確
美容師: 31,054元
護理師: 31,175元
櫃檯: 31,054元
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def verify_final_salary_settings():
    print("=== 最終底薪設定驗證 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 基本數據
    data[4][4] = 8000000  # E5 總業績
    data[6][4] = 3000000  # E7 總消耗
    
    # 設定底薪測試數據
    # 美容師1 - K欄 (底薪 31,054元)
    data[8][10] = "美容師小美"
    data[8][11] = 31054     # L9: 底薪
    data[8][12] = 5000      # M9: 手技獎金
    
    # 美容師2 - N欄 (底薪 31,054元)
    data[9][13] = "美容師小玲"
    data[9][14] = 31054     # O10: 底薪
    data[9][15] = 3000      # P10: 手技獎金
    
    # 護理師 (底薪 31,175元)
    data[8][16] = "護理師小雅"
    data[8][17] = 31175     # R9: 底薪
    data[8][18] = 8000      # S9: 手技獎金
    
    # 櫃檯 (底薪 31,054元)
    data[11][16] = "櫃檯小君"
    data[11][17] = 31054    # R12: 底薪
    data[11][18] = 2000     # S12: 手技獎金
    
    # 設置計算器
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    calc.staff_count = 3  # 2美容師 + 1護理師
    
    # 測試獲取員工資料
    staff_data = calc.get_individual_staff_data()
    
    print("員工底薪驗證:")
    print("-" * 50)
    
    expected_salaries = {
        '美容師': 31054,
        '護理師': 31175,
        '櫃檯': 31054
    }
    
    all_correct = True
    
    for staff in staff_data:
        name = staff['name']
        position = staff['position']
        actual_salary = staff['base_salary']
        expected_salary = expected_salaries[position]
        
        is_correct = actual_salary == expected_salary
        if not is_correct:
            all_correct = False
        
        status = "✓" if is_correct else "✗"
        print(f"{name} ({position}):")
        print(f"  實際底薪: {actual_salary:,}")
        print(f"  預期底薪: {expected_salary:,}")
        print(f"  驗證結果: {status}")
        print()
    
    print("底薪設定總結:")
    print("-" * 30)
    for position, expected in expected_salaries.items():
        print(f"{position}: {expected:,}元 ✓")
    
    print(f"\n整體驗證結果: {'全部正確 ✓' if all_correct else '發現錯誤 ✗'}")
    
    if all_correct:
        print("\n🎉 所有底薪設定都符合要求！")
        print("美容師: 31,054元")
        print("護理師: 31,175元")
        print("櫃檯: 31,054元")
    else:
        print("\n❌ 發現底薪設定錯誤，請檢查！")

if __name__ == "__main__":
    verify_final_salary_settings()
