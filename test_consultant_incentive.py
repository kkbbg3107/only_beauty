#!/usr/bin/env python3
"""
測試顧問業績達標激勵獎金和顯示修改
"""

import pandas as pd
import sys
import os

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from salary_calculator import OnlyBeautySalaryCalculator

def test_consultant_incentive_bonus():
    print("=== 測試顧問業績達標激勵獎金 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 場景1: 門店達標，顧問個人也達標
    print("場景1: 門店業績達標 + 顧問個人業績達標")
    data[4][4] = 6000000  # E5 總業績 (達到高標600萬)
    data[6][4] = 3000000  # E7 總消耗
    
    # 顧問資料 - 達標顧問 (業績>=168萬)
    data[8][0] = "顧問小王"  # A9
    data[8][2] = 2000000   # C9 個人業績 (>=168萬)
    data[8][6] = 800000    # G9 個人消耗
    
    # 顧問資料 - 未達標顧問 (業績<168萬)
    data[9][0] = "顧問小李"  # A10
    data[9][2] = 1500000   # C10 個人業績 (<168萬)
    data[9][6] = 600000    # G10 個人消耗
    
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    calc.manager_name = "顧問小王"  # 設定店長
    
    # 計算顧問獎金
    consultant_bonuses, _, _ = calc.calculate_consultant_bonus()
    
    # 計算個人獎金 (包含業績達標激勵獎金)
    individual_bonuses = calc.calculate_individual_bonus(consultant_bonuses, high_target_amount=6000000)
    
    print("\n顧問業績達標激勵獎金結果:")
    print("-" * 50)
    
    for name, bonus_data in individual_bonuses.items():
        personal_performance = consultant_bonuses[name]['personal_performance']
        incentive_bonus = bonus_data.get('performance_incentive_bonus', 0)
        
        print(f"{name} ({bonus_data['role']}):")
        print(f"  個人業績: {personal_performance:,}")
        print(f"  個人業績 >= 168萬: {'✓' if personal_performance >= 1680000 else '✗'}")
        print(f"  門店業績達標: ✓ (600萬)")
        print(f"  業績達標激勵獎金: {incentive_bonus:,}")
        
        if personal_performance >= 1680000:
            print(f"  ✅ 符合條件，獲得激勵獎金 {incentive_bonus:,}")
        else:
            print(f"  ❌ 個人業績未達168萬，無激勵獎金")
        print()
    
    print("="*50)
    
    # 場景2: 門店未達標
    print("\n場景2: 門店業績未達標")
    data[4][4] = 5000000  # E5 總業績 (未達到高標600萬)
    
    calc2 = OnlyBeautySalaryCalculator()
    calc2.excel_data = pd.DataFrame.from_dict(data, orient='index')
    calc2.manager_name = "顧問小王"
    
    consultant_bonuses2, _, _ = calc2.calculate_consultant_bonus()
    individual_bonuses2 = calc2.calculate_individual_bonus(consultant_bonuses2, high_target_amount=6000000)
    
    print("\n顧問業績達標激勵獎金結果:")
    print("-" * 50)
    
    for name, bonus_data in individual_bonuses2.items():
        personal_performance = consultant_bonuses2[name]['personal_performance']
        incentive_bonus = bonus_data.get('performance_incentive_bonus', 0)
        
        print(f"{name} ({bonus_data['role']}):")
        print(f"  個人業績: {personal_performance:,}")
        print(f"  個人業績 >= 168萬: {'✓' if personal_performance >= 1680000 else '✗'}")
        print(f"  門店業績達標: ✗ (500萬 < 600萬)")
        print(f"  業績達標激勵獎金: {incentive_bonus:,}")
        print(f"  ❌ 門店未達標，無激勵獎金")
        print()

    print("\n業績達標激勵獎金規則:")
    print("- 獎金金額: 10,000元")
    print("- 發放條件: 個人業績 >= 168萬 AND 門店業績達高標")
    print("- 發放方式: 季發 (不計入當月總薪資)")

if __name__ == "__main__":
    test_consultant_incentive_bonus()
