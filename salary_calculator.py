import pandas as pd
import os
from typing import Dict, List

class OnlyBeautySalaryCalculator:
    def __init__(self):
        # 業績獎金等級表
        self.performance_bonus_levels = [
            (1800000, 2500000, 0.005),
            (2500001, 4000000, 0.01),
            (4000001, 6000000, 0.025),
            (6000001, 8000000, 0.045)
        ]
        
        # 消耗獎金等級表
        self.consumption_bonus_levels = [
            (0, 1500000, 0.006),
            (1500001, 2500000, 0.01),
            (2500001, float('inf'), 0.015)
        ]
        
        self.excel_data = None
        self.consultant_count = 0
        self.staff_count = 0
        
    def load_excel(self, file_path: str) -> bool:
        """載入Excel檔案並找出數字最大的工作表"""
        try:
            if not os.path.exists(file_path):
                print(f"錯誤：檔案 {file_path} 不存在")
                return False
            
            # 讀取所有工作表名稱
            xl_file = pd.ExcelFile(file_path)
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
            self.excel_data = pd.read_excel(file_path, sheet_name=max_sheet, header=None)
            print("Excel檔案載入成功！")
            return True
            
        except Exception as e:
            print(f"載入Excel檔案時發生錯誤: {e}")
            return False
    
    def get_performance_bonus_rate(self, amount: float) -> float:
        """根據業績金額獲取業績獎金比例"""
        for min_val, max_val, rate in self.performance_bonus_levels:
            if min_val <= amount <= max_val:
                return rate
        return 0
    
    def get_consumption_bonus_rate(self, amount: float) -> float:
        """根據消耗金額獲取消耗獎金比例"""
        for min_val, max_val, rate in self.consumption_bonus_levels:
            if min_val <= amount <= max_val:
                return rate
        return 0
    
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
    
    def calculate_consultant_bonus(self) -> Dict:
        """計算顧問獎金"""
        if self.excel_data is None:
            return {}
        
        # 獲取總業績和總消耗
        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0  # E5
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0  # E7
        
        print(f"總業績 (E5): {total_performance:,.0f}")
        print(f"總消耗 (E7): {total_consumption:,.0f}")
        
        # 獲取顧問資料
        consultants = self.get_consultants_data()
        if not consultants:
            return {}
        
        print(f"找到 {len(consultants)} 位顧問")
        
        # 計算業績獎金
        performance_rate = self.get_performance_bonus_rate(total_performance)
        consultant_performance_pool = total_performance * 0.7 * performance_rate
        
        # 計算消耗獎金
        consumption_rate = self.get_consumption_bonus_rate(total_consumption)
        consultant_consumption_pool = total_consumption * 0.4 * consumption_rate
        
        print(f"業績獎金比例: {performance_rate*100}%")
        print(f"顧問業績獎金池: {consultant_performance_pool:,.0f}")
        print(f"消耗獎金比例: {consumption_rate*100}%")
        print(f"顧問消耗獎金池: {consultant_consumption_pool:,.0f}")
        
        # 計算總業績和總消耗（用於比例計算）
        total_consultant_performance = sum(c['performance'] for c in consultants)
        total_consultant_consumption = sum(c['consumption'] for c in consultants)
        
        # 計算每位顧問的獎金
        consultant_bonuses = {}
        for consultant in consultants:
            # 業績獎金分配
            if total_consultant_performance > 0:
                performance_ratio = consultant['performance'] / total_consultant_performance
                performance_bonus = consultant_performance_pool * performance_ratio
            else:
                performance_bonus = 0
            
            # 消耗獎金分配
            if total_consultant_consumption > 0:
                consumption_ratio = consultant['consumption'] / total_consultant_consumption
                consumption_bonus = consultant_consumption_pool * consumption_ratio
            else:
                consumption_bonus = 0
            
            consultant_bonuses[consultant['name']] = {
                'performance_bonus': performance_bonus,
                'consumption_bonus': consumption_bonus,
                'total_bonus': performance_bonus + consumption_bonus,
                'personal_performance': consultant['performance'],
                'personal_consumption': consultant['consumption']
            }
        
        return consultant_bonuses
    
    def calculate_staff_bonus(self) -> Dict:
        """計算美容師/護士獎金"""
        if self.excel_data is None or self.staff_count == 0:
            return {}
        
        # 獲取總業績和總消耗
        total_performance = self.excel_data.iloc[4, 4] if not pd.isna(self.excel_data.iloc[4, 4]) else 0  # E5
        total_consumption = self.excel_data.iloc[6, 4] if not pd.isna(self.excel_data.iloc[6, 4]) else 0  # E7
        
        # 計算業績獎金
        performance_rate = self.get_performance_bonus_rate(total_performance)
        staff_performance_pool = total_performance * 0.3 * performance_rate
        performance_bonus_per_person = staff_performance_pool / self.staff_count
        
        # 計算消耗獎金
        consumption_rate = self.get_consumption_bonus_rate(total_consumption)
        staff_consumption_pool = total_consumption * 0.6 * consumption_rate
        consumption_bonus_per_person = staff_consumption_pool / self.staff_count
        
        return {
            'staff_count': self.staff_count,
            'performance_pool': staff_performance_pool,
            'consumption_pool': staff_consumption_pool,
            'performance_bonus_per_person': performance_bonus_per_person,
            'consumption_bonus_per_person': consumption_bonus_per_person,
            'total_bonus_per_person': performance_bonus_per_person + consumption_bonus_per_person
        }
    
    def display_results(self, consultant_bonuses: Dict, staff_bonuses: Dict):
        """顯示計算結果"""
        print("\n" + "="*60)
        print("薪資計算結果")
        print("="*60)
        
        if consultant_bonuses:
            print("\n顧問獎金明細:")
            print("-" * 50)
            for name, bonus in consultant_bonuses.items():
                print(f"{name}:")
                print(f"  個人業績: {bonus['personal_performance']:,.0f}")
                print(f"  個人消耗: {bonus['personal_consumption']:,.0f}")
                print(f"  業績獎金: {bonus['performance_bonus']:,.0f}")
                print(f"  消耗獎金: {bonus['consumption_bonus']:,.0f}")
                print(f"  總獎金: {bonus['total_bonus']:,.0f}")
                print()
        
        if staff_bonuses:
            print("美容師/護士獎金:")
            print("-" * 50)
            print(f"總人數: {staff_bonuses['staff_count']} 人")
            print(f"業績獎金池: {staff_bonuses['performance_pool']:,.0f}")
            print(f"消耗獎金池: {staff_bonuses['consumption_pool']:,.0f}")
            print(f"每人業績獎金: {staff_bonuses['performance_bonus_per_person']:,.0f}")
            print(f"每人消耗獎金: {staff_bonuses['consumption_bonus_per_person']:,.0f}")
            print(f"每人總獎金: {staff_bonuses['total_bonus_per_person']:,.0f}")
    
    def run(self):
        """主程式運行"""
        print("Only Beauty 薪資計算系統")
        print("="*40)
        
        # 步驟1: 輸入Excel檔案路徑
        while True:
            excel_path = input("請輸入Excel檔案路徑: ").strip()
            if self.load_excel(excel_path):
                break
            print("請重新輸入正確的檔案路徑\n")
        
        # 步驟2: 輸入美容師/護士人數
        while True:
            try:
                staff_count = int(input("請輸入美容師/護士總人數: "))
                if staff_count > 0:
                    self.staff_count = staff_count
                    break
                else:
                    print("人數必須大於0")
            except ValueError:
                print("請輸入有效的數字")
        
        # 步驟3: 計算獎金
        print("\n開始計算獎金...")
        consultant_bonuses = self.calculate_consultant_bonus()
        staff_bonuses = self.calculate_staff_bonus()
        
        # 步驟4: 顯示結果
        self.display_results(consultant_bonuses, staff_bonuses)

if __name__ == "__main__":
    calculator = OnlyBeautySalaryCalculator()
    calculator.run()
