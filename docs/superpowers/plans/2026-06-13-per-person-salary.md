# 門市薪資「每人客製個人獎金」Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 讓 Streamlit 門市薪資系統的「個人業績/個人消耗」獎金支援三種角色(店長/副店長/顧問)與兩種算法(階梯/全額),且每位顧問可在網頁上各自指定。

**Architecture:** 在 `OnlyBeautySalaryCalculator` 內新增「副店長」級距表與 `calc_full_amount_bonus`(全額)方法;重構 `calculate_individual_bonus` 接受 `role_config` 字典(name → {role, mode});在 `main()` 上傳後新增一個「角色與計算方式」設定區,選擇存入 `st.session_state` 並於計算時帶入。預設「顧問+階梯」=現況,向後相容。

**Tech Stack:** Python, Streamlit 1.50, pandas, pytest(新加入做單元測試)。所有指令用 repo 內 `venv/`。

---

## 檔案結構

- Modify: `web_app/streamlit_app.py`
  - `__init__`:新增 `deputy_performance_levels`、`deputy_consumption_levels`
  - 新增方法 `calc_full_amount_bonus`
  - 重構 `calculate_individual_bonus` 簽章與內部選表/選算法邏輯
  - `main()`:新增「步驟3:顧問角色與計算方式」UI,並把 `role_config` 傳入計算
  - 結果顯示:每人加上「角色・方式」標籤
- Create: `tests/test_individual_bonus.py`(pytest 單元測試)
- Modify: `web_app/requirements.txt`(加 `pytest`,供本機測試)

**測試前置**:所有測試用 `venv/` 的 python,並在測試檔頂端把 `web_app/` 加入 `sys.path`、關閉 streamlit 警告。

---

## Task 1: 安裝 pytest 並建立測試骨架

**Files:**
- Create: `tests/test_individual_bonus.py`
- Modify: `web_app/requirements.txt`

- [ ] **Step 1: 安裝 pytest 到 venv**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/pip install pytest
```
Expected: 成功安裝 pytest(出現 `Successfully installed pytest-...`)。

- [ ] **Step 2: 把 pytest 記到 requirements**

在 `web_app/requirements.txt` 最後一行加入:
```
pytest
```

- [ ] **Step 3: 建立測試檔骨架(含 import 與冒煙測試)**

Create `tests/test_individual_bonus.py`:
```python
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_app"))

import streamlit_app  # noqa: E402


def make_calc():
    return streamlit_app.OnlyBeautySalaryCalculator()


def test_module_imports_and_class_exists():
    c = make_calc()
    assert hasattr(c, "calc_progressive_bonus")
```

- [ ] **Step 4: 跑測試確認骨架通過**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: `test_module_imports_and_class_exists PASSED`。

- [ ] **Step 5: Commit**

```bash
cd /Users/ben_kuo/only_beauty
git add tests/test_individual_bonus.py web_app/requirements.txt
git commit -m "test: add pytest scaffold for individual bonus"
```

---

## Task 2: 新增副店長級距表 + 全額抽成方法

**Files:**
- Modify: `web_app/streamlit_app.py`(`__init__` 約 84–109 行區塊;在 `calc_progressive_bonus` 附近新增方法)
- Test: `tests/test_individual_bonus.py`

- [ ] **Step 1: 寫失敗測試(副店長表 + 全額計算)**

在 `tests/test_individual_bonus.py` 末端加入:
```python
def test_deputy_levels_exist():
    c = make_calc()
    assert c.deputy_performance_levels == [
        (0, 800000, 0.005),
        (800001, 1400000, 0.008),
        (1400001, 1900000, 0.012),
        (1900001, float("inf"), 0.016),
    ]
    assert c.deputy_consumption_levels == [
        (0, 400000, 0.010),
        (400001, 900000, 0.012),
        (900001, float("inf"), 0.018),
    ]


