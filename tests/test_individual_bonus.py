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
