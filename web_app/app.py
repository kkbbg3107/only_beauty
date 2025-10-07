from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
import traceback
from typing import Dict, List
import json

app = Flask(__name__)

# 設定檔案上傳
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 確保上傳目錄存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """檢查檔案類型是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class OnlyBeautySalaryCalculator:
    """薪資計算器 - 網頁版"""

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

        # 高標達標獎金設定
        self.high_target_bonuses = {
            '美容師': 5000,
            '護理師': 10000
        }

        self.excel_data = None
        self.consultant_count = 0
        self.staff_count = 0
        self.manager_name = None

    def load_excel_from_file(self, file_path: str) -> bool:
        """從檔案路徑載入Excel"""
        try:
            # 讀取所有工作表名稱
            xl_file = pd.ExcelFile(file_path)
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
                return False

            # 找出最大的數字工作表
            max_sheet = str(max(numeric_sheets))

            # 讀取該工作表
            self.excel_data = pd.read_excel(file_path, sheet_name=max_sheet, header=None)
            return True

        except Exception as e:
            print(f"載入Excel檔案時發生錯誤: {e}")
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

    def get_product_sales_statistics(self, file_path: str) -> Dict:
        """統計所有顧問的產品銷售組數"""
        try:
            xl_file = pd.ExcelFile(file_path)
            sheet_names = xl_file.sheet_names
            consultant_product_sales = {}

            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

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

            return consultant_product_sales

        except Exception as e:
            print(f"統計產品銷售時發生錯誤: {e}")
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

    def calculate_individual_bonus(self, consultant_bonuses: Dict, high_target_amount: float = None) -> Dict:
        """計算個人業績獎金和個人消耗獎金"""
        individual_bonuses = {}

        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0
        store_achieved = high_target_amount and total_performance >= high_target_amount

        for name, bonus_data in consultant_bonuses.items():
            performance = bonus_data['personal_performance']
            consumption = bonus_data['personal_consumption']

            is_manager = (name == self.manager_name)

            if is_manager:
                perf_levels = self.manager_performance_levels
                cons_levels = self.manager_consumption_levels
                role = "店長"
            else:
                perf_levels = self.consultant_performance_levels
                cons_levels = self.consultant_consumption_levels
                role = "顧問"

            individual_performance_bonus = self.calc_progressive_bonus(performance, perf_levels)
            individual_consumption_bonus = self.calc_progressive_bonus(consumption, cons_levels)

            performance_incentive_bonus = 0
            if performance >= 1680000 and store_achieved:
                performance_incentive_bonus = 10000

            individual_bonuses[name] = {
                'role': role,
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

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """靜態檔案服務"""
    return send_from_directory('static', filename)

@app.route('/calculate', methods=['POST'])
def calculate_salary():
    """計算薪資API"""
    try:
        # 檢查檔案上傳
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '沒有上傳檔案'
            })

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '沒有選擇檔案'
            })

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '檔案格式不支援，請上傳 .xlsx 或 .xls 檔案'
            })

        # 獲取表單參數
        staff_count = request.form.get('staff_count')
        manager_name = request.form.get('manager_name', '').strip()
        high_target = request.form.get('high_target', '').strip()

        # 驗證參數
        try:
            staff_count = int(staff_count)
            if staff_count < 1:
                raise ValueError("員工人數必須大於0")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': '員工人數格式錯誤'
            })

        high_target_amount = None
        if high_target:
            try:
                high_target_amount = float(high_target)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '高標達標金額格式錯誤'
                })

        # 儲存上傳的檔案
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # 初始化計算器
            calculator = OnlyBeautySalaryCalculator()
            calculator.staff_count = staff_count
            calculator.manager_name = manager_name if manager_name else None

            # 載入Excel檔案
            if not calculator.load_excel_from_file(file_path):
                return jsonify({
                    'success': False,
                    'error': 'Excel檔案載入失敗，請檢查檔案格式'
                })

            # 統計產品銷售
            product_sales = calculator.get_product_sales_statistics(file_path)
            product_bonuses = calculator.calculate_product_bonus(product_sales)

            # 計算團體獎金
            consultant_bonuses, consultant_performance_pool, consultant_consumption_pool = calculator.calculate_consultant_bonus(product_bonuses)
            staff_bonuses = calculator.calculate_staff_bonus(consultant_performance_pool, consultant_consumption_pool)

            # 計算個人獎金
            individual_bonuses = calculator.calculate_individual_bonus(consultant_bonuses, high_target_amount)

            # 計算高標達標獎金
            high_target_bonuses = {}
            if high_target_amount:
                high_target_bonuses = calculator.calculate_high_target_bonus(high_target_amount)

            # 計算個別員工薪資明細
            individual_staff_salaries = calculator.calculate_individual_staff_salary(high_target_bonuses, staff_bonuses, high_target_amount)

            # 準備回傳結果
            results = {
                'consultant_bonuses': consultant_bonuses,
                'staff_bonuses': staff_bonuses,
                'individual_bonuses': individual_bonuses,
                'high_target_bonuses': high_target_bonuses,
                'individual_staff_salaries': individual_staff_salaries,
                'product_bonuses': product_bonuses
            }

            return jsonify({
                'success': True,
                'results': results
            })

        finally:
            # 清理上傳的檔案
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        # 記錄錯誤詳情
        error_detail = traceback.format_exc()
        print(f"計算錯誤: {error_detail}")

        return jsonify({
            'success': False,
            'error': f'計算過程發生錯誤: {str(e)}'
        })

@app.errorhandler(413)
def too_large(e):
    """檔案太大錯誤處理"""
    return jsonify({
        'success': False,
        'error': '檔案太大，請上傳小於16MB的檔案'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """404錯誤處理"""
    return jsonify({
        'success': False,
        'error': '頁面不存在'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """500錯誤處理"""
    return jsonify({
        'success': False,
        'error': '伺服器內部錯誤'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)