# 門市薪資系統 — 顧問個人獎金「每人客製」設計

日期:2026-06-13
範圍:只改 `web_app/streamlit_app.py`(線上 Streamlit app)。

## 背景與目標

現有「個人業績/個人消耗」獎金的算法很死:
- 角色只用 `name == self.manager_name` 判斷 → 不是店長就一律當「顧問」。
- 只有「階梯制(累進)」一種算法。

需求(來自規則文件 #3、#4):個人業績與個人消耗要支援
1. 三種角色級距:**店長 / 副店長(新增) / 顧問**
2. 兩種計算方式:**階梯制(現有) / 全額抽成(新增)**
3. 兩者可獨立組合,**每個人在網頁上各自指定**。

## 不在範圍內(維持不變)

- 團體業績級距(已含 800 萬以上,正確)。
- 團體消耗級距(正確)。
- 美容師 / 護理師 / 櫃檯 / 高標達標 / 產品達標 / VIP 等所有其他邏輯。
- CLI 版 `salary_calculator.py`(不動)。
- 醫師薪資系統(本次完全不碰)。

## 名詞定義

- **階梯制(progressive)**:現有 `calc_progressive_bonus`,逐級累進。
- **全額抽成(full amount)**:整筆金額 × 所落級距的單一費率。
  - 例:店長 業績 3,407,468 落在最高級距 → 3,407,468 × 2.10% = 71,557。
  - 同一個人的「業績」與「消耗」套用同一個 mode。

## 級距表

### 既有(不變)
- 店長業績:≤100萬 0.8% | 100–160萬 1.0% | 160–210萬 1.6% | 210萬+ 2.1%
- 顧問業績:≤60萬 0.4% | 60–120萬 0.7% | 120–170萬 0.8% | 170萬+ 1.2%
- 店長消耗:≤50萬 1.2% | 50–100萬 1.5% | 100萬+ 2.4%
- 顧問消耗:≤30萬 0.6% | 30–60萬 0.8% | 60萬+ 1.2%

### 新增:副店長
```python
self.deputy_performance_levels = [
    (0, 800000, 0.005),
    (800001, 1400000, 0.008),
    (1400001, 1900000, 0.012),
    (1900001, float('inf'), 0.016),
]
self.deputy_consumption_levels = [
    (0, 400000, 0.010),
    (400001, 900000, 0.012),
    (900001, float('inf'), 0.018),
]
```

## 全額抽成計算

```python
def calc_full_amount_bonus(self, amount, levels):
    """整筆金額 × 所落最高級距的單一費率"""
    selected_rate = levels[0][2]
    for min_val, max_val, rate in levels:
        if amount > min_val:
            selected_rate = rate
    return amount * selected_rate
```

驗證(取自規則文件範例):
- 張嘉如 店長/全額:3,407,468 × 2.1% = 71,557 ✓
- 廖政翔 店長/全額:2,158,139 × 2.1% = 45,321 ✓
- 施宜廷 副店長/全額:2,840,931 × 1.6% = 45,455 ✓
- 張嘉如 消耗 店長/全額:2,758,058 × 2.4% = 66,193 ✓
- 劉芸芸 副店長/階梯:業績 2,733,748 → 累進 28,140 ✓
- 吳翊菱 副店長/階梯:消耗 2,467,383 → 累進 38,213 ✓

## 核心重構:`calculate_individual_bonus`

新增參數 `role_config: Dict[str, {'role','mode'}]`。

```python
def calculate_individual_bonus(self, consultant_bonuses, high_target_amount=None, role_config=None):
    role_config = role_config or {}
    ...
    for name, bonus_data in consultant_bonuses.items():
        cfg  = role_config.get(name, {})
        role = cfg.get('role') or ('店長' if name == self.manager_name else '顧問')
        mode = cfg.get('mode', '階梯')

        if role == '店長':
            perf_levels, cons_levels = self.manager_performance_levels, self.manager_consumption_levels
        elif role == '副店長':
            perf_levels, cons_levels = self.deputy_performance_levels, self.deputy_consumption_levels
        else:
            perf_levels, cons_levels = self.consultant_performance_levels, self.consultant_consumption_levels

        calc = self.calc_full_amount_bonus if mode == '全額' else self.calc_progressive_bonus
        individual_performance_bonus  = calc(performance, perf_levels)
        individual_consumption_bonus  = calc(consumption, cons_levels)
        # performance_incentive_bonus 邏輯不變
        individual_bonuses[name] = {
            'role': role, 'mode': mode,
            'individual_performance_bonus': individual_performance_bonus,
            'individual_consumption_bonus': individual_consumption_bonus,
            'performance_incentive_bonus': performance_incentive_bonus,
            'individual_total': individual_performance_bonus + individual_consumption_bonus,
        }
```

## UI 流程(每人設定區)

頁面順序調整為:
1. 步驟1:上傳 Excel(不變)
2. 步驟2:基本資料設定(人數、店長名稱、高標)(不變)
3. **步驟3(新增):顧問角色與計算方式** — 上傳後自動列出 `get_consultants_data()` 的所有顧問名字,每人兩個 `st.selectbox`:
   - 角色:店長 / 副店長 / 顧問(預設:名字 == 店長名 → 店長,否則顧問)
   - 方式:階梯 / 全額(預設:階梯)
   - 選擇存入 `st.session_state['role_config']`。
4. 步驟4:開始計算 — 把 `role_config` 傳入 `calculate_individual_bonus`。
5. 步驟5:結果 — 顯示每人的角色與方式以利核對。

### 預設值(向後相容)
不做任何手動調整 = 全部「(店長例外的)顧問 + 階梯制」,輸出與現況一致。
設定不跨月保留(只存在 session,重整即清空)。

## 結果顯示

個人獎金區塊每人多顯示「角色 / 方式」標籤(例:`副店長・全額`),其餘格式不變。

## 測試方式

用規則文件的範例數字做為驗收案例(上面「驗證」清單),逐一比對:
- 全額:店長/副店長 各一例(業績+消耗)。
- 階梯:副店長 各一例(業績+消耗)、顧問維持原結果。
- 預設值:不設定時,既有顧問/店長輸出與改動前一致(回歸測試)。