def test_full_amount_manager_performance():
    c = make_calc()
    # 張嘉如 業績 3,407,468 × 2.1% = 71,557
    got = c.calc_full_amount_bonus(3407468, c.manager_performance_levels)
    assert round(got) == 71557


def test_full_amount_deputy_performance():
    c = make_calc()
    # 施宜廷 業績 2,840,931 × 1.6% = 45,455
    got = c.calc_full_amount_bonus(2840931, c.deputy_performance_levels)
    assert round(got) == 45455


def test_full_amount_manager_consumption():
    c = make_calc()
    # 張嘉如 消耗 2,758,058 × 2.4% = 66,193
    got = c.calc_full_amount_bonus(2758058, c.manager_consumption_levels)
    assert round(got) == 66193


def test_progressive_deputy_performance():
    c = make_calc()
    # 劉芸芸 業績 2,733,748 階梯 → 28,140
    got = c.calc_progressive_bonus(2733748, c.deputy_performance_levels)
    assert round(got) == 28140


def test_progressive_deputy_consumption():
    c = make_calc()
    # 吳翊菱 消耗 2,467,383 階梯 → 38,213
    got = c.calc_progressive_bonus(2467383, c.deputy_consumption_levels)
    assert round(got) == 38213
```

- [ ] **Step 2: 跑測試確認失敗**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 新增測試 FAIL(`AttributeError: ... deputy_performance_levels` / `calc_full_amount_bonus`)。

- [ ] **Step 3: 在 `__init__` 新增副店長兩張表**

在 `web_app/streamlit_app.py` 的 `self.consultant_consumption_levels = [...]` 區塊(約 105–109 行)之後、`# 高標達標獎金設定` 之前,插入:
```python
        # 副店長 個人業績 / 個人消耗 等級表
        self.deputy_performance_levels = [
            (0, 800000, 0.005),
            (800001, 1400000, 0.008),
            (1400001, 1900000, 0.012),
            (1900001, float('inf'), 0.016)
        ]

        self.deputy_consumption_levels = [
            (0, 400000, 0.010),
            (400001, 900000, 0.012),
            (900001, float('inf'), 0.018)
        ]
```

- [ ] **Step 4: 新增 `calc_full_amount_bonus` 方法**

在 `calc_progressive_bonus` 方法(`def calc_progressive_bonus(self, amount: float, levels: List[tuple]) -> float:`)的正下方,新增:
```python
    def calc_full_amount_bonus(self, amount: float, levels: List[tuple]) -> float:
        """全額抽成:整筆金額 × 所落最高級距的單一費率"""
        selected_rate = levels[0][2]
        for min_val, max_val, rate in levels:
            if amount > min_val:
                selected_rate = rate
        return amount * selected_rate
```

- [ ] **Step 5: 跑測試確認通過**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 全部 PASSED(含 6 個新測試)。

- [ ] **Step 6: Commit**

```bash
cd /Users/ben_kuo/only_beauty
git add web_app/streamlit_app.py tests/test_individual_bonus.py
git commit -m "feat: add deputy tier tables and full-amount bonus calc"
```

---

## Task 3: 重構 `calculate_individual_bonus` 接受 role_config

**Files:**
- Modify: `web_app/streamlit_app.py`(`calculate_individual_bonus`,約 379–416 行)
- Test: `tests/test_individual_bonus.py`

- [ ] **Step 1: 寫失敗測試(角色+方式組合)**

