#!/usr/bin/env python3
"""
測試櫃檯新獎金規則
"""

import pandas as pd
import sys
import os

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from salary_calculator import OnlyBeautySalaryCalculator
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)

def test_counter_bonus():
    print("=== 測試櫃檯新獎金規則 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 測試場景1: 符合所有櫃檯獎金條件
    print("場景1: 業績800萬, 消耗350萬, 高標達標金額600萬")
    data[4][4] = 8000000  # E5 總業績 (>500萬, >600萬達標)
    data[6][4] = 3500000  # E7 總消耗 (>300萬)
    
    # 櫃檯員工
    data[11][16] = "櫃檯小君"
    data[11][17] = 31054    # R12: 底薪
    data[11][18] = 2000     # S12: 手技獎金
    
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    # 計算櫃檯薪資 (高標達標金額 600萬)
    individual_staff_salaries = calc.calculate_individual_staff_salary(
        high_target_amount=6000000
    )
    
    print("櫃檯獎金明細:")
    for name, salary_data in individual_staff_salaries.items():
        if salary_data['position'] == '櫃檯':
            print(f"{name}:")
            print(f"  底薪: {salary_data['base_salary']:,}")
            print(f"  手技獎金: {salary_data['hand_skill_bonus']:,}")
            print(f"  職等獎金: {salary_data['rank_bonus']:,}")
            print(f"  職務津貼: {salary_data['position_allowance']:,}")
            print(f"  門店業績達標+消耗300萬獎金: {salary_data.get('consumption_achievement_bonus', 0):,}")
            print(f"  業績500萬獎金: {salary_data.get('performance_500w_bonus', 0):,}")
            print(f"  門店業績激勵獎金: {salary_data.get('store_performance_incentive', 0):,}")
            print(f"  【當月總薪資】: {salary_data['total_salary']:,}")
    
    print("\n" + "="*50)
    
    # 測試場景2: 只符合部分條件
    print("場景2: 業績400萬, 消耗200萬, 高標達標金額600萬")
    data[4][4] = 4000000  # E5 總業績 (<500萬, <600萬未達標)
    data[6][4] = 2000000  # E7 總消耗 (<300萬)
    
    calc2 = OnlyBeautySalaryCalculator()
    calc2.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    individual_staff_salaries2 = calc2.calculate_individual_staff_salary(
        high_target_amount=6000000
    )
    
    print("櫃檯獎金明細:")
    for name, salary_data in individual_staff_salaries2.items():
        if salary_data['position'] == '櫃檯':
            print(f"{name}:")
            print(f"  底薪: {salary_data['base_salary']:,}")
            print(f"  手技獎金: {salary_data['hand_skill_bonus']:,}")
            print(f"  職等獎金: {salary_data['rank_bonus']:,}")
            print(f"  職務津貼: {salary_data['position_allowance']:,}")
            print(f"  門店業績達標+消耗300萬獎金: {salary_data.get('consumption_achievement_bonus', 0):,}")
            print(f"  業績500萬獎金: {salary_data.get('performance_500w_bonus', 0):,}")
            print(f"  門店業績激勵獎金: {salary_data.get('store_performance_incentive', 0):,}")
            print(f"  【當月總薪資】: {salary_data['total_salary']:,}")

    print("\n櫃檯獎金規則說明:")
    print("1. 門店業績達標+消耗300萬獎金: 需要業績達高標 AND 消耗≥300萬")
    print("2. 業績500萬獎金: 需要業績≥500萬")
    print("3. 門店業績激勵獎金: 需要業績達高標")

if __name__ == "__main__":
    test_counter_bonus()
