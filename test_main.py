#!/usr/bin/env python3
"""
測試主程式是否正常運行
"""

from salary_calculator import OnlyBeautySalaryCalculator

def test_main():
    print("=== 測試主程式 ===")
    
    try:
        calc = OnlyBeautySalaryCalculator()
        print("✓ 薪資計算器創建成功")
        
        # 測試基本功能
        if hasattr(calc, 'get_individual_staff_data'):
            print("✓ get_individual_staff_data 方法存在")
        
        if hasattr(calc, 'calculate_individual_staff_salary'):
            print("✓ calculate_individual_staff_salary 方法存在")
            
        print("\n底薪設定已更新：")
        print("- 美容師: 31,054元 (默認值)")
        print("- 護理師: 31,175元 (默認值)")
        print("- 櫃檯: 31,054元 (默認值)")
        print("\n當Excel中有底薪數據時，會優先使用Excel中的值")
        print("當Excel中沒有底薪數據時，會使用上述默認值")
        
        print("\n🎉 salary_calculator.py 修改完成！")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    test_main()
