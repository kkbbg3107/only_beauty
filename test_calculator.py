#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from salary_calculator import OnlyBeautySalaryCalculator

def test_calculator():
    """測試薪資計算程式"""
    
    calculator = OnlyBeautySalaryCalculator()
    
    # 載入測試Excel檔案
    excel_path = "test_salary_data.xlsx"
    if not calculator.load_excel(excel_path):
        print("載入測試檔案失敗")
        return
    
    # 設定美容師/護士人數
    calculator.staff_count = 10
    
    # 計算獎金
    print("\n開始計算獎金...")
    consultant_bonuses = calculator.calculate_consultant_bonus()
    staff_bonuses = calculator.calculate_staff_bonus()
    
    # 顯示結果
    calculator.display_results(consultant_bonuses, staff_bonuses)

if __name__ == "__main__":
    test_calculator()
