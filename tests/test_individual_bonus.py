import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_app"))

import streamlit_app  # noqa: E402


def make_calc():
    return streamlit_app.OnlyBeautySalaryCalculator()


def test_module_imports_and_class_exists():
    c = make_calc()
    assert hasattr(c, "calc_progressive_bonus")


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


def test_full_amount_manager_performance_liao():
    c = make_calc()
    # 廖政翔 業績 2,158,139 店長/全額 × 2.1% = 45,321
    got = c.calc_full_amount_bonus(2158139, c.manager_performance_levels)
    assert round(got) == 45321
