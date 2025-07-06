#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from salary_calculator import OnlyBeautySalaryCalculator

def test_new_logic():
    """測試新的產品達標邏輯"""
    print("=== 測試產品達標獎金邏輯 ===")
    print("規則：")
    print("1. 產品銷售達到30組以上 → 獲得2000元產品達標獎金")
    print("2. 產品銷售未達30組 → 團體業績獎金和團體消耗獎金清零")
    print("3. 只有產品達標的顧問才能獲得團體獎金")
    print()
    
    # 模擬產品銷售數據
    test_product_sales = {
        'K': 45,      # 達標
        'A': 32,      # 達標  
        'B': 25,      # 未達標
        '公司': 28,   # 未達標
        'C': 35       # 達標
    }
    
    calculator = OnlyBeautySalaryCalculator()
    
    # 計算產品達標獎金
    product_bonuses = calculator.calculate_product_bonus(test_product_sales)
    
    print("\n產品達標狀況:")
    print("-" * 40)
    for consultant, data in product_bonuses.items():
        status = "達標 ✓" if data['qualified'] else "未達標 ✗"
        team_bonus_status = "有團體獎金" if data['qualified'] else "團體獎金清零"
        print(f"{consultant}: {data['sales_count']} 組 → {data['bonus']:,}元 ({status}) - {team_bonus_status}")
    
    print("\n說明:")
    print("- K, A, C 產品達標，可獲得團體業績獎金 + 團體消耗獎金 + 產品達標獎金")
    print("- B, 公司 產品未達標，團體業績獎金和團體消耗獎金被清零，只能獲得0元")

if __name__ == "__main__":
    test_new_logic()
