#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from salary_calculator import OnlyBeautySalaryCalculator

def test_fixed_calculation():
    """測試修正後的計算，確保不重複顯示階段"""
    print("=== 測試修正後的計算 ===")
    
    calculator = OnlyBeautySalaryCalculator()
    calculator.staff_count = 3
    
    # 模擬產品銷售數據 - 全部未達標
    test_product_sales = {'K': 25, 'A': 20}
    product_bonuses = calculator.calculate_product_bonus(test_product_sales)
    
    # 模擬Excel數據
    import pandas as pd
    import numpy as np
    
    # 創建模擬的Excel數據
    mock_data = pd.DataFrame(index=range(20), columns=range(20))
    mock_data.iloc[4, 4] = 4808039  # E5 總業績
    mock_data.iloc[6, 4] = 4871854  # E7 總消耗
    mock_data.iloc[8, 0] = 'K'      # A9 顧問名稱
    mock_data.iloc[8, 2] = 4808039  # C9 個人業績
    mock_data.iloc[8, 6] = 1200000  # G9 個人消耗
    mock_data.iloc[9, 0] = 'A'      # A10 顧問名稱
    mock_data.iloc[9, 2] = 1500000  # C10 個人業績
    mock_data.iloc[9, 6] = 800000   # G10 個人消耗
    
    calculator.excel_data = mock_data
    
    print("開始計算團體獎金...")
    consultant_bonuses, perf_pool, cons_pool = calculator.calculate_consultant_bonus(product_bonuses)
    print(f"\n顧問業績獎金池: {perf_pool:,.0f}")
    print(f"顧問消耗獎金池: {cons_pool:,.0f}")
    
    print("\n計算美容師/護士獎金...")
    staff_bonuses = calculator.calculate_staff_bonus(perf_pool, cons_pool)
    
    print(f"\n美容師/護士業績獎金池: {staff_bonuses['performance_pool']:,.0f}")
    print(f"美容師/護士消耗獎金池: {staff_bonuses['consumption_pool']:,.0f}")
    print(f"每人總獎金: {staff_bonuses['total_bonus_per_person']:,.0f}")
    
    print("\n✅ 測試完成 - 階段計算應該只顯示一次")

if __name__ == "__main__":
    test_fixed_calculation()
