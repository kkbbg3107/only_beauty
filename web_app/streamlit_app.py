import streamlit as st
import pandas as pd
import os
import tempfile
import traceback
from typing import Dict, List
import json

# 設定頁面配置
st.set_page_config(
    page_title="Only Beauty 薪資計算系統",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4a5568;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    .result-card {
        background-color: #f7fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .highlight-number {
        font-size: 1.2rem;
        font-weight: bold;
        color: #667eea;
    }
    .success-message {
        background-color: #c6f6d5;
        color: #22543d;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #9ae6b4;
    }
    .error-message {
        background-color: #fed7d7;
        color: #742a2a;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #fc8181;
    }
</style>
""", unsafe_allow_html=True)

class OnlyBeautySalaryCalculator:
    """薪資計算器 - Streamlit版"""

    def __init__(self):
        # 團體業績獎金等級表
        self.performance_bonus_levels = [
            (1800000, 2500000, 0.005),
            (2500001, 4000000, 0.01),
            (4000001, 6000000, 0.025),
            (6000001, 8000000, 0.045)
        ]

        # 團體消耗獎金等級表
        self.consumption_bonus_levels = [
            (0, 1500000, 0.006),
            (1500001, 2500000, 0.01),
            (2500001, float('inf'), 0.015)
        ]

        # 個人業績獎金等級表
        self.manager_performance_levels = [
            (0, 1000000, 0.008),
            (1000001, 1600000, 0.01),
            (1600001, 2100000, 0.016),
            (2100001, float('inf'), 0.021)
        ]

        self.consultant_performance_levels = [
            (0, 600000, 0.004),
            (600001, 1200000, 0.007),
            (1200001, 1700000, 0.008),
            (1700001, float('inf'), 0.012)
        ]

        # 個人消耗獎金等級表
        self.manager_consumption_levels = [
            (0, 500000, 0.012),
            (500001, 1000000, 0.015),
            (1000001, float('inf'), 0.024)
        ]

        self.consultant_consumption_levels = [
            (0, 300000, 0.006),
            (300001, 600000, 0.008),
            (600001, float('inf'), 0.012)
        ]

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

        # 高標達標獎金設定
        self.high_target_bonuses = {
            '美容師': 5000,
            '護理師': 10000
        }

        self.excel_data = None
        self.consultant_count = 0
        self.staff_count = 0
        self.manager_name = None

    def load_excel_from_bytes(self, file_bytes) -> bool:
        """從檔案位元組載入Excel"""
        try:
            # 使用臨時檔案
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name

            # 讀取所有工作表名稱
            xl_file = pd.ExcelFile(tmp_file_path)
            sheet_names = xl_file.sheet_names

            # 篩選出數字工作表名稱
            numeric_sheets = []
            for sheet in sheet_names:
                try:
                    if sheet.isdigit() or (isinstance(sheet, str) and sheet.replace('.', '').isdigit()):
                        numeric_sheets.append(int(float(sheet)))
                    elif isinstance(sheet, str) and len(sheet) == 6 and sheet.isdigit():
                        numeric_sheets.append(int(sheet))
                except ValueError:
                    continue

            if not numeric_sheets:
                os.unlink(tmp_file_path)
                return False

            # 找出最大的數字工作表
            max_sheet = str(max(numeric_sheets))

            # 讀取該工作表
            self.excel_data = pd.read_excel(tmp_file_path, sheet_name=max_sheet, header=None)

            # 清理臨時檔案
            os.unlink(tmp_file_path)
            return True

        except Exception as e:
            st.error(f"載入Excel檔案時發生錯誤: {e}")
            return False

    def get_consultants_data(self) -> List[Dict]:
        """獲取顧問資料"""
        if self.excel_data is None:
            return []

        consultants = []
        row = 8  # A9對應index 8

        while row < len(self.excel_data):
            consultant_name = self.excel_data.iloc[row, 0]  # A欄

            if pd.isna(consultant_name) or consultant_name == "":
                break

            if str(consultant_name).strip() != "公司":
                personal_performance = self.excel_data.iloc[row, 2] if not pd.isna(self.excel_data.iloc[row, 2]) else 0
                personal_consumption = self.excel_data.iloc[row, 6] if not pd.isna(self.excel_data.iloc[row, 6]) else 0

                consultants.append({
                    'name': consultant_name,
                    'performance': float(personal_performance),
                    'consumption': float(personal_consumption),
                    'row': row + 1
                })

            row += 1

        self.consultant_count = len(consultants)
        return consultants

    def calc_progressive_bonus(self, amount: float, levels: List[tuple]) -> float:
        """累進制計算獎金"""
        total = 0
        for min_val, max_val, rate in levels:
            if amount > min_val:
                upper_bound = min(amount, max_val)
                taxable_amount = upper_bound - min_val
                bonus_for_this_level = taxable_amount * rate
                total += bonus_for_this_level
            if amount <= max_val:
                break
        return total

    def calc_full_amount_bonus(self, amount: float, levels: List[tuple]) -> float:
        """全額抽成:整筆金額 × 所落最高級距的單一費率"""
        selected_rate = levels[0][2]
        for min_val, max_val, rate in levels:
            if amount > min_val:
                selected_rate = rate
        return amount * selected_rate

    def get_vip_statistics(self, file_bytes) -> Dict:
        """統計所有 sheet 的 VIP 項目 (D17 以下 = VIP, E 欄 = 項目名稱)"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name

            xl_file = pd.ExcelFile(tmp_file_path)
            sheet_names = xl_file.sheet_names
            vip_statistics = {}

            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(tmp_file_path, sheet_name=sheet_name, header=None)

                    # 從第17行開始 (index 16)
                    for row_idx in range(16, len(df)):
                        d_cell = df.iloc[row_idx, 3] if row_idx < len(df) and 3 < len(df.columns) else None

                        # 檢查 D 欄是否包含 "VIP"
                        if pd.notna(d_cell) and "VIP" in str(d_cell):
                            e_cell = df.iloc[row_idx, 4] if row_idx < len(df) and 4 < len(df.columns) else None

                            if pd.notna(e_cell):
                                item_name = str(e_cell).strip()

                                if item_name not in vip_statistics:
                                    vip_statistics[item_name] = 0

                                vip_statistics[item_name] += 1

                except Exception:
                    continue

            os.unlink(tmp_file_path)
            return vip_statistics

        except Exception as e:
            st.error(f"統計 VIP 項目時發生錯誤: {e}")
            return {}

    def get_product_sales_statistics(self, file_bytes) -> Dict:
        """統計所有顧問的產品銷售組數"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name

            xl_file = pd.ExcelFile(tmp_file_path)
            sheet_names = xl_file.sheet_names
            consultant_product_sales = {}

            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(tmp_file_path, sheet_name=sheet_name, header=None)

                    for row_idx in range(16, len(df)):
                        f_cell = df.iloc[row_idx, 5] if row_idx < len(df) and 5 < len(df.columns) else None

                        if pd.notna(f_cell) and str(f_cell).strip() == "購產品":
                            o_cell = df.iloc[row_idx, 14] if row_idx < len(df) and 14 < len(df.columns) else None

                            if pd.notna(o_cell):
                                consultant_code = str(o_cell).strip()

                                if consultant_code not in consultant_product_sales:
                                    consultant_product_sales[consultant_code] = 0

                                consultant_product_sales[consultant_code] += 1

                except Exception:
                    continue

            os.unlink(tmp_file_path)
            return consultant_product_sales

        except Exception as e:
            st.error(f"統計產品銷售時發生錯誤: {e}")
            return {}

    def calculate_product_bonus(self, product_sales: Dict) -> Dict:
        """計算產品達標獎金（30組以上得2000元）"""
        product_bonuses = {}

        for consultant, sales_count in product_sales.items():
            bonus = 2000 if sales_count >= 30 else 0
            product_bonuses[consultant] = {
                'sales_count': sales_count,
                'bonus': bonus,
                'qualified': sales_count >= 30
            }

        return product_bonuses

    def calculate_consultant_bonus(self, product_bonuses: Dict = None) -> tuple:
        """計算顧問獎金"""
        if self.excel_data is None:
            return {}, 0, 0

        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0
        consultants = self.get_consultants_data()

        if not consultants:
            return {}, 0, 0

        consultant_performance_pool = self.calc_progressive_bonus(total_performance, self.performance_bonus_levels) * 0.7
        consultant_consumption_pool = self.calc_progressive_bonus(total_consumption, self.consumption_bonus_levels) * 0.4

        total_consultant_performance = sum(c['performance'] for c in consultants)
        consultant_bonuses = {}

        for consultant in consultants:
            product_qualified = True
            if product_bonuses and consultant['name'] in product_bonuses:
                product_qualified = product_bonuses[consultant['name']]['qualified']

            perf_ok = consultant['performance'] >= 1680000
            cons_ok = consultant['performance'] >= 1200000

            if not product_qualified:
                performance_bonus = 0
                consumption_bonus = 0
            else:
                if perf_ok and total_consultant_performance > 0:
                    performance_ratio = consultant['performance'] / total_consultant_performance
                    performance_bonus = consultant_performance_pool * performance_ratio
                else:
                    performance_bonus = 0

                if cons_ok and total_consumption > 0:
                    consumption_ratio = consultant['consumption'] / total_consumption
                    consumption_bonus = consultant_consumption_pool * consumption_ratio
                else:
                    consumption_bonus = 0

            consultant_bonuses[consultant['name']] = {
                'performance_bonus': performance_bonus,
                'consumption_bonus': consumption_bonus,
                'total_bonus': performance_bonus + consumption_bonus,
                'personal_performance': consultant['performance'],
                'personal_consumption': consultant['consumption'],
                'product_qualified': product_qualified
            }

        return consultant_bonuses, consultant_performance_pool, consultant_consumption_pool

    def calculate_staff_bonus(self, consultant_performance_pool: float = None, consultant_consumption_pool: float = None) -> Dict:
        """計算美容師/護士獎金"""
        if self.excel_data is None or self.staff_count == 0:
            return {}

        if consultant_performance_pool is None or consultant_consumption_pool is None:
            total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0
            total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0
            consultant_performance_pool = self.calc_progressive_bonus(total_performance, self.performance_bonus_levels) * 0.7
            consultant_consumption_pool = self.calc_progressive_bonus(total_consumption, self.consumption_bonus_levels) * 0.4

        staff_performance_pool = consultant_performance_pool / 0.7 * 0.3
        staff_consumption_pool = consultant_consumption_pool / 0.4 * 0.6

        performance_bonus_per_person = staff_performance_pool / self.staff_count
        consumption_bonus_per_person = staff_consumption_pool / self.staff_count

        return {
            'staff_count': self.staff_count,
            'performance_pool': staff_performance_pool,
            'consumption_pool': staff_consumption_pool,
            'performance_bonus_per_person': performance_bonus_per_person,
            'consumption_bonus_per_person': consumption_bonus_per_person,
            'total_bonus_per_person': performance_bonus_per_person + consumption_bonus_per_person
        }

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

    def get_individual_staff_data(self) -> List[Dict]:
        """獲取個別美容師/護理師/櫃檯資料"""
        if self.excel_data is None:
            return []

        staff_data = []

        # 美容師資料 (K9-K15, L9-L15, M9-M15)
        for row in range(8, 15):
            if row < len(self.excel_data):
                name = self.excel_data.iloc[row, 10]  # K欄
                base_salary = 31054
                hand_skill_bonus = self.excel_data.iloc[row, 12] if not pd.isna(self.excel_data.iloc[row, 12]) else 0

                if pd.notna(name) and str(name).strip():
                    staff_data.append({
                        'name': str(name).strip(),
                        'position': '美容師',
                        'base_salary': float(base_salary),
                        'hand_skill_bonus': float(hand_skill_bonus),
                        'row': row + 1
                    })

        # 美容師資料 (N9-N15, O9-O15, P9-P15)
        for row in range(8, 15):
            if row < len(self.excel_data):
                name = self.excel_data.iloc[row, 13]  # N欄
                base_salary = self.excel_data.iloc[row, 14] if not pd.isna(self.excel_data.iloc[row, 14]) else 31054
                hand_skill_bonus = self.excel_data.iloc[row, 15] if not pd.isna(self.excel_data.iloc[row, 15]) else 0

                if pd.notna(name) and str(name).strip():
                    staff_data.append({
                        'name': str(name).strip(),
                        'position': '美容師',
                        'base_salary': float(base_salary),
                        'hand_skill_bonus': float(hand_skill_bonus),
                        'row': row + 1
                    })

        # 護理師資料 (Q9-Q11)
        for row in range(8, 11):
            if row < len(self.excel_data):
                name = self.excel_data.iloc[row, 16]  # Q欄
                base_salary = 31175
                hand_skill_bonus = self.excel_data.iloc[row, 18] if not pd.isna(self.excel_data.iloc[row, 18]) else 0

                if pd.notna(name) and str(name).strip():
                    staff_data.append({
                        'name': str(name).strip(),
                        'position': '護理師',
                        'base_salary': float(base_salary),
                        'hand_skill_bonus': float(hand_skill_bonus),
                        'row': row + 1
                    })

        # 櫃檯資料 (Q12-Q15)
        for row in range(11, 15):
            if row < len(self.excel_data):
                name = self.excel_data.iloc[row, 16]  # Q欄
                base_salary = 31054
                hand_skill_bonus = self.excel_data.iloc[row, 18] if not pd.isna(self.excel_data.iloc[row, 18]) else 0

                if pd.notna(name) and str(name).strip():
                    staff_data.append({
                        'name': str(name).strip(),
                        'position': '櫃檯',
                        'base_salary': float(base_salary),
                        'hand_skill_bonus': float(hand_skill_bonus),
                        'row': row + 1
                    })

        return staff_data

    def calculate_high_target_bonus(self, high_target_amount: float = None) -> Dict:
        """計算高標達標獎金"""
        if high_target_amount is None:
            return {}

        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0

        if total_performance < high_target_amount:
            return {}

        staff_data = self.get_individual_staff_data()
        high_target_bonuses = {}

        for staff in staff_data:
            if staff['position'] in self.high_target_bonuses:
                bonus_amount = self.high_target_bonuses[staff['position']]
                high_target_bonuses[staff['name']] = {
                    'position': staff['position'],
                    'bonus': bonus_amount
                }

        return high_target_bonuses

    def calculate_individual_staff_salary(self, high_target_bonuses: Dict = None, staff_team_bonus: Dict = None, high_target_amount: float = None) -> Dict:
        """計算個別美容師/護理師/櫃檯的完整薪資明細"""
        staff_data = self.get_individual_staff_data()
        salary_details = {}

        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0

        team_performance_bonus = 0
        team_consumption_bonus = 0
        if staff_team_bonus:
            team_performance_bonus = staff_team_bonus.get('performance_bonus_per_person', 0)
            team_consumption_bonus = staff_team_bonus.get('consumption_bonus_per_person', 0)

        for staff in staff_data:
            name = staff['name']
            position = staff['position']
            base_salary = staff['base_salary']
            hand_skill_bonus = staff['hand_skill_bonus']

            overtime_pay = 0

            high_target_bonus = 0
            if high_target_bonuses and name in high_target_bonuses:
                high_target_bonus = high_target_bonuses[name]['bonus']

            license_allowance = 0
            full_attendance_bonus = 0
            rank_bonus = 0
            position_allowance = 0

            consumption_achievement_bonus = 0
            performance_500w_bonus = 0
            store_performance_incentive = 0

            if position == '護理師':
                license_allowance = 5000
                full_attendance_bonus = 2000
            elif position == '櫃檯':
                rank_bonus = 1946
                position_allowance = 2000

                if high_target_amount and total_performance >= high_target_amount and total_consumption >= 3000000:
                    consumption_achievement_bonus = 3000

                if total_performance >= 5000000:
                    performance_500w_bonus = 5000

                if high_target_amount and total_performance >= high_target_amount:
                    store_performance_incentive = 5000

            if position == '美容師':
                total_salary = (base_salary + overtime_pay + hand_skill_bonus +
                              license_allowance + rank_bonus + position_allowance)
            elif position == '護理師':
                total_salary = (base_salary + overtime_pay + hand_skill_bonus +
                              license_allowance + rank_bonus + position_allowance)
            else:  # 櫃檯
                total_salary = (base_salary + overtime_pay + hand_skill_bonus + high_target_bonus +
                              license_allowance +
                              rank_bonus + position_allowance + consumption_achievement_bonus +
                              performance_500w_bonus + store_performance_incentive)

            salary_details[name] = {
                'position': position,
                'base_salary': base_salary,
                'overtime_pay': overtime_pay,
                'hand_skill_bonus': hand_skill_bonus,
                'team_performance_bonus': team_performance_bonus if position in ['美容師', '護理師'] else 0,
                'team_consumption_bonus': team_consumption_bonus if position in ['美容師', '護理師'] else 0,
                'high_target_bonus': high_target_bonus,
                'license_allowance': license_allowance,
                'full_attendance_bonus': full_attendance_bonus,
                'rank_bonus': rank_bonus,
                'position_allowance': position_allowance,
                'consumption_achievement_bonus': consumption_achievement_bonus,
                'performance_500w_bonus': performance_500w_bonus,
                'store_performance_incentive': store_performance_incentive,
                'total_salary': total_salary,
                'row': staff['row']
            }

        return salary_details

def format_currency(amount):
    """格式化貨幣顯示"""
    if isinstance(amount, (int, float)):
        return f"NT$ {amount:,.0f}"
    return "NT$ 0"

def main():
    """主應用程式"""
    # 標題
    st.markdown('<div class="main-header">💰 Only Beauty 薪資計算系統</div>', unsafe_allow_html=True)
    st.markdown("---")

    # 初始化 session state
    if 'calculator' not in st.session_state:
        st.session_state.calculator = OnlyBeautySalaryCalculator()
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False

    # 側邊欄配置
    with st.sidebar:
        st.header("📋 操作步驟")
        st.write("1. 上傳Excel檔案")
        st.write("2. 設定基本參數")
        st.write("3. 設定角色與計算方式")
        st.write("4. 計算薪資")
        st.write("5. 查看結果")
        st.markdown("---")

    # 步驟1: 檔案上傳
    st.markdown('<div class="step-header">📁 步驟 1: 上傳Excel檔案</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "選擇Excel檔案",
        type=['xlsx', 'xls'],
        help="請上傳包含薪資資料的Excel檔案"
    )

    if uploaded_file is not None:
        try:
            # 讀取檔案
            file_bytes = uploaded_file.read()

            with st.spinner('正在解析Excel檔案...'):
                if st.session_state.calculator.load_excel_from_bytes(file_bytes):
                    st.session_state.file_uploaded = True
                    st.session_state.uploaded_file_bytes = file_bytes
                    st.success(f"✅ 檔案 '{uploaded_file.name}' 上傳成功！")
                else:
                    st.error("❌ Excel檔案解析失敗，請檢查檔案格式")
                    st.session_state.file_uploaded = False
        except Exception as e:
            st.error(f"❌ 檔案處理錯誤: {str(e)}")
            st.session_state.file_uploaded = False

    # 步驟2: 基本設定
    if st.session_state.file_uploaded:
        st.markdown("---")
        st.markdown('<div class="step-header">⚙️ 步驟 2: 基本資料設定</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            staff_count = st.number_input(
                "美容師/護理師總人數",
                min_value=1,
                max_value=50,
                value=5,
                help="請輸入美容師和護理師的總人數"
            )

        with col2:
            manager_name = st.text_input(
                "店長名稱",
                value="",
                help="如果有店長請輸入名稱，沒有請留空"
            )

        with col3:
            high_target = st.number_input(
                "高標達標金額",
                min_value=0,
                value=4000000,
                step=100000,
                format="%d",
                help="設定高標達標獎金的業績門檻"
            )

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
                with col_b:
                    role = st.selectbox(
                        "角色", ['顧問', '副店長', '店長'],
                        index=0,
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

        # 步驟3: 開始計算
        st.markdown("---")
        st.markdown('<div class="step-header">🔢 步驟 4: 開始計算</div>', unsafe_allow_html=True)

        if st.button("🚀 開始計算薪資", type="primary", use_container_width=True):
            try:
                with st.spinner('正在計算薪資，請稍候...'):
                    # 設定參數
                    st.session_state.calculator.staff_count = staff_count
                    st.session_state.calculator.manager_name = manager_name if manager_name else None
                    high_target_amount = high_target if high_target > 0 else None

                    # 統計 VIP 項目
                    with st.status("統計 VIP 項目中...", expanded=True) as status:
                        vip_statistics = st.session_state.calculator.get_vip_statistics(st.session_state.uploaded_file_bytes)
                        status.update(label="VIP 項目統計完成!", state="complete")

                    # 統計產品銷售
                    with st.status("統計產品銷售中...", expanded=True) as status:
                        product_sales = st.session_state.calculator.get_product_sales_statistics(st.session_state.uploaded_file_bytes)
                        product_bonuses = st.session_state.calculator.calculate_product_bonus(product_sales)
                        status.update(label="產品銷售統計完成!", state="complete")

                    # 計算團體獎金
                    with st.status("計算團體獎金中...", expanded=True) as status:
                        consultant_bonuses, consultant_performance_pool, consultant_consumption_pool = st.session_state.calculator.calculate_consultant_bonus(product_bonuses)
                        staff_bonuses = st.session_state.calculator.calculate_staff_bonus(consultant_performance_pool, consultant_consumption_pool)
                        status.update(label="團體獎金計算完成!", state="complete")

                    # 計算個人獎金
                    with st.status("計算個人獎金中...", expanded=True) as status:
                        individual_bonuses = st.session_state.calculator.calculate_individual_bonus(
                            consultant_bonuses,
                            high_target_amount,
                            st.session_state.get('role_config')
                        )
                        status.update(label="個人獎金計算完成!", state="complete")

                    # 計算高標達標獎金
                    with st.status("計算高標達標獎金中...", expanded=True) as status:
                        high_target_bonuses = {}
                        if high_target_amount:
                            high_target_bonuses = st.session_state.calculator.calculate_high_target_bonus(high_target_amount)
                        status.update(label="高標達標獎金計算完成!", state="complete")

                    # 計算個別員工薪資明細
                    with st.status("計算薪資明細中...", expanded=True) as status:
                        individual_staff_salaries = st.session_state.calculator.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses, high_target_amount)
                        status.update(label="薪資明細計算完成!", state="complete")

                    # 儲存結果
                    st.session_state.results = {
                        'consultant_bonuses': consultant_bonuses,
                        'staff_bonuses': staff_bonuses,
                        'individual_bonuses': individual_bonuses,
                        'high_target_bonuses': high_target_bonuses,
                        'individual_staff_salaries': individual_staff_salaries,
                        'product_bonuses': product_bonuses,
                        'vip_statistics': vip_statistics
                    }

                    st.success("🎉 薪資計算完成！請查看下方結果。")

            except Exception as e:
                st.error(f"❌ 計算過程發生錯誤: {str(e)}")
                st.exception(e)

    # 步驟4: 顯示結果
    if st.session_state.results:
        st.markdown("---")
        st.markdown('<div class="step-header">📊 步驟 5: 計算結果</div>', unsafe_allow_html=True)

        results = st.session_state.results

        # 建立分頁
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 顧問獎金", "🏢 員工獎金", "💰 薪資明細", "📈 統計摘要", "💎 VIP 項目統計"])

        with tab1:
            st.subheader("顧問獎金明細")
            if results['consultant_bonuses']:
                for name, data in results['consultant_bonuses'].items():
                    with st.container():
                        st.markdown(f"**{name}**")

                        # 第一行：個人業績和消耗
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("個人業績", format_currency(data['personal_performance']))
                        with col2:
                            st.metric("個人消耗", format_currency(data['personal_consumption']))
                        with col3:
                            st.metric("團體業績獎金", format_currency(data['performance_bonus']))
                        with col4:
                            st.metric("團體消耗獎金", format_currency(data['consumption_bonus']))

                        # 第二行：個人業績獎金和個人消耗獎金
                        if results.get('individual_bonuses') and name in results['individual_bonuses']:
                            individual_data = results['individual_bonuses'][name]

                            _role = individual_data.get('role', '顧問')
                            _mode = individual_data.get('mode', '階梯')
                            st.markdown(f"#### 個人獎金（{_role}・{_mode}）")
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("個人業績獎金", format_currency(individual_data['individual_performance_bonus']))
                            with col2:
                                st.metric("個人消耗獎金", format_currency(individual_data['individual_consumption_bonus']))
                            with col3:
                                if individual_data.get('performance_incentive_bonus', 0) > 0:
                                    st.metric("業績激勵獎金", format_currency(individual_data['performance_incentive_bonus']))
                            with col4:
                                st.metric("個人獎金小計", format_currency(individual_data['individual_total']))

                        total_bonus = data['performance_bonus'] + data['consumption_bonus']
                        st.metric("**團體總獎金**", format_currency(total_bonus))

                        if not data.get('product_qualified', True):
                            st.warning("⚠️ 產品未達標，團體獎金已清零")

                        st.markdown("---")
            else:
                st.info("無顧問獎金資料")

        with tab2:
            st.subheader("美容師/護理師團體獎金")
            if results['staff_bonuses']:
                data = results['staff_bonuses']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("總人數", f"{data['staff_count']} 人")
                with col2:
                    st.metric("業績獎金池", format_currency(data['performance_pool']))
                with col3:
                    st.metric("消耗獎金池", format_currency(data['consumption_pool']))

                st.markdown("### 每人獎金分配")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("每人業績獎金", format_currency(data['performance_bonus_per_person']))
                with col2:
                    st.metric("每人消耗獎金", format_currency(data['consumption_bonus_per_person']))
                with col3:
                    st.metric("每人總獎金", format_currency(data['total_bonus_per_person']))
            else:
                st.info("無員工獎金資料")

        with tab3:
            st.subheader("個別員工薪資明細")
            if results['individual_staff_salaries']:
                # 按職位分組顯示
                positions = ['美容師', '護理師', '櫃檯']

                for position in positions:
                    position_staff = {name: data for name, data in results['individual_staff_salaries'].items()
                                    if data['position'] == position}

                    if position_staff:
                        st.markdown(f"### {position}")

                        for name, salary_data in position_staff.items():
                            with st.expander(f"{name} (第{salary_data['row']}行)"):
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.write("**基本薪資**")
                                    st.write(f"底薪: {format_currency(salary_data['base_salary'])}")
                                    if salary_data['hand_skill_bonus'] > 0:
                                        st.write(f"手技獎金: {format_currency(salary_data['hand_skill_bonus'])}")

                                with col2:
                                    st.write("**津貼獎金**")
                                    if salary_data['license_allowance'] > 0:
                                        st.write(f"執照津貼: {format_currency(salary_data['license_allowance'])}")
                                    if salary_data['rank_bonus'] > 0:
                                        st.write(f"職等獎金: {format_currency(salary_data['rank_bonus'])}")
                                    if salary_data['position_allowance'] > 0:
                                        st.write(f"職務津貼: {format_currency(salary_data['position_allowance'])}")

                                with col3:
                                    st.write("**特殊獎金**")
                                    if salary_data.get('consumption_achievement_bonus', 0) > 0:
                                        st.write(f"門店業績達標+消耗300萬獎金: {format_currency(salary_data['consumption_achievement_bonus'])}")
                                    if salary_data.get('performance_500w_bonus', 0) > 0:
                                        st.write(f"業績500萬獎金: {format_currency(salary_data['performance_500w_bonus'])}")
                                    if salary_data.get('store_performance_incentive', 0) > 0:
                                        st.write(f"門店業績激勵獎金: {format_currency(salary_data['store_performance_incentive'])}")

                                st.markdown("---")
                                st.markdown(f"**當月總薪資: {format_currency(salary_data['total_salary'])}**")

                                # 不計入當月總薪資的項目
                                if position in ['美容師', '護理師']:
                                    separate_items = []
                                    if salary_data['team_performance_bonus'] > 0:
                                        separate_items.append(f"團體業績獎金: {format_currency(salary_data['team_performance_bonus'])}")
                                    if salary_data['team_consumption_bonus'] > 0:
                                        separate_items.append(f"團體消耗獎金: {format_currency(salary_data['team_consumption_bonus'])}")
                                    if position == '護理師' and salary_data['full_attendance_bonus'] > 0:
                                        separate_items.append(f"全勤獎金: {format_currency(salary_data['full_attendance_bonus'])}")
                                    if salary_data['high_target_bonus'] > 0:
                                        separate_items.append(f"高標達標獎金: {format_currency(salary_data['high_target_bonus'])}")

                                    if separate_items:
                                        st.info("**不計入當月總薪資的項目:**\n" + "\n".join([f"• {item}" for item in separate_items]))
            else:
                st.info("無薪資明細資料")

        with tab4:
            st.subheader("統計摘要")

            # 計算總計數據
            total_consultant_bonus = 0
            total_consultants = 0
            if results['consultant_bonuses']:
                for data in results['consultant_bonuses'].values():
                    total_consultant_bonus += data['performance_bonus'] + data['consumption_bonus']
                    total_consultants += 1

            total_staff_salary = 0
            total_staff = 0
            if results['individual_staff_salaries']:
                for data in results['individual_staff_salaries'].values():
                    total_staff_salary += data['total_salary']
                    total_staff += 1

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 👥 人員統計")
                st.metric("顧問人數", f"{total_consultants} 人")
                st.metric("員工人數", f"{total_staff} 人")
                st.metric("總人數", f"{total_consultants + total_staff} 人")

            with col2:
                st.markdown("### 💰 金額統計")
                st.metric("顧問總獎金", format_currency(total_consultant_bonus))
                st.metric("員工總薪資", format_currency(total_staff_salary))
                st.metric("**總支出**", format_currency(total_consultant_bonus + total_staff_salary))

            # 產品銷售統計
            if results['product_bonuses']:
                st.markdown("### 🛍️ 產品銷售統計")
                product_data = []
                for consultant, data in results['product_bonuses'].items():
                    product_data.append({
                        '顧問': consultant,
                        '銷售組數': data['sales_count'],
                        '獎金': format_currency(data['bonus']),
                        '達標狀況': '✅ 達標' if data['qualified'] else '❌ 未達標'
                    })

                if product_data:
                    df = pd.DataFrame(product_data)
                    st.dataframe(df, use_container_width=True)

        with tab5:
            st.subheader("VIP 項目統計")

            if results.get('vip_statistics'):
                vip_stats = results['vip_statistics']

                # 顯示總計
                total_vip_count = sum(vip_stats.values())
                st.markdown(f"### 📊 VIP 總數: {total_vip_count}")

                st.markdown("---")
                st.markdown("### 📋 項目明細")

                # 建立表格資料
                vip_data = []
                for item_name, count in sorted(vip_stats.items(), key=lambda x: x[1], reverse=True):
                    vip_data.append({
                        'VIP 項目': item_name,
                        '數量': count
                    })

                if vip_data:
                    df = pd.DataFrame(vip_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # 視覺化圖表
                    st.markdown("---")
                    st.markdown("### 📊 項目分布圖")

                    # 使用 Streamlit 內建的條形圖
                    chart_df = df.set_index('VIP 項目')
                    st.bar_chart(chart_df)
                else:
                    st.info("目前沒有 VIP 項目資料")
            else:
                st.info("目前沒有 VIP 項目資料")

        # 匯出功能
        st.markdown("---")
        if st.button("📥 匯出計算結果 (JSON)", use_container_width=True):
            result_json = json.dumps(results, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                label="下載 JSON 檔案",
                data=result_json,
                file_name="salary_calculation_results.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()