在 `tests/test_individual_bonus.py` 末端加入:
```python
import pandas as pd


def _calc_with_data():
    c = make_calc()
    # calculate_individual_bonus 會讀 excel_data.iloc[4,4](總業績),給個 10x10 的 0
    c.excel_data = pd.DataFrame([[0] * 10 for _ in range(10)])
    return c


def test_individual_bonus_manager_full_amount():
    c = _calc_with_data()
    consultant_bonuses = {
        "張嘉如": {"personal_performance": 3407468, "personal_consumption": 2758058}
    }
    role_config = {"張嘉如": {"role": "店長", "mode": "全額"}}
    out = c.calculate_individual_bonus(consultant_bonuses, None, role_config)
    assert out["張嘉如"]["role"] == "店長"
    assert out["張嘉如"]["mode"] == "全額"
    assert round(out["張嘉如"]["individual_performance_bonus"]) == 71557
    assert round(out["張嘉如"]["individual_consumption_bonus"]) == 66193


def test_individual_bonus_deputy_progressive():
    c = _calc_with_data()
    consultant_bonuses = {
        "劉芸芸": {"personal_performance": 2733748, "personal_consumption": 2175723}
    }
    role_config = {"劉芸芸": {"role": "副店長", "mode": "階梯"}}
    out = c.calculate_individual_bonus(consultant_bonuses, None, role_config)
    assert out["劉芸芸"]["role"] == "副店長"
    assert round(out["劉芸芸"]["individual_performance_bonus"]) == 28140
    # 消耗 2,175,723 階梯 → 32,963
    assert round(out["劉芸芸"]["individual_consumption_bonus"]) == 32963


def test_individual_bonus_default_is_consultant_progressive():
    c = _calc_with_data()
    consultant_bonuses = {
        "蕭茹心": {"personal_performance": 1532495, "personal_consumption": 977128}
    }
    # 不給 role_config → 預設 顧問 + 階梯,結果須等同現況
    out = c.calculate_individual_bonus(consultant_bonuses, None)
    assert out["蕭茹心"]["role"] == "顧問"
    assert out["蕭茹心"]["mode"] == "階梯"
    assert round(out["蕭茹心"]["individual_performance_bonus"]) == 9260
    assert round(out["蕭茹心"]["individual_consumption_bonus"]) == 8726


def test_individual_bonus_default_manager_name():
    c = _calc_with_data()
    c.manager_name = "店長甲"
    consultant_bonuses = {
        "店長甲": {"personal_performance": 3407468, "personal_consumption": 2758058}
    }
    # 沒給 role_config,但名字==店長名 → 預設店長 + 階梯
    out = c.calculate_individual_bonus(consultant_bonuses, None)
    assert out["店長甲"]["role"] == "店長"
    assert out["店長甲"]["mode"] == "階梯"
```

- [ ] **Step 2: 跑測試確認失敗**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 4 個新測試 FAIL(目前簽章不收 `role_config`、輸出無 `mode`、副店長未支援)。

- [ ] **Step 3: 重構 `calculate_individual_bonus`**

把 `web_app/streamlit_app.py` 的整個 `calculate_individual_bonus`(從 `def calculate_individual_bonus(self, consultant_bonuses: Dict, high_target_amount: float = None) -> Dict:` 到 `return individual_bonuses`)替換為:
```python
    def calculate_individual_bonus(self, consultant_bonuses: Dict, high_target_amount: float = None, role_config: Dict = None) -> Dict:
        """計算個人業績獎金和個人消耗獎金(支援角色與計算方式客製)"""
        individual_bonuses = {}
        role_config = role_config or {}

        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0
        store_achieved = high_target_amount and total_performance >= high_target_amount

        for name, bonus_data in consultant_bonuses.items():
            performance = bonus_data['personal_performance']
            consumption = bonus_data['personal_consumption']

            cfg = role_config.get(name, {})
            role = cfg.get('role') or ('店長' if name == self.manager_name else '顧問')
            mode = cfg.get('mode', '階梯')

            if role == '店長':
                perf_levels = self.manager_performance_levels
                cons_levels = self.manager_consumption_levels
            elif role == '副店長':
                perf_levels = self.deputy_performance_levels
                cons_levels = self.deputy_consumption_levels
            else:
                perf_levels = self.consultant_performance_levels
                cons_levels = self.consultant_consumption_levels

            calc = self.calc_full_amount_bonus if mode == '全額' else self.calc_progressive_bonus
            individual_performance_bonus = calc(performance, perf_levels)
            individual_consumption_bonus = calc(consumption, cons_levels)

            performance_incentive_bonus = 0
            if performance >= 1680000 and store_achieved:
                performance_incentive_bonus = 10000

            individual_bonuses[name] = {
                'role': role,
                'mode': mode,
                'individual_performance_bonus': individual_performance_bonus,
                'individual_consumption_bonus': individual_consumption_bonus,
                'performance_incentive_bonus': performance_incentive_bonus,
                'individual_total': individual_performance_bonus + individual_consumption_bonus
            }

        return individual_bonuses
```

