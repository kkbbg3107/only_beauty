#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡化版測試程式 - 直接執行薪資計算邏輯
"""

def simple_test():
    print("=== Only Beauty 薪資計算系統測試 ===")
    
    # 模擬數據
    total_performance = 5000000  # E5
    total_consumption = 4000000  # E7
    
    # 顧問數據 (排除"公司")
    consultants = [
        {"name": "王顧問", "performance": 2000000, "consumption": 1800000},
        {"name": "李顧問", "performance": 1500000, "consumption": 1200000},
        {"name": "張顧問", "performance": 1000000, "consumption": 800000}
    ]
    
    staff_count = 10  # 美容師/護士人數
    
    print(f"總業績: {total_performance:,}")
    print(f"總消耗: {total_consumption:,}")
    print(f"顧問數量: {len(consultants)}")
    print(f"美容師/護士人數: {staff_count}")
    print()
    
    # 業績獎金等級表
    performance_levels = [
        (1800000, 2500000, 0.005),
        (2500001, 4000000, 0.01),
        (4000001, 6000000, 0.025),
        (6000001, 8000000, 0.045)
    ]
    
    # 消耗獎金等級表
    consumption_levels = [
        (0, 1500000, 0.006),
        (1500001, 2500000, 0.01),
        (2500001, float('inf'), 0.015)
    ]
    
    # 計算業績獎金比例
    performance_rate = 0
    for min_val, max_val, rate in performance_levels:
        if min_val <= total_performance <= max_val:
            performance_rate = rate
            break
    
    # 計算消耗獎金比例
    consumption_rate = 0
    for min_val, max_val, rate in consumption_levels:
        if min_val <= total_consumption <= max_val:
            consumption_rate = rate
            break
    
    print(f"業績獎金比例: {performance_rate*100}%")
    print(f"消耗獎金比例: {consumption_rate*100}%")
    print()
    
    # 計算顧問獎金池
    consultant_performance_pool = total_performance * 0.7 * performance_rate
    consultant_consumption_pool = total_consumption * 0.4 * consumption_rate
    
    print(f"顧問業績獎金池: {consultant_performance_pool:,.0f}")
    print(f"顧問消耗獎金池: {consultant_consumption_pool:,.0f}")
    print()
    
    # 計算總顧問業績和消耗
    total_consultant_performance = sum(c["performance"] for c in consultants)
    total_consultant_consumption = sum(c["consumption"] for c in consultants)
    
    print("顧問獎金明細:")
    print("-" * 60)
    for consultant in consultants:
        # 業績獎金分配
        performance_ratio = consultant["performance"] / total_consultant_performance
        performance_bonus = consultant_performance_pool * performance_ratio
        
        # 消耗獎金分配
        consumption_ratio = consultant["consumption"] / total_consultant_consumption
        consumption_bonus = consultant_consumption_pool * consumption_ratio
        
        total_bonus = performance_bonus + consumption_bonus
        
        print(f"{consultant['name']}:")
        print(f"  個人業績: {consultant['performance']:,}")
        print(f"  個人消耗: {consultant['consumption']:,}")
        print(f"  業績獎金: {performance_bonus:,.0f}")
        print(f"  消耗獎金: {consumption_bonus:,.0f}")
        print(f"  總獎金: {total_bonus:,.0f}")
        print()
    
    # 計算美容師/護士獎金
    staff_performance_pool = total_performance * 0.3 * performance_rate
    staff_consumption_pool = total_consumption * 0.6 * consumption_rate
    
    performance_bonus_per_person = staff_performance_pool / staff_count
    consumption_bonus_per_person = staff_consumption_pool / staff_count
    total_bonus_per_person = performance_bonus_per_person + consumption_bonus_per_person
    
    print("美容師/護士獎金:")
    print("-" * 60)
    print(f"總人數: {staff_count}")
    print(f"業績獎金池: {staff_performance_pool:,.0f}")
    print(f"消耗獎金池: {staff_consumption_pool:,.0f}")
    print(f"每人業績獎金: {performance_bonus_per_person:,.0f}")
    print(f"每人消耗獎金: {consumption_bonus_per_person:,.0f}")
    print(f"每人總獎金: {total_bonus_per_person:,.0f}")

if __name__ == "__main__":
    simple_test()
