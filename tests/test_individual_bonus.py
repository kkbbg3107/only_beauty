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
