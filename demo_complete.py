#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Only Beauty 薪資計算系統 - 完整使用示例
展示所有新功能的使用方法
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def create_demo_excel():
    """創建示例Excel數據"""
    # 創建完整的示例數據
    data = {}
    for i in range(25):
        data[i] = [None] * 25
    
    # 基本業績數據
    data[4][4] = 8500000   # E5: 總業績 (達到高標)
    data[6][4] = 3200000   # E7: 總消耗
    
    # 顧問資料 (A9-A12)
    data[8][0] = "王店長"    # A9
    data[8][2] = 2500000    # C9 個人業績
    data[8][6] = 900000     # G9 個人消耗
    
    data[9][0] = "李顧問"    # A10
    data[9][2] = 2000000    # C10 個人業績
    data[9][6] = 700000     # G10 個人消耗
    
    data[10][0] = "張顧問"   # A11
    data[10][2] = 1800000   # C11 個人業績
    data[10][6] = 600000    # G11 個人消耗
    
    # 美容師資料 (K9-K13)
    data[8][10] = "美容師小美"   # K9
    data[8][11] = 30154         # L9 底薪+加班費
    data[8][12] = 6000          # M9 手技獎金
    
    data[9][10] = "美容師小花"   # K10
    data[9][11] = 30154         # L10
    data[9][12] = 5500          # M10
    
    data[10][10] = "美容師小玉"  # K11
    data[10][11] = 30154        # L11
    data[10][12] = 4800         # M11
    
    # 美容師資料 (N9-N11)
    data[8][13] = "美容師小雅"   # N9
    data[8][14] = 30154         # O9 底薪+加班費
    data[8][15] = 8500          # P9 手技獎金
    
    data[9][13] = "美容師小芳"   # N10
    data[9][14] = 30154         # O10
    data[9][15] = 7800          # P10
    
    # 護理師資料 (Q9-Q11)
    data[8][16] = "護理師小君"   # Q9
    data[8][17] = 31178         # R9 底薪+加班費
    data[8][18] = 2500          # S9 手技獎金
    
    data[9][16] = "護理師小欣"   # Q10
    data[9][17] = 31178         # R10
    data[9][18] = 2200          # S10
    
    # 櫃檯資料 (Q12-Q15)
    data[11][16] = "櫃檯小婷"    # Q12
    data[11][17] = 31054        # R12 底薪+加班費
    data[11][18] = 1800         # S12 手技獎金
    
    data[12][16] = "櫃檯小慧"    # Q13
    data[12][17] = 31054        # R13
    data[12][18] = 1600         # S13
    
    return pd.DataFrame.from_dict(data, orient='index')

def demo_complete_calculation():
    """示範完整的薪資計算流程"""
    print("="*80)
    print("Only Beauty 薪資計算系統 - 完整功能示範")
    print("="*80)
    
    # 初始化系統
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = create_demo_excel()
    calc.staff_count = 9  # 5美容師 + 2護理師 + 2櫃檯
    calc.manager_name = "王店長"
    
    print("\n📊 基本資料設定:")
    print(f"   美容師/護理師人數: {calc.staff_count}")
    print(f"   店長: {calc.manager_name}")
    
    # 1. 產品銷售統計 (模擬)
    print("\n🛍️  產品銷售統計:")
    product_sales = {"王店長": 35, "李顧問": 28, "張顧問": 32}
    product_bonuses = calc.calculate_product_bonus(product_sales)
    
    # 2. 團體獎金計算
    print("\n💰 團體獎金計算:")
    consultant_bonuses, perf_pool, cons_pool = calc.calculate_consultant_bonus(product_bonuses)
    staff_bonuses = calc.calculate_staff_bonus(perf_pool, cons_pool)
    
    # 3. 個人獎金計算
    print("\n🎯 個人獎金計算:")
    individual_bonuses = calc.calculate_individual_bonus(consultant_bonuses)
    
    # 4. 高標達標獎金
    print("\n🚀 高標達標獎金計算:")
    high_target_amount = 8000000  # 設定高標 800萬
    high_target_bonuses = calc.calculate_high_target_bonus(high_target_amount)
    
    # 5. 個別員工薪資
    print("\n👥 個別員工薪資計算:")
    individual_staff_salaries = calc.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses)
    
    # 6. 顯示完整結果
    print("\n" + "="*80)
    print("完整薪資計算結果")
    print("="*80)
    
    calc.display_results(
        consultant_bonuses, 
        staff_bonuses, 
        product_bonuses, 
        individual_bonuses,
        individual_staff_salaries, 
        high_target_bonuses
    )
    
    # 7. 總結統計
    print("\n📈 總結統計:")
    print("-" * 60)
    
    total_consultant_bonus = sum(
        c['total_bonus'] + individual_bonuses.get(name, {}).get('individual_total', 0)
        for name, c in consultant_bonuses.items()
    )
    
    total_product_bonus = sum(p['bonus'] for p in product_bonuses.values())
    total_high_target_bonus = sum(h['bonus'] for h in high_target_bonuses.values())
    total_staff_salary = sum(s['total_salary'] for s in individual_staff_salaries.values())
    
    print(f"顧問總獎金: {total_consultant_bonus:,.0f} 元")
    print(f"產品達標獎金: {total_product_bonus:,.0f} 元")
    print(f"高標達標獎金: {total_high_target_bonus:,.0f} 元")
    print(f"個別員工總薪資: {total_staff_salary:,.0f} 元")
    print(f"系統總支出: {total_consultant_bonus + total_product_bonus + total_high_target_bonus + total_staff_salary:,.0f} 元")

def demo_features():
    """示範系統特色功能"""
    print("\n" + "="*80)
    print("系統特色功能示範")
    print("="*80)
    
    calc = OnlyBeautySalaryCalculator()
    
    print("\n1. 🎯 高標達標獎金配置:")
    for position, amount in calc.high_target_bonuses.items():
        print(f"   {position}: {amount:,} 元")
    
    print("\n2. 📊 累進制獎金級距:")
    print("   業績獎金級距:")
    for min_val, max_val, rate in calc.performance_bonus_levels:
        max_str = f"{max_val:,}" if max_val != float('inf') else "無上限"
        print(f"   {min_val:,} - {max_str}: {rate*100:.1f}%")
    
    print("\n3. 👤 個人獎金級距 (店長 vs 顧問):")
    print("   店長業績級距:")
    for min_val, max_val, rate in calc.manager_performance_levels:
        max_str = f"{max_val:,}" if max_val != float('inf') else "無上限"
        print(f"   {min_val:,} - {max_str}: {rate*100:.1f}%")
    
    print("\n4. 💼 職位差異化薪資結構:")
    positions = {
        '美容師': {'base': '28,590', 'overtime': '1,564', 'total': '30,154', 'special': '高標5,000+團體獎金'},
        '護理師': {'base': '28,590', 'overtime': '2,588', 'total': '31,178', 'special': '高標10,000+執照津貼5,000+全勤2,000+團體獎金'},
        '櫃檯': {'base': '28,590', 'overtime': '2,464', 'total': '31,054', 'special': '職等獎金1,946+職務津貼2,000 (無團體獎金)'}
    }
    
    for pos, info in positions.items():
        print(f"   {pos}: 底薪{info['base']} + 加班費{info['overtime']} = {info['total']} + {info['special']}")

if __name__ == "__main__":
    # 執行完整示範
    demo_complete_calculation()
    demo_features()
    
    print("\n" + "="*80)
    print("🎉 Only Beauty 薪資計算系統示範完成!")
    print("📝 執行 python salary_calculator.py 開始正式使用")
    print("="*80)