- [ ] **Step 4: 跑測試確認通過**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 全部 PASSED。

- [ ] **Step 5: Commit**

```bash
cd /Users/ben_kuo/only_beauty
git add web_app/streamlit_app.py tests/test_individual_bonus.py
git commit -m "feat: support per-person role and calc mode in individual bonus"
```

---

## Task 4: 新增「角色與計算方式」UI 並接線

**Files:**
- Modify: `web_app/streamlit_app.py`(`main()`:步驟2 之後新增區塊;步驟3 計算處傳入 `role_config`)

說明:Streamlit 互動 UI 不做自動化測試,改用「程式可被匯入 + 計算管線吃得到 role_config」的冒煙驗證 + 手動檢查清單。

- [ ] **Step 1: 在基本資料設定之後、開始計算之前,新增設定區**

找到 `main()` 裡基本資料設定區塊結尾(`high_target = st.number_input(...)` 之後、`st.markdown('<div class="step-header">🔢 步驟 3: 開始計算...` 之前)。在兩者之間插入:
```python
        # 步驟 2.5: 顧問角色與計算方式
        st.markdown("---")
        st.markdown('<div class="step-header">🧑‍💼 步驟 3: 顧問角色與計算方式</div>', unsafe_allow_html=True)
        st.caption("預設「顧問・階梯」。需要的人改成 店長/副店長 或 全額。")

        consultants = st.session_state.calculator.get_consultants_data()
        role_config = {}
        if consultants:
            for c in consultants:
                cname = str(c['name']).strip()
                col_a, col_b, col_c = st.columns([2, 2, 2])
                with col_a:
                    st.write(cname)
                default_role = '店長' if (manager_name and cname == manager_name.strip()) else '顧問'
                with col_b:
                    role = st.selectbox(
                        "角色", ['顧問', '副店長', '店長'],
                        index=['顧問', '副店長', '店長'].index(default_role),
                        key=f"role_{cname}"
                    )
                with col_c:
                    mode = st.selectbox(
                        "計算方式", ['階梯', '全額'],
                        index=0,
                        key=f"mode_{cname}"
                    )
                role_config[cname] = {'role': role, 'mode': mode}
        else:
            st.info("上傳的 Excel 尚未讀到顧問名單。")
        st.session_state.role_config = role_config
```
> 註:`get_consultants_data()` 需要 `excel_data`,上傳成功後已載入,故此處可呼叫。

- [ ] **Step 2: 計算時把 role_config 傳入**

在 `main()` 的計算區塊找到這行:
```python
                        individual_bonuses = st.session_state.calculator.calculate_individual_bonus(consultant_bonuses, high_target_amount)
```
改為:
```python
                        individual_bonuses = st.session_state.calculator.calculate_individual_bonus(
                            consultant_bonuses,
                            high_target_amount,
                            st.session_state.get('role_config')
                        )
```

- [ ] **Step 3: 冒煙驗證(模組可匯入、無語法錯誤)**

Run:
```bash
cd /Users/ben_kuo/only_beauty/web_app && ../venv/bin/python -c "import warnings; warnings.filterwarnings('ignore'); import streamlit_app; print('import OK')" 2>&1 | tail -1
```
Expected: `import OK`(無 SyntaxError / IndentationError)。

