#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from salary_calculator import OnlyBeautySalaryCalculator

def test_product_sales():
    """測試產品銷售統計功能"""
    calculator = OnlyBeautySalaryCalculator()
    
    # 測試產品銷售統計
    print("=== 測試產品銷售統計 ===")
    
    # 這裡需要您提供實際的Excel檔案路徑
    test_file = input("請輸入測試用的Excel檔案路徑: ").strip()
    
    if test_file:
        # 統計產品銷售
        product_sales = calculator.get_product_sales_statistics(test_file)
        
        if product_sales:
            print(f"\n找到 {len(product_sales)} 個顧問的產品銷售記錄")
            
            # 計算產品達標獎金
            product_bonuses = calculator.calculate_product_bonus(product_sales)
            
            print("\n詳細統計結果:")
            print("=" * 50)
            for consultant, data in product_bonuses.items():
                status = "達標 ✓" if data['qualified'] else "未達標 ✗"
                print(f"{consultant:>8}: {data['sales_count']:>3} 組 → {data['bonus']:>5,}元 ({status})")
            
            # 統計摘要
            total_sales = sum(data['sales_count'] for data in product_bonuses.values())
            total_bonus = sum(data['bonus'] for data in product_bonuses.values())
            qualified_count = sum(1 for data in product_bonuses.values() if data['qualified'])
            
            print("\n摘要:")
            print(f"總產品銷售組數: {total_sales} 組")
            print(f"達標人數: {qualified_count} 人")
            print(f"產品達標獎金總額: {total_bonus:,} 元")
        else:
            print("沒有找到產品銷售記錄")
    else:
        print("未提供檔案路徑，跳過測試")

if __name__ == "__main__":
    test_product_sales()
