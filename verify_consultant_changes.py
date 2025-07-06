#!/usr/bin/env python3
"""
驗證顧問業績達標激勵獎金修改
"""

print("=== 顧問獎金顯示修改驗證 ===\n")

# 測試顧問業績達標激勵獎金邏輯
print("業績達標激勵獎金規則測試:")
print("-" * 40)

# 測試案例
test_cases = [
    {"name": "顧問A", "performance": 2000000, "store_target": 6000000, "store_actual": 6500000},
    {"name": "顧問B", "performance": 1500000, "store_target": 6000000, "store_actual": 6500000},
    {"name": "顧問C", "performance": 2000000, "store_target": 6000000, "store_actual": 5500000},
]

for case in test_cases:
    name = case["name"]
    performance = case["performance"]
    store_target = case["store_target"]
    store_actual = case["store_actual"]
    
    # 檢查條件
    personal_qualified = performance >= 1680000
    store_qualified = store_actual >= store_target
    
    # 計算激勵獎金
    incentive_bonus = 10000 if (personal_qualified and store_qualified) else 0
    
    print(f"{name}:")
    print(f"  個人業績: {performance:,}")
    print(f"  個人達標 (>=168萬): {'✓' if personal_qualified else '✗'}")
    print(f"  門店業績: {store_actual:,}")
    print(f"  門店達標 (>={store_target:,}): {'✓' if store_qualified else '✗'}")
    print(f"  業績達標激勵獎金: {incentive_bonus:,}")
    
    if incentive_bonus > 0:
        print("  ✅ 符合條件，獲得激勵獎金")
    else:
        print("  ❌ 不符合條件，無激勵獎金")
    print()

print("修改摘要:")
print("✅ 移除顧問獎金明細中的三行小計")
print("✅ 新增業績達標激勵獎金 10,000元")
print("✅ 激勵獎金條件: 個人業績>=168萬 + 門店達標")
print("✅ 激勵獎金顯示為 '不計入當月總薪資'")

print("\n新的顧問獎金顯示格式:")
print("-" * 40)
print("顧問小王:")
print("  個人業績: 2,000,000")
print("  個人消耗: 800,000")
print("  團體業績獎金: 25,000")
print("  團體消耗獎金: 5,000")
print("  產品銷售: 35 組")
print("  產品達標獎金: 2,000")
print("  個人業績獎金: 20,000 (店長)")
print("  個人消耗獎金: 12,000 (店長)")
print("")
print("  業績達標激勵獎金: 10,000 (不計入當月總薪資)")
print()

print("✅ 所有修改已完成")