- [ ] **Step 4: 回歸測試(確保邏輯層仍綠)**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 全部 PASSED。

- [ ] **Step 5: 手動檢查清單(由使用者執行)**

啟動:
```bash
cd /Users/ben_kuo/only_beauty/web_app && ../venv/bin/streamlit run streamlit_app.py
```
檢查:
1. 上傳 Excel 後出現「步驟3:顧問角色與計算方式」,每位顧問各一列、兩個下拉。
2. 預設皆為「顧問・階梯」;若有填店長名稱,該人預設「店長」。
3. 把某人改成「店長・全額」,按開始計算,結果該人個人業績獎金 = 整筆業績×最高級距費率。
4. 不改任何人時,結果與改動前一致。

- [ ] **Step 6: Commit**

```bash
cd /Users/ben_kuo/only_beauty
git add web_app/streamlit_app.py
git commit -m "feat: add per-consultant role/mode UI in Streamlit app"
```

---

## Task 5: 結果顯示加上「角色・方式」標籤

**Files:**
- Modify: `web_app/streamlit_app.py`(個人獎金結果顯示處)

- [ ] **Step 1: 確認目前個人獎金標題是寫死的**

Run:
```bash
cd /Users/ben_kuo/only_beauty && grep -n "個人獎金（累進制）" web_app/streamlit_app.py
```
Expected: 命中一行(約 781 行):`st.markdown("#### 個人獎金（累進制）")`。此標題寫死,要改成依角色/方式動態顯示。

- [ ] **Step 2: 把寫死標題改成動態「角色・方式」**

把 `web_app/streamlit_app.py` 的這行:
```python
                            st.markdown("#### 個人獎金（累進制）")
```
改為:
```python
                            _role = individual_data.get('role', '顧問')
                            _mode = individual_data.get('mode', '階梯')
                            st.markdown(f"#### 個人獎金（{_role}・{_mode}）")
```
> 縮排需與原行一致(在 `with st.container()` → `if ...individual_bonuses` 區塊內,即原行的相同層級)。

- [ ] **Step 3: 冒煙驗證**

Run:
```bash
cd /Users/ben_kuo/only_beauty/web_app && ../venv/bin/python -c "import warnings; warnings.filterwarnings('ignore'); import streamlit_app; print('import OK')" 2>&1 | tail -1
```
Expected: `import OK`。

- [ ] **Step 4: 回歸測試**

Run:
```bash
cd /Users/ben_kuo/only_beauty && venv/bin/python -m pytest tests/test_individual_bonus.py -v
```
Expected: 全部 PASSED。

- [ ] **Step 5: Commit**

```bash
cd /Users/ben_kuo/only_beauty
git add web_app/streamlit_app.py
git commit -m "feat: show role and calc mode in individual bonus results"
```

---

## 驗收對照(來自規則文件範例)

| 人 | 角色/方式 | 項目 | 數字 | 期望 |
|---|---|---|---|---|
| 張嘉如 | 店長/全額 | 業績 3,407,468 | ×2.1% | 71,557 |
| 廖政翔 | 店長/全額 | 業績 2,158,139 | ×2.1% | 45,321 |
| 施宜廷 | 副店長/全額 | 業績 2,840,931 | ×1.6% | 45,455 |
| 張嘉如 | 店長/全額 | 消耗 2,758,058 | ×2.4% | 66,193 |
| 劉芸芸 | 副店長/階梯 | 業績 2,733,748 | 累進 | 28,140 |
| 劉芸芸 | 副店長/階梯 | 消耗 2,175,723 | 累進 | 32,963 |
| 吳翊菱 | 副店長/階梯 | 消耗 2,467,383 | 累進 | 38,213 |
| 蕭茹心 | 顧問/階梯(預設) | 業績 1,532,495 | 累進 | 9,260 |
| 蕭茹心 | 顧問/階梯(預設) | 消耗 977,128 | 累進 | 8,726 |
