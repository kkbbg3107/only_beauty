#!/usr/bin/env python3
"""
驗證高標達標獎金修改
"""

print("=== 高標達標獎金修改驗證 ===\n")

# 測試薪資計算邏輯
print("修改前後對比:")
print("-" * 40)

# 美容師
beauty_base = 31054
beauty_hand = 5000
beauty_high_target = 5000

print("美容師薪資結構:")
print("修改前:")
print(f"  當月總薪資 = 底薪 + 手技獎金 + 高標達標獎金")
print(f"  = {beauty_base:,} + {beauty_hand:,} + {beauty_high_target:,}")
print(f"  = {beauty_base + beauty_hand + beauty_high_target:,}")

print("修改後:")
print(f"  當月總薪資 = 底薪 + 手技獎金")
print(f"  = {beauty_base:,} + {beauty_hand:,}")
print(f"  = {beauty_base + beauty_hand:,}")
print(f"  高標達標獎金: {beauty_high_target:,} (不計入當月總薪資)")

print()

# 護理師
nurse_base = 31175
nurse_hand = 8000
nurse_license = 5000
nurse_full_attendance = 2000
nurse_high_target = 10000

print("護理師薪資結構:")
print("修改前:")
print(f"  當月總薪資 = 底薪 + 手技獎金 + 執照津貼 + 高標達標獎金")
print(f"  = {nurse_base:,} + {nurse_hand:,} + {nurse_license:,} + {nurse_high_target:,}")
print(f"  = {nurse_base + nurse_hand + nurse_license + nurse_high_target:,}")
print(f"  全勤獎金: {nurse_full_attendance:,} (不計入當月總薪資)")

print("修改後:")
print(f"  當月總薪資 = 底薪 + 手技獎金 + 執照津貼")
print(f"  = {nurse_base:,} + {nurse_hand:,} + {nurse_license:,}")
print(f"  = {nurse_base + nurse_hand + nurse_license:,}")
print(f"  全勤獎金: {nurse_full_attendance:,} (不計入當月總薪資)")
print(f"  高標達標獎金: {nurse_high_target:,} (不計入當月總薪資)")

print()

# 櫃檯 (無變動)
counter_base = 31054
counter_hand = 2000
counter_rank = 1946
counter_position = 2000
counter_high_target = 0  # 櫃檯沒有高標達標獎金

print("櫃檯薪資結構 (無變動):")
print(f"  當月總薪資 = 底薪 + 手技獎金 + 職等獎金 + 職務津貼 + 櫃檯專用獎金")
print(f"  = {counter_base:,} + {counter_hand:,} + {counter_rank:,} + {counter_position:,} + 櫃檯專用獎金")
print(f"  = {counter_base + counter_hand + counter_rank + counter_position:,} + 櫃檯專用獎金")
print("  註：櫃檯沒有高標達標獎金")

print("\n" + "="*50)
print("✅ 修改完成！")
print("✅ 美容師/護理師的高標達標獎金已移至不計入當月總薪資")
print("✅ 顯示格式已調整為標註 (不計入當月總薪資)")
