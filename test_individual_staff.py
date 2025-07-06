#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試個別員工薪資計算功能
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def create_test_excel():
    """創建測試用的Excel數據"""
    # 創建測試數據
    data = {}
    
    # 設定基本業績數據
    for i in range(20):
        data[i] = [None] * 25
    
    # E5: 總業績
    data[4][4] = 8000000  # 高於高標
    
    # E7: 總消耗
    data[6][4] = 3000000
    
    # A9-A11: 顧問名稱和數據
    data[8][0] = "王小美"   # A9
    data[8][2] = 2000000   # C9 個人業績
    data[8][6] = 800000    # G9 個人消耗
    
    data[9][0] = "李小花"   # A10
    data[9][2] = 1800000   # C10 個人業績
    data[9][6] = 600000    # G10 個人消耗
    
    # K9-K15: 美容師資料
    data[8][10] = "美容師A"  # K9
    data[8][11] = 30000     # L9 底薪
    data[8][12] = 5000      # M9 手技獎金
    
    data[9][10] = "美容師B"  # K10
    data[9][11] = 32000     # L10 底薪
    data[9][12] = 4500      # M10 手技獎金
    
    data[10][10] = "美容師C" # K11
    data[10][11] = 28000    # L11 底薪
    data[10][12] = 6000     # M11 手技獎金
    
    # N9-N15: 護理師資料
    data[8][13] = "護理師A"  # N9
    data[8][14] = 35000     # O9 底薪
    data[8][15] = 8000      # P9 手技獎金
    
    data[9][13] = "護理師B"  # N10
    data[9][14] = 38000     # O10 底薪
    data[9][15] = 7500      # P10 手技獎金
    
    # Q9-Q15: 櫃檯資料
    data[8][16] = "櫃檯A"   # Q9
    data[8][17] = 26000    # R9 底薪
    data[8][18] = 2000     # S9 手技獎金
    
    data[9][16] = "櫃檯B"   # Q10
    data[9][17] = 28000    # R10 底薪
    data[9][18] = 1500     # S10 手技獎金
    
    # 轉換為DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    return df

def test_individual_staff_calculation():
    """測試個別員工薪資計算功能"""
    print("=== 測試個別員工薪資計算功能 ===\n")
    
    # 創建測試數據
    test_data = create_test_excel()
    
    # 初始化計算器
    calculator = OnlyBeautySalaryCalculator()
    calculator.excel_data = test_data
    calculator.staff_count = 7  # 3美容師 + 2護理師 + 2櫃檯
    calculator.manager_name = "王小美"
    
    print("1. 測試獲取個別員工資料:")
    staff_data = calculator.get_individual_staff_data()
    for staff in staff_data:
        print(f"  {staff['name']} ({staff['position']}): 底薪={staff['base_salary']:,}, 手技獎金={staff['hand_skill_bonus']:,}")
    
    print("\n2. 測試高標達標獎金計算:")
    high_target_amount = 7500000  # 設定高標
    high_target_bonuses = calculator.calculate_high_target_bonus(high_target_amount)
    
    print("\n3. 測試團體獎金計算:")
    consultant_bonuses, perf_pool, cons_pool = calculator.calculate_consultant_bonus()
    staff_bonuses = calculator.calculate_staff_bonus(perf_pool, cons_pool)
    
    print("\n4. 測試個別員工完整薪資計算:")
    individual_staff_salaries = calculator.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses)
    
    print("\n5. 顯示結果:")
    calculator.display_results({}, staff_bonuses, {}, {}, individual_staff_salaries, high_target_bonuses)

def test_edge_cases():
    """測試邊界情況"""
    print("\n=== 測試邊界情況 ===\n")
    
    calculator = OnlyBeautySalaryCalculator()
    
    # 測試1: 沒有Excel數據
    print("1. 測試沒有Excel數據:")
    staff_data = calculator.get_individual_staff_data()
    print(f"   結果: {len(staff_data)} 筆員工資料")
    
    # 測試2: 空的員工資料
    print("\n2. 測試空的員工資料:")
    calculator.excel_data = pd.DataFrame()
    high_target_bonuses = calculator.calculate_high_target_bonus(5000000)
    print(f"   高標達標獎金: {len(high_target_bonuses)} 筆")
    
    # 測試3: 總業績未達高標
    print("\n3. 測試總業績未達高標:")
    test_data = create_test_excel()
    test_data.iloc[4, 4] = 5000000  # 總業績低於高標
    calculator.excel_data = test_data
    high_target_bonuses = calculator.calculate_high_target_bonus(7500000)
    print(f"   高標達標獎金: {len(high_target_bonuses)} 筆")

if __name__ == "__main__":
    test_individual_staff_calculation()
    test_edge_cases()
    print("\n測試完成！")
