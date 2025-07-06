#!/usr/bin/env python3

print("簡單測試開始...")

try:
    import pandas as pd
    print("✓ pandas 導入成功")
    
    import os
    import sys
    print("✓ 基本模組導入成功")
    
    # 檢查檔案是否存在
    if os.path.exists("salary_calculator.py"):
        print("✓ salary_calculator.py 檔案存在")
    else:
        print("✗ salary_calculator.py 檔案不存在")
    
    # 嘗試導入
    from salary_calculator import OnlyBeautySalaryCalculator
    print("✓ OnlyBeautySalaryCalculator 導入成功")
    
    # 創建實例
    calc = OnlyBeautySalaryCalculator()
    print("✓ 計算器實例創建成功")
    
    print("\n=== 測試櫃檯獎金規則 ===")
    
    # 創建簡單測試數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 設定業績和消耗數據
    data[4][4] = 8000000  # E5 總業績
    data[6][4] = 3500000  # E7 總消耗
    
    # 設定櫃檯員工
    data[11][16] = "櫃檯小君"
    data[11][17] = 31054    # 底薪
    data[11][18] = 2000     # 手技獎金
    
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    # 測試個別員工薪資計算
    individual_salaries = calc.calculate_individual_staff_salary(high_target_amount=6000000)
    
    print("櫃檯員工薪資計算結果:")
    for name, salary_data in individual_salaries.items():
        if salary_data['position'] == '櫃檯':
            print(f"\n{name} 薪資明細:")
            print(f"  底薪: {salary_data['base_salary']:,}")
            print(f"  手技獎金: {salary_data['hand_skill_bonus']:,}")
            print(f"  職等獎金: {salary_data['rank_bonus']:,}")
            print(f"  職務津貼: {salary_data['position_allowance']:,}")
            
            # 新的櫃檯獎金
            consumption_bonus = salary_data.get('consumption_achievement_bonus', 0)
            performance_bonus = salary_data.get('performance_500w_bonus', 0)
            incentive_bonus = salary_data.get('store_performance_incentive', 0)
            
            print(f"  門店業績達標+消耗300萬獎金: {consumption_bonus:,}")
            print(f"  業績500萬獎金: {performance_bonus:,}")
            print(f"  門店業績激勵獎金: {incentive_bonus:,}")
            print(f"  【當月總薪資】: {salary_data['total_salary']:,}")
            
            # 驗證獎金規則
            print(f"\n獎金規則驗證:")
            print(f"  業績 {data[4][4]:,} >= 600萬(高標): {'✓' if data[4][4] >= 6000000 else '✗'}")
            print(f"  消耗 {data[6][4]:,} >= 300萬: {'✓' if data[6][4] >= 3000000 else '✗'}")
            print(f"  業績 {data[4][4]:,} >= 500萬: {'✓' if data[4][4] >= 5000000 else '✗'}")
            
            expected_consumption = 3000 if (data[4][4] >= 6000000 and data[6][4] >= 3000000) else 0
            expected_performance = 5000 if data[4][4] >= 5000000 else 0
            expected_incentive = 5000 if data[4][4] >= 6000000 else 0
            
            print(f"\n預期獎金:")
            print(f"  消耗達標獎金: {expected_consumption:,} (實際: {consumption_bonus:,}) {'✓' if consumption_bonus == expected_consumption else '✗'}")
            print(f"  業績500萬獎金: {expected_performance:,} (實際: {performance_bonus:,}) {'✓' if performance_bonus == expected_performance else '✗'}")
            print(f"  業績激勵獎金: {expected_incentive:,} (實際: {incentive_bonus:,}) {'✓' if incentive_bonus == expected_incentive else '✗'}")
    
    print("\n測試完成!")
    
except Exception as e:
    print(f"✗ 錯誤: {e}")
    import traceback
    traceback.print_exc()
