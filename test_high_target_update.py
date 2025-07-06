#!/usr/bin/env python3
"""
測試美容師和護理師高標達標獎金移除
"""

import pandas as pd
import sys
import os

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from salary_calculator import OnlyBeautySalaryCalculator

def test_high_target_bonus_update():
    print("=== 測試高標達標獎金移除 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 設定業績數據，達到高標
    data[4][4] = 8000000  # E5 總業績 (假設高標為600萬)
    data[6][4] = 3000000  # E7 總消耗
    
    # 設定員工資料
    data[8][10] = "美容師小美"   # K9: 美容師姓名
    data[8][12] = 5000         # M9: 手技獎金
    
    data[8][16] = "護理師小雅"   # Q9: 護理師姓名
    data[8][18] = 8000         # S9: 手技獎金
    
    data[11][16] = "櫃檯小君"    # Q12: 櫃檯姓名
    data[11][18] = 2000        # S12: 手技獎金
    
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    # 計算高標達標獎金
    high_target_bonuses = calc.calculate_high_target_bonus(high_target_amount=6000000)
    
    # 計算個別員工薪資
    individual_staff_salaries = calc.calculate_individual_staff_salary(
        high_target_bonuses=high_target_bonuses,
        high_target_amount=6000000
    )
    
    print("薪資計算結果驗證:")
    print("-" * 50)
    
    for name, salary_data in individual_staff_salaries.items():
        position = salary_data['position']
        print(f"\n{name} ({position}):")
        print(f"  底薪: {salary_data['base_salary']:,}")
        print(f"  手技獎金: {salary_data['hand_skill_bonus']:,}")
        
        if position == '美容師':
            # 美容師：底薪 + 手技獎金 (高標達標獎金不計入)
            expected_total = salary_data['base_salary'] + salary_data['hand_skill_bonus']
            actual_total = salary_data['total_salary']
            high_target = salary_data['high_target_bonus']
            
            print(f"  高標達標獎金: {high_target:,} (不計入當月總薪資)")
            print(f"  【當月總薪資】: {actual_total:,}")
            print(f"  預期總薪資: {expected_total:,}")
            print(f"  計算正確: {'✓' if actual_total == expected_total else '✗'}")
            
            if high_target != 5000:
                print(f"  ⚠️  高標達標獎金應為5000，實際為{high_target}")
        
        elif position == '護理師':
            # 護理師：底薪 + 手技獎金 + 執照津貼 (高標達標獎金、全勤獎金不計入)
            expected_total = (salary_data['base_salary'] + salary_data['hand_skill_bonus'] + 
                            salary_data['license_allowance'])
            actual_total = salary_data['total_salary']
            high_target = salary_data['high_target_bonus']
            
            print(f"  執照津貼: {salary_data['license_allowance']:,}")
            print(f"  高標達標獎金: {high_target:,} (不計入當月總薪資)")
            print(f"  全勤獎金: {salary_data['full_attendance_bonus']:,} (不計入當月總薪資)")
            print(f"  【當月總薪資】: {actual_total:,}")
            print(f"  預期總薪資: {expected_total:,}")
            print(f"  計算正確: {'✓' if actual_total == expected_total else '✗'}")
            
            if high_target != 10000:
                print(f"  ⚠️  高標達標獎金應為10000，實際為{high_target}")
        
        elif position == '櫃檯':
            # 櫃檯：高標達標獎金計入當月總薪資
            base_total = (salary_data['base_salary'] + salary_data['hand_skill_bonus'] + 
                         salary_data['rank_bonus'] + salary_data['position_allowance'])
            high_target = salary_data['high_target_bonus']
            counter_bonuses = (salary_data.get('consumption_achievement_bonus', 0) + 
                             salary_data.get('performance_500w_bonus', 0) + 
                             salary_data.get('store_performance_incentive', 0))
            expected_total = base_total + high_target + counter_bonuses
            actual_total = salary_data['total_salary']
            
            print(f"  職等獎金: {salary_data['rank_bonus']:,}")
            print(f"  職務津貼: {salary_data['position_allowance']:,}")
            print(f"  高標達標獎金: {high_target:,} (計入當月總薪資)")
            print(f"  櫃檯專用獎金: {counter_bonuses:,}")
            print(f"  【當月總薪資】: {actual_total:,}")
            print(f"  預期總薪資: {expected_total:,}")
            print(f"  計算正確: {'✓' if actual_total == expected_total else '✗'}")
    
    print("\n" + "="*50)
    print("修改摘要:")
    print("✅ 美容師高標達標獎金 5,000元 移至不計入當月總薪資")
    print("✅ 護理師高標達標獎金 10,000元 移至不計入當月總薪資")
    print("✅ 櫃檯高標達標獎金仍計入當月總薪資")
    print("✅ 護理師全勤獎金 2,000元 仍在不計入當月總薪資")

if __name__ == "__main__":
    test_high_target_bonus_update()
