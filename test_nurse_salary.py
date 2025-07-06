#!/usr/bin/env python3
"""
測試護理師全勤獎金移除後的薪資計算
"""

import pandas as pd
import sys
import os

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from salary_calculator import OnlyBeautySalaryCalculator

def test_nurse_salary_update():
    print("=== 測試護理師全勤獎金移除 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 設定基本數據
    data[4][4] = 6000000  # E5 總業績
    data[6][4] = 3000000  # E7 總消耗
    
    # 設定護理師資料
    data[8][16] = "護理師小雅"   # Q9: 護理師姓名
    data[8][18] = 8000         # S9: 手技獎金
    
    # 設定美容師資料作為對照
    data[8][10] = "美容師小美"   # K9: 美容師姓名
    data[8][12] = 5000         # M9: 手技獎金
    
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    # 計算個別員工薪資
    individual_staff_salaries = calc.calculate_individual_staff_salary()
    
    print("員工薪資計算結果:")
    print("-" * 50)
    
    for name, salary_data in individual_staff_salaries.items():
        position = salary_data['position']
        print(f"\n{name} ({position}):")
        print(f"  底薪: {salary_data['base_salary']:,}")
        print(f"  手技獎金: {salary_data['hand_skill_bonus']:,}")
        
        if position == '護理師':
            print(f"  執照津貼: {salary_data['license_allowance']:,}")
            print(f"  全勤獎金: {salary_data['full_attendance_bonus']:,} (不計入當月總薪資)")
            
            # 驗證薪資計算
            expected_total = (salary_data['base_salary'] + salary_data['hand_skill_bonus'] + 
                            salary_data['license_allowance'])
            actual_total = salary_data['total_salary']
            
            print(f"  【當月總薪資】: {actual_total:,}")
            print(f"  預期總薪資: {expected_total:,}")
            print(f"  計算正確: {'✓' if actual_total == expected_total else '✗'}")
            
            if actual_total != expected_total:
                print(f"  ⚠️  計算錯誤！全勤獎金 {salary_data['full_attendance_bonus']:,} 被計入了總薪資")
        
        elif position == '美容師':
            expected_total = salary_data['base_salary'] + salary_data['hand_skill_bonus']
            actual_total = salary_data['total_salary']
            
            print(f"  【當月總薪資】: {actual_total:,}")
            print(f"  預期總薪資: {expected_total:,}")
            print(f"  計算正確: {'✓' if actual_total == expected_total else '✗'}")
    
    print("\n薪資結構說明:")
    print("- 美容師當月總薪資 = 底薪 + 手技獎金")
    print("- 護理師當月總薪資 = 底薪 + 手技獎金 + 執照津貼")
    print("- 護理師全勤獎金不計入當月總薪資，單獨顯示")

if __name__ == "__main__":
    test_nurse_salary_update()
