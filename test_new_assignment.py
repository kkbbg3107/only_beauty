#!/usr/bin/env python3
"""
測試調整後的員工分配邏輯
K9-K15, N9-N15: 美容師
Q9-Q11: 護理師
Q12-Q15: 櫃檯
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def test_new_logic():
    print("=== 測試新的員工分配邏輯 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 基本數據
    data[4][4] = 8000000  # E5 總業績
    data[6][4] = 3000000  # E7 總消耗
    
    # K9-K12: 美容師
    data[8][10] = "美容師K9"
    data[8][11] = 30154
    data[8][12] = 5000
    
    data[9][10] = "美容師K10" 
    data[9][11] = 30154
    data[9][12] = 4500
    
    data[10][10] = "美容師K11"
    data[10][11] = 30154
    data[10][12] = 5500
    
    data[11][10] = "美容師K12"
    data[11][11] = 30154
    data[11][12] = 4800
    
    # N9-N11: 美容師
    data[8][13] = "美容師N9"
    data[8][14] = 30154
    data[8][15] = 6000
    
    data[9][13] = "美容師N10"
    data[9][14] = 30154
    data[9][15] = 5800
    
    data[10][13] = "美容師N11"
    data[10][14] = 30154
    data[10][15] = 5200
    
    # Q9-Q11: 護理師
    data[8][16] = "護理師Q9"
    data[8][17] = 31178
    data[8][18] = 8000
    
    data[9][16] = "護理師Q10"
    data[9][17] = 31178
    data[9][18] = 7500
    
    data[10][16] = "護理師Q11"
    data[10][17] = 31178
    data[10][18] = 7200
    
    # Q12-Q15: 櫃檯
    data[11][16] = "櫃檯Q12"
    data[11][17] = 31054
    data[11][18] = 2000
    
    data[12][16] = "櫃檯Q13"
    data[12][17] = 31054
    data[12][18] = 1800
    
    # 設置計算器
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    calc.staff_count = 12  # 7美容師 + 3護理師 + 2櫃檯
    
    # 測試獲取員工資料
    staff_data = calc.get_individual_staff_data()
    
    print("員工分配結果:")
    print("-" * 50)
    
    beauty_count = 0
    nurse_count = 0
    counter_count = 0
    
    for staff in staff_data:
        position = staff['position']
        row = staff['row']
        name = staff['name']
        
        if position == '美容師':
            beauty_count += 1
        elif position == '護理師':
            nurse_count += 1
        elif position == '櫃檯':
            counter_count += 1
            
        print(f"{name} ({position}) - 第{row}行")
    
    print("\n統計:")
    print(f"美容師: {beauty_count} 人 (應為K9-K15 + N9-N15)")
    print(f"護理師: {nurse_count} 人 (應為Q9-Q11)")
    print(f"櫃檯: {counter_count} 人 (應為Q12-Q15)")
    
    # 測試高標達標獎金
    print("\n高標達標獎金測試:")
    high_target_bonuses = calc.calculate_high_target_bonus(7500000)
    
    for name, bonus_data in high_target_bonuses.items():
        position = bonus_data['position']
        bonus = bonus_data['bonus']
        print(f"{name} ({position}): {bonus:,} 元")
    
    # 測試團體獎金分配
    print("\n團體獎金分配測試:")
    consultant_bonuses, perf_pool, cons_pool = calc.calculate_consultant_bonus()
    staff_bonuses = calc.calculate_staff_bonus(perf_pool, cons_pool)
    
    beauty_nurse_count = beauty_count + nurse_count
    print(f"美容師+護理師總人數: {beauty_nurse_count}")
    print(f"每人業績獎金: {staff_bonuses.get('performance_bonus_per_person', 0):,.0f}")
    print(f"每人消耗獎金: {staff_bonuses.get('consumption_bonus_per_person', 0):,.0f}")
    
    # 完整薪資計算
    print("\n完整薪資計算:")
    individual_staff_salaries = calc.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses)
    
    for name, salary_data in individual_staff_salaries.items():
        position = salary_data['position']
        total = salary_data['total_salary']
        team_bonus = salary_data['team_performance_bonus'] + salary_data['team_consumption_bonus']
        
        print(f"{name} ({position}): 總薪資 {total:,.0f} (團體獎金: {team_bonus:,.0f})")

if __name__ == "__main__":
    test_new_logic()
