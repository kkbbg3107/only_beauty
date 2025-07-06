import pandas as pd
import os
from typing import Dict, List

class OnlyBeautySalaryCalculator:
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
        
        self.excel_data = None
        self.consultant_count = 0
        self.staff_count = 0
        self.manager_name = None  # 店長名稱
        
    def load_excel(self, file_path: str) -> bool:
        """載入Excel檔案並找出數字最大的工作表"""
        try:
            # 展開 ~ 路徑
            expanded_path = os.path.expanduser(file_path)
            print(f"正在檢查路徑: {expanded_path}")
            
            if not os.path.exists(expanded_path):
                print(f"❌ 錯誤：檔案 {expanded_path} 不存在")
                
                # 提供路徑建議
                suggestions = self.suggest_file_paths(expanded_path)
                if suggestions:
                    print("\n💡 找到可能的檔案位置:")
                    for idx, path in enumerate(suggestions, 1):
                        print(f"   {idx}. {path}")
                    print("\n提示：您可以複製正確的路徑重新輸入")
                else:
                    print("\n💡 建議檢查:")
                    print("   - 檔案是否在桌面或下載資料夾")
                    print("   - 檔案名稱拼寫是否正確")
                    print("   - 可以將檔案拖拽到終端獲取完整路徑")
                return False
            
            # 讀取所有工作表名稱
            xl_file = pd.ExcelFile(expanded_path)
            sheet_names = xl_file.sheet_names
            
            print(f"找到的工作表: {sheet_names}")
            
            # 篩選出數字工作表名稱
            numeric_sheets = []
            for sheet in sheet_names:
                # 檢查是否為純數字或數字字符串
                try:
                    if sheet.isdigit() or (isinstance(sheet, str) and sheet.replace('.', '').isdigit()):
                        numeric_sheets.append(int(float(sheet)))
                    # 也接受YYYYMM格式（如202412）
                    elif isinstance(sheet, str) and len(sheet) == 6 and sheet.isdigit():
                        numeric_sheets.append(int(sheet))
                except ValueError:
                    continue
            
            if not numeric_sheets:
                print("錯誤：沒有找到數字工作表")
                return False
            
            # 找出最大的數字工作表
            max_sheet = str(max(numeric_sheets))
            print(f"使用工作表: {max_sheet}")
            
            # 讀取該工作表
            self.excel_data = pd.read_excel(expanded_path, sheet_name=max_sheet, header=None)
            print("Excel檔案載入成功！")
            return True
            
        except Exception as e:
            print(f"載入Excel檔案時發生錯誤: {e}")
            return False
    
    def suggest_file_paths(self, original_path: str) -> List[str]:
        """當檔案不存在時，提供可能的路徑建議"""
        suggestions = []
        filename = os.path.basename(original_path)
        
        # 常見的目錄位置
        common_dirs = [
            "/Users/ben_kuo/Desktop",
            "/Users/ben_kuo/Downloads", 
            "/Users/ben_kuo/Documents",
            "/Users/ben_kuo/only_beauty_report",
            os.getcwd()  # 當前目錄
        ]
        
        for directory in common_dirs:
            if os.path.exists(directory):
                potential_path = os.path.join(directory, filename)
                if os.path.exists(potential_path):
                    suggestions.append(potential_path)
        
        # 搜尋包含相似名稱的檔案
        try:
            base_name = os.path.splitext(filename)[0]
            for root, dirs, files in os.walk("/Users/ben_kuo"):
                for file in files:
                    if (file.endswith(('.xlsx', '.xls')) and 
                        (base_name.lower() in file.lower() or file.lower() in base_name.lower())):
                        suggestions.append(os.path.join(root, file))
                        if len(suggestions) >= 5:  # 限制建議數量
                            break
                if len(suggestions) >= 5:
                    break
        except Exception:
            pass
        
        return list(set(suggestions))  # 去除重複
    
    def get_consultants_data(self) -> List[Dict]:
        """獲取顧問資料"""
        if self.excel_data is None:
            return []
        
        consultants = []
        row = 8  # A9對應index 8
        
        while row < len(self.excel_data):
            consultant_name = self.excel_data.iloc[row, 0]  # A欄
            
            # 如果遇到空值或NaN，停止
            if pd.isna(consultant_name) or consultant_name == "":
                break
                
            # 跳過"公司"
            if str(consultant_name).strip() != "公司":
                personal_performance = self.excel_data.iloc[row, 2] if not pd.isna(self.excel_data.iloc[row, 2]) else 0  # C欄
                personal_consumption = self.excel_data.iloc[row, 6] if not pd.isna(self.excel_data.iloc[row, 6]) else 0  # G欄
                
                consultants.append({
                    'name': consultant_name,
                    'performance': float(personal_performance),
                    'consumption': float(personal_consumption),
                    'row': row + 1  # 顯示Excel實際行號
                })
            
            row += 1
        
        self.consultant_count = len(consultants)
        return consultants
    
    def calculate_consultant_bonus(self, product_bonuses: Dict = None) -> Dict:
        """計算顧問獎金（累進制），產品未達標者清零"""
        if self.excel_data is None:
            return {}
        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0  # E5
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0  # E7
        consultants = self.get_consultants_data()
        if not consultants:
            return {}
        print(f"總業績 (E5): {total_performance:,.0f}")
        print(f"總消耗 (E7): {total_consumption:,.0f}")
        # 業績獎金累進制
        consultant_performance_pool = self.calc_progressive_bonus(total_performance, self.performance_bonus_levels) * 0.7
        # 消耗獎金累進制
        consultant_consumption_pool = self.calc_progressive_bonus(total_consumption, self.consumption_bonus_levels) * 0.4
        print(f"顧問團體業績獎金池(累進): {consultant_performance_pool:,.0f}")
        print(f"顧問團體消耗獎金池(累進): {consultant_consumption_pool:,.0f}")
        total_consultant_performance = sum(c['performance'] for c in consultants)
        consultant_bonuses = {}
        for consultant in consultants:
            # 檢查產品達標狀況
            product_qualified = True  # 預設達標
            if product_bonuses and consultant['name'] in product_bonuses:
                product_qualified = product_bonuses[consultant['name']]['qualified']
            
            # 達標才分配
            perf_ok = consultant['performance'] >= 1680000
            cons_ok = consultant['performance'] >= 1200000
            
            # 如果產品未達標，清零所有獎金
            if not product_qualified:
                performance_bonus = 0
                consumption_bonus = 0
                print(f"  {consultant['name']}: 產品未達標，團體獎金清零")
            else:
                # 業績獎金分配
                if perf_ok and total_consultant_performance > 0:
                    performance_ratio = consultant['performance'] / total_consultant_performance
                    performance_bonus = consultant_performance_pool * performance_ratio
                else:
                    performance_bonus = 0
                # 消耗獎金分配
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
        return consultant_bonuses

    def calculate_staff_bonus(self) -> Dict:
        """計算美容師/護士獎金（累進制）"""
        if self.excel_data is None or self.staff_count == 0:
            return {}
        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0  # E5
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0  # E7
        # 業績獎金累進制
        staff_performance_pool = self.calc_progressive_bonus(total_performance, self.performance_bonus_levels) * 0.3
        # 消耗獎金累進制
        staff_consumption_pool = self.calc_progressive_bonus(total_consumption, self.consumption_bonus_levels) * 0.6
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
    
    def calculate_individual_bonus(self, consultant_bonuses: Dict) -> Dict:
        """計算個人業績獎金和個人消耗獎金"""
        individual_bonuses = {}
        
        print("\n開始計算個人獎金...")
        print(f"店長: {self.manager_name}")
        
        for name, bonus_data in consultant_bonuses.items():
            performance = bonus_data['personal_performance']
            consumption = bonus_data['personal_consumption']
            
            # 判斷是否為店長
            is_manager = (name == self.manager_name)
            
            # 選擇對應的級距表
            if is_manager:
                perf_levels = self.manager_performance_levels
                cons_levels = self.manager_consumption_levels
                role = "店長"
            else:
                perf_levels = self.consultant_performance_levels
                cons_levels = self.consultant_consumption_levels
                role = "顧問"
            
            # 計算個人業績獎金
            individual_performance_bonus = self.calc_progressive_bonus(performance, perf_levels, show_detail=False)
            
            # 計算個人消耗獎金
            individual_consumption_bonus = self.calc_progressive_bonus(consumption, cons_levels, show_detail=False)
            
            individual_bonuses[name] = {
                'role': role,
                'individual_performance_bonus': individual_performance_bonus,
                'individual_consumption_bonus': individual_consumption_bonus,
                'individual_total': individual_performance_bonus + individual_consumption_bonus
            }
            
            print(f"  {name} ({role}):")
            print(f"    個人業績獎金: {individual_performance_bonus:,.0f}")
            print(f"    個人消耗獎金: {individual_consumption_bonus:,.0f}")
            print(f"    個人獎金小計: {individual_performance_bonus + individual_consumption_bonus:,.0f}")
        
        return individual_bonuses
    
    def display_results(self, consultant_bonuses: Dict, staff_bonuses: Dict, product_bonuses: Dict = None, individual_bonuses: Dict = None):
        """顯示計算結果"""
        print("\n" + "="*70)
        print("薪資計算結果")
        print("="*70)
        
        if consultant_bonuses:
            print("\n顧問獎金明細:")
            print("-" * 60)
            for name, bonus in consultant_bonuses.items():
                print(f"{name}:")
                print(f"  個人業績: {bonus['personal_performance']:,.0f}")
                print(f"  個人消耗: {bonus['personal_consumption']:,.0f}")
                print(f"  團體業績獎金: {bonus['performance_bonus']:,.0f}")
                print(f"  團體消耗獎金: {bonus['consumption_bonus']:,.0f}")
                
                # 加入產品達標獎金
                product_bonus = 0
                if product_bonuses and name in product_bonuses:
                    product_bonus = product_bonuses[name]['bonus']
                    sales_count = product_bonuses[name]['sales_count']
                    print(f"  產品銷售: {sales_count} 組")
                    print(f"  產品達標獎金: {product_bonus:,.0f}")
                    
                    # 顯示產品達標狀況
                    if not product_bonuses[name]['qualified']:
                        print("  ⚠️  產品未達標，團體獎金已清零")
                
                # 加入個人獎金
                individual_performance_bonus = 0
                individual_consumption_bonus = 0
                if individual_bonuses and name in individual_bonuses:
                    individual_performance_bonus = individual_bonuses[name]['individual_performance_bonus']
                    individual_consumption_bonus = individual_bonuses[name]['individual_consumption_bonus']
                    role = individual_bonuses[name]['role']
                    print(f"  個人業績獎金: {individual_performance_bonus:,.0f} ({role})")
                    print(f"  個人消耗獎金: {individual_consumption_bonus:,.0f} ({role})")
                
                team_total = bonus['total_bonus'] + product_bonus
                individual_total = individual_performance_bonus + individual_consumption_bonus
                grand_total = team_total + individual_total
                
                print(f"  團體獎金小計: {bonus['total_bonus']:,.0f}")
                print(f"  團體+產品獎金: {team_total:,.0f}")
                print(f"  個人獎金小計: {individual_total:,.0f}")
                print(f"  【總獎金】: {grand_total:,.0f}")
                print()
        
        if staff_bonuses:
            print("美容師/護士獎金:")
            print("-" * 60)
            print(f"總人數: {staff_bonuses['staff_count']} 人")
            print(f"業績獎金池: {staff_bonuses['performance_pool']:,.0f}")
            print(f"消耗獎金池: {staff_bonuses['consumption_pool']:,.0f}")
            print(f"每人業績獎金: {staff_bonuses['performance_bonus_per_person']:,.0f}")
            print(f"每人消耗獎金: {staff_bonuses['consumption_bonus_per_person']:,.0f}")
            print(f"每人總獎金: {staff_bonuses['total_bonus_per_person']:,.0f}")
        
        if product_bonuses:
            print("\n產品達標獎金摘要:")
            print("-" * 60)
            total_product_bonus = sum(p['bonus'] for p in product_bonuses.values())
            qualified_count = sum(1 for p in product_bonuses.values() if p['qualified'])
            print(f"達標人數: {qualified_count} 人")
            print(f"產品達標獎金總額: {total_product_bonus:,.0f} 元")
    
    def calc_progressive_bonus(self, amount: float, levels: List[tuple], show_detail: bool = True) -> float:
        """累進制計算獎金，levels=[(min,max,rate), ...]"""
        total = 0
        for min_val, max_val, rate in levels:
            if amount > min_val:
                # 計算這個區間的獎金
                upper_bound = min(amount, max_val)
                taxable_amount = upper_bound - min_val
                bonus_for_this_level = taxable_amount * rate
                total += bonus_for_this_level
                if show_detail:
                    print(f"  階段 ({min_val:,}-{max_val:,}): {taxable_amount:,.0f} × {rate:.3f} = {bonus_for_this_level:,.2f}")
            if amount <= max_val:
                break
        return total
    
    def get_product_sales_statistics(self, file_path: str) -> Dict:
        """統計所有顧問的產品銷售組數"""
        try:
            expanded_path = os.path.expanduser(file_path)
            xl_file = pd.ExcelFile(expanded_path)
            sheet_names = xl_file.sheet_names
            
            # 統計每個顧問的產品銷售數量
            consultant_product_sales = {}
            
            print("\n開始統計產品銷售...")
            
            for sheet_name in sheet_names:
                print(f"正在檢查工作表: {sheet_name}")
                
                try:
                    # 讀取工作表
                    df = pd.read_excel(expanded_path, sheet_name=sheet_name, header=None)
                    
                    # 從第17行開始檢查 (F17對應index 16)
                    for row_idx in range(16, len(df)):
                        # 檢查F欄 (index 5) 是否包含 "購產品"
                        f_cell = df.iloc[row_idx, 5] if row_idx < len(df) and 5 < len(df.columns) else None
                        
                        if pd.notna(f_cell) and "購產品" in str(f_cell):
                            # 取得O欄 (index 14) 的顧問代號
                            o_cell = df.iloc[row_idx, 14] if row_idx < len(df) and 14 < len(df.columns) else None
                            
                            if pd.notna(o_cell):
                                consultant_code = str(o_cell).strip()
                                
                                # 初始化顧問的銷售計數
                                if consultant_code not in consultant_product_sales:
                                    consultant_product_sales[consultant_code] = 0
                                
                                # 增加一組產品銷售
                                consultant_product_sales[consultant_code] += 1
                                
                                print(f"  工作表 {sheet_name}, 第{row_idx+1}行: 顧問 {consultant_code} 賣出產品")
                
                except Exception as e:
                    print(f"  跳過工作表 {sheet_name}: {e}")
                    continue
            
            return consultant_product_sales
            
        except Exception as e:
            print(f"統計產品銷售時發生錯誤: {e}")
            return {}
    
    def calculate_product_bonus(self, product_sales: Dict) -> Dict:
        """計算產品達標獎金（30組以上得2000元）"""
        product_bonuses = {}
        
        print("\n產品銷售統計:")
        print("-" * 40)
        
        for consultant, sales_count in product_sales.items():
            # 達到30組以上就有2000元獎金
            bonus = 2000 if sales_count >= 30 else 0
            product_bonuses[consultant] = {
                'sales_count': sales_count,
                'bonus': bonus,
                'qualified': sales_count >= 30
            }
            
            status = "✓ 達標" if sales_count >= 30 else "✗ 未達標"
            print(f"{consultant}: {sales_count} 組 → {bonus:,}元 {status}")
        
        return product_bonuses

    def run(self):
        """主程式運行"""
        print("Only Beauty 薪資計算系統")
        print("="*40)
        print("提示：")
        print("• 輸入 'exit' 或 'quit' 可隨時退出程式")
        print("• 可使用 ~ 代表用戶主目錄，例如: ~/only_beauty_report/檔案名.xlsx")
        print("• 按 Ctrl+C 強制終止程式")
        print()
        
        try:
            # 步驟1: 輸入Excel檔案路徑
            while True:
                print("範例路徑格式:")
                print("  ~/only_beauty_report/Hsinchu202506.xlsx")
                print("  /Users/ben_kuo/Desktop/檔案名.xlsx")
                excel_path = input("\n請輸入Excel檔案路徑: ").strip()
                
                # 檢查退出命令
                if excel_path.lower() in ['exit', 'quit', 'q']:
                    print("程式已退出")
                    return
                
                if self.load_excel(excel_path):
                    break
                print("請重新輸入正確的檔案路徑\n")
            
            # 步驟2: 輸入美容師/護士人數
            while True:
                try:
                    staff_input = input("請輸入美容師/護士總人數: ").strip()
                    
                    # 檢查退出命令
                    if staff_input.lower() in ['exit', 'quit', 'q']:
                        print("程式已退出")
                        return
                    
                    staff_count = int(staff_input)
                    if staff_count > 0:
                        self.staff_count = staff_count
                        break
                    else:
                        print("人數必須大於0")
                except ValueError:
                    print("請輸入有效的數字")
            
            # 步驟3: 輸入店長名稱
            while True:
                manager_input = input("請輸入店長名稱 (如果沒有店長請輸入 'none'): ").strip()
                
                # 檢查退出命令
                if manager_input.lower() in ['exit', 'quit', 'q']:
                    print("程式已退出")
                    return
                
                if manager_input.lower() == 'none':
                    self.manager_name = None
                    print("已設定無店長")
                    break
                elif manager_input:
                    self.manager_name = manager_input
                    print(f"店長設定為: {self.manager_name}")
                    break
                else:
                    print("請輸入店長名稱或 'none'")
            
            # 步驟4: 統計產品銷售並計算產品達標獎金
            print("\n開始統計產品銷售...")
            product_sales = self.get_product_sales_statistics(excel_path)
            product_bonuses = self.calculate_product_bonus(product_sales)
            
            # 步驟5: 計算團體獎金（考慮產品達標狀況）
            print("\n開始計算團體獎金...")
            consultant_bonuses = self.calculate_consultant_bonus(product_bonuses)
            staff_bonuses = self.calculate_staff_bonus()
            
            # 步驟6: 計算個人獎金
            individual_bonuses = self.calculate_individual_bonus(consultant_bonuses)
            
            # 步驟7: 顯示結果
            self.display_results(consultant_bonuses, staff_bonuses, product_bonuses, individual_bonuses)
            
        except KeyboardInterrupt:
            print("\n\n程式已被用戶中斷 (Ctrl+C)")
            print("感謝使用 Only Beauty 薪資計算系統！")
        except EOFError:
            print("\n\n程式已結束")
            print("感謝使用 Only Beauty 薪資計算系統！")

if __name__ == "__main__":
    calculator = OnlyBeautySalaryCalculator()
    calculator.run()
