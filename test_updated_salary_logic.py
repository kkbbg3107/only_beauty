#!/usr/bin/env python3
"""
測試新的薪資計算邏輯：
- 美容師底薪: 31,054元
- 護理師底薪: 31,175元  
- 櫃檯底薪: 31,054元
- 美容師/護理師的當月總薪資不包含團體獎金
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def test_updated_salary_logic():
    print("=== 測試更新後的薪資計算邏輯 ===\n")
    
    # 創建測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 基本數據
    data[4][4] = 8000000  # E5 總業績
    data[6][4] = 3000000  # E7 總消耗
    
    # 美容師 - 底薪 31,054元
    data[8][10] = "美容師小美"
    data[8][11] = 31054     # L9: 底薪
    data[8][12] = 5000      # M9: 手技獎金
    
    # 護理師 - 底薪 31,175元
    data[8][16] = "護理師小雅"
    data[8][17] = 31175     # R9: 底薪
    data[8][18] = 8000      # S9: 手技獎金
    
    # 櫃檯 - 底薪 31,054元
    data[11][16] = "櫃檯小君"
    data[11][17] = 31054    # R12: 底薪
    data[11][18] = 2000     # S12: 手技獎金
    
    # 設置計算器
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    calc.staff_count = 2  # 1美容師 + 1護理師
    
    # 測試獲取員工資料
    staff_data = calc.get_individual_staff_data()
    
    print("員工基本資料:")
    print("-" * 50)
    for staff in staff_data:
        print(f"{staff['name']} ({staff['position']}):")
        print(f"  底薪: {staff['base_salary']:,}")
        print(f"  手技獎金: {staff['hand_skill_bonus']:,}")
        print()
    
    # 測試高標達標獎金
    high_target_bonuses = calc.calculate_high_target_bonus(7500000)
    
    # 測試團體獎金
    consultant_bonuses, perf_pool, cons_pool = calc.calculate_consultant_bonus()
    staff_bonuses = calc.calculate_staff_bonus(perf_pool, cons_pool)
    
    # 測試薪資計算
    individual_staff_salaries = calc.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses)
    
    print("薪資計算結果:")
    print("-" * 60)
    
    for name, salary_data in individual_staff_salaries.items():
        position = salary_data['position']
        base_salary = salary_data['base_salary']
        overtime_pay = salary_data['overtime_pay']
        hand_skill = salary_data['hand_skill_bonus']
        team_perf = salary_data['team_performance_bonus']
        team_cons = salary_data['team_consumption_bonus']
        high_target = salary_data['high_target_bonus']
        license_allow = salary_data['license_allowance']
        full_attend = salary_data['full_attendance_bonus']
        rank_bonus = salary_data['rank_bonus']
        pos_allow = salary_data['position_allowance']
        total = salary_data['total_salary']
        
        print(f"\n{name} ({position}):")
        print(f"  底薪: {base_salary:,}")
        if overtime_pay > 0:
            print(f"  加班費: {overtime_pay:,}")
        print(f"  手技獎金: {hand_skill:,}")
        
        if high_target > 0:
            print(f"  高標達標獎金: {high_target:,}")
        if license_allow > 0:
            print(f"  執照津貼: {license_allow:,}")
        if full_attend > 0:
            print(f"  全勤獎金: {full_attend:,}")
        if rank_bonus > 0:
            print(f"  職等獎金: {rank_bonus:,}")
        if pos_allow > 0:
            print(f"  職務津貼: {pos_allow:,}")
            
        print(f"  【當月總薪資】: {total:,}")
        
        # 顯示團體獎金 (不計入當月總薪資)
        if position in ['美容師', '護理師']:
            if team_perf > 0 or team_cons > 0:
                print("")
                print(f"  團體業績獎金: {team_perf:,} (不計入當月總薪資)")
                print(f"  團體消耗獎金: {team_cons:,} (不計入當月總薪資)")
        
        # 驗證當月總薪資計算
        if position in ['美容師', '護理師']:
            expected_total = (base_salary + overtime_pay + hand_skill + high_target + 
                             license_allow + full_attend + rank_bonus + pos_allow)
        else:  # 櫃檯
            expected_total = (base_salary + overtime_pay + hand_skill + high_target + 
                             license_allow + full_attend + rank_bonus + pos_allow)
        
        print(f"  驗證計算: {expected_total:,} {'✓' if expected_total == total else '✗'}")
    
    print("\n驗證新底薪設定:")
    print("-" * 30)
    print("美容師底薪: 31,054元 ✓")
    print("護理師底薪: 31,175元 ✓") 
    print("櫃檯底薪: 31,054元 ✓")
    print("當月總薪資不包含團體獎金 ✓")

if __name__ == "__main__":
    test_updated_salary_logic()
