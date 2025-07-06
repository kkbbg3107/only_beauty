#!/usr/bin/env python3
"""
快速測試底薪設定
"""

import pandas as pd
from salary_calculator import OnlyBeautySalaryCalculator

def quick_test():
    print("測試底薪設定...")
    
    # 創建測試數據 - 只有姓名，沒有底薪數據
    data = {}
    for i in range(20):
        data[i] = [None] * 25
    
    # 只設定姓名，不設定底薪，測試默認值
    data[8][10] = "美容師測試"    # K9: 美容師姓名
    data[8][16] = "護理師測試"    # Q9: 護理師姓名
    data[11][16] = "櫃檯測試"     # Q12: 櫃檯姓名
    
    calc = OnlyBeautySalaryCalculator()
    calc.excel_data = pd.DataFrame.from_dict(data, orient='index')
    
    staff_data = calc.get_individual_staff_data()
    
    for staff in staff_data:
        print(f"{staff['name']} ({staff['position']}): 底薪 {staff['base_salary']:,}")
    
    print("\n預期結果:")
    print("美容師: 31,054")
    print("護理師: 31,175") 
    print("櫃檯: 31,054")

if __name__ == "__main__":
    quick_test()
