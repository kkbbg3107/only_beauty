#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from salary_calculator import OnlyBeautySalaryCalculator

def test_individual_bonus():
    """測試個人獎金計算"""
    print("=== 測試個人獎金計算 ===")
    
    calculator = OnlyBeautySalaryCalculator()
    
    # 設定店長
    calculator.manager_name = "K"
    
    # 模擬顧問數據
    mock_consultant_bonuses = {
        'K': {
            'personal_performance': 4808039,
            'personal_consumption': 1200000,
            'performance_bonus': 27091,
            'consumption_bonus': 6298,
            'total_bonus': 33389,
            'product_qualified': True
        },
        'A': {
            'personal_performance': 1500000,
            'personal_consumption': 800000,
            'performance_bonus': 15000,
            'consumption_bonus': 3000,
            'total_bonus': 18000,
            'product_qualified': True
        }
    }
    
    # 計算個人獎金
    individual_bonuses = calculator.calculate_individual_bonus(mock_consultant_bonuses)
    
    print("\n個人獎金明細:")
    print("-" * 50)
    
    for name, data in individual_bonuses.items():
        print(f"{name} ({data['role']}):")
        print(f"  個人業績獎金: {data['individual_performance_bonus']:,.0f}")
        print(f"  個人消耗獎金: {data['individual_consumption_bonus']:,.0f}")
        print(f"  個人獎金總計: {data['individual_total']:,.0f}")
        print()
    
    print("級距說明:")
    print("店長業績獎金級距:")
    print("  0-1,000,000: 0.8%")
    print("  1,000,001-1,600,000: 1.0%") 
    print("  1,600,001-2,100,000: 1.6%")
    print("  2,100,001以上: 2.1%")
    print()
    print("顧問業績獎金級距:")
    print("  0-600,000: 0.4%")
    print("  600,001-1,200,000: 0.7%")
    print("  1,200,001-1,700,000: 0.8%")
    print("  1,700,001以上: 1.2%")

if __name__ == "__main__":
    test_individual_bonus()
