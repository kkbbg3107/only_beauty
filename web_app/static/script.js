// 全域變數
let uploadedFile = null;
let calculationResults = null;

// DOM 載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeForm();
});

// 初始化檔案上傳功能
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // 點擊上傳區域觸發檔案選擇
    uploadArea.addEventListener('click', function(e) {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    // 檔案選擇事件
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    // 拖拽事件
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isValidExcelFile(file)) {
                handleFileUpload(file);
            } else {
                showError('請選擇有效的Excel檔案 (.xlsx 或 .xls)');
            }
        }
    });
}

// 驗證Excel檔案
function isValidExcelFile(file) {
    const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel' // .xls
    ];

    const validExtensions = ['.xlsx', '.xls'];
    const fileName = file.name.toLowerCase();
    const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

    return validTypes.includes(file.type) || hasValidExtension;
}

// 處理檔案上傳
function handleFileUpload(file) {
    if (!isValidExcelFile(file)) {
        showError('請選擇有效的Excel檔案 (.xlsx 或 .xls)');
        return;
    }

    uploadedFile = file;

    // 顯示檔案資訊
    showFileStatus(`已選擇檔案: ${file.name} (${formatFileSize(file.size)})`, 'success');

    // 模擬Excel解析進度
    simulateExcelParsing().then(() => {
        // 解析完成，顯示下一步
        showStep(2);
    });
}

// 模擬Excel解析進度
function simulateExcelParsing() {
    return new Promise((resolve) => {
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        progressContainer.style.display = 'block';

        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15 + 5; // 隨機增加5-20%

            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);

                progressFill.style.width = '100%';
                progressText.textContent = '解析完成！';

                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    resolve();
                }, 1000);
            } else {
                progressFill.style.width = progress + '%';
                progressText.textContent = `解析中... ${Math.round(progress)}%`;
            }
        }, 200);
    });
}

// 格式化檔案大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 顯示檔案狀態
function showFileStatus(message, type) {
    const fileStatus = document.getElementById('fileStatus');
    fileStatus.textContent = message;
    fileStatus.className = `file-status ${type}`;
}

// 初始化表單
function initializeForm() {
    const configForm = document.getElementById('configForm');
    configForm.addEventListener('submit', function(e) {
        e.preventDefault();
        startCalculation();
    });
}

// 開始計算
function startCalculation() {
    const staffCount = document.getElementById('staffCount').value;
    const managerName = document.getElementById('managerName').value;
    const highTarget = document.getElementById('highTarget').value;

    // 驗證必填欄位
    if (!staffCount || staffCount < 1) {
        showError('請輸入有效的員工人數');
        return;
    }

    if (!uploadedFile) {
        showError('請先上傳Excel檔案');
        return;
    }

    // 顯示計算步驟
    showStep(3);

    // 準備表單資料
    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('staff_count', staffCount);
    formData.append('manager_name', managerName || '');
    formData.append('high_target', highTarget || '');

    // 開始計算進度動畫
    startCalculationProgress();

    // 發送到後端處理
    fetch('/calculate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            calculationResults = data.results;
            displayResults(data.results);
            showStep(4);
        } else {
            showError(data.error || '計算過程發生錯誤');
            showStep(2); // 回到設定頁面
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('網路錯誤或伺服器無回應');
        showStep(2); // 回到設定頁面
    });
}

// 開始計算進度動畫
function startCalculationProgress() {
    const steps = ['product', 'team', 'individual', 'salary'];
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            // 更新當前步驟狀態
            updateProgressStep(steps[currentStep], 'active', '計算中...');

            // 模擬計算時間
            setTimeout(() => {
                updateProgressStep(steps[currentStep], 'completed', '完成');
                currentStep++;

                if (currentStep >= steps.length) {
                    clearInterval(interval);
                }
            }, 1500 + Math.random() * 1000); // 1.5-2.5秒
        }
    }, 2000);
}

// 更新進度步驟狀態
function updateProgressStep(stepId, status, statusText) {
    const stepElement = document.getElementById(`step-${stepId}`);
    const statusElement = document.getElementById(`status-${stepId}`);

    stepElement.className = `progress-step ${status}`;
    statusElement.textContent = statusText;
}

// 顯示指定步驟
function showStep(stepNumber) {
    // 隱藏所有步驟
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => {
        step.style.display = 'none';
    });

    // 顯示指定步驟
    const targetStep = document.getElementById(`step${stepNumber}`);
    if (targetStep) {
        targetStep.style.display = 'block';
    }
}

// 顯示結果
function displayResults(results) {
    displayConsultantResults(results.consultant_bonuses);
    displayStaffResults(results.staff_bonuses);
    displaySalaryResults(results.individual_staff_salaries);
    displaySummaryResults(results);
}

// 顯示顧問結果
function displayConsultantResults(consultants) {
    const container = document.getElementById('consultantResults');

    if (!consultants || Object.keys(consultants).length === 0) {
        container.innerHTML = '<p>無顧問資料</p>';
        return;
    }

    let html = '';

    Object.entries(consultants).forEach(([name, data]) => {
        const totalBonus = data.performance_bonus + data.consumption_bonus;

        html += `
            <div class="result-card">
                <h4>${name}</h4>
                <div class="result-item">
                    <span class="result-label">個人業績:</span>
                    <span class="result-value currency">${formatCurrency(data.personal_performance)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">個人消耗:</span>
                    <span class="result-value currency">${formatCurrency(data.personal_consumption)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">團體業績獎金:</span>
                    <span class="result-value currency">${formatCurrency(data.performance_bonus)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">團體消耗獎金:</span>
                    <span class="result-value currency">${formatCurrency(data.consumption_bonus)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">總獎金:</span>
                    <span class="result-value result-highlight currency">${formatCurrency(totalBonus)}</span>
                </div>
                ${!data.product_qualified ? '<div style="color: #f56565; font-weight: 600;">⚠️ 產品未達標，團體獎金已清零</div>' : ''}
            </div>
        `;
    });

    container.innerHTML = html;
}

// 顯示員工結果
function displayStaffResults(staffData) {
    const container = document.getElementById('staffResults');

    if (!staffData) {
        container.innerHTML = '<p>無員工獎金資料</p>';
        return;
    }

    const html = `
        <div class="result-card">
            <h4>美容師/護理師團體獎金</h4>
            <div class="result-item">
                <span class="result-label">總人數:</span>
                <span class="result-value">${staffData.staff_count} 人</span>
            </div>
            <div class="result-item">
                <span class="result-label">業績獎金池:</span>
                <span class="result-value currency">${formatCurrency(staffData.performance_pool)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">消耗獎金池:</span>
                <span class="result-value currency">${formatCurrency(staffData.consumption_pool)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">每人業績獎金:</span>
                <span class="result-value currency">${formatCurrency(staffData.performance_bonus_per_person)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">每人消耗獎金:</span>
                <span class="result-value currency">${formatCurrency(staffData.consumption_bonus_per_person)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">每人總獎金:</span>
                <span class="result-value result-highlight currency">${formatCurrency(staffData.total_bonus_per_person)}</span>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// 顯示薪資明細
function displaySalaryResults(salaries) {
    const container = document.getElementById('salaryResults');

    if (!salaries || Object.keys(salaries).length === 0) {
        container.innerHTML = '<p>無薪資明細資料</p>';
        return;
    }

    // 按職位分組
    const positions = ['美容師', '護理師', '櫃檯'];
    let html = '';

    positions.forEach(position => {
        const positionStaff = Object.entries(salaries).filter(([name, data]) => data.position === position);

        if (positionStaff.length > 0) {
            html += `<h4>${position}</h4>`;

            positionStaff.forEach(([name, data]) => {
                html += `
                    <div class="result-card">
                        <h4>${name} (第${data.row}行)</h4>
                        <div class="result-item">
                            <span class="result-label">底薪:</span>
                            <span class="result-value currency">${formatCurrency(data.base_salary)}</span>
                        </div>
                `;

                if (data.hand_skill_bonus > 0) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">手技獎金:</span>
                            <span class="result-value currency">${formatCurrency(data.hand_skill_bonus)}</span>
                        </div>
                    `;
                }

                if (data.license_allowance > 0) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">執照津貼:</span>
                            <span class="result-value currency">${formatCurrency(data.license_allowance)}</span>
                        </div>
                    `;
                }

                if (data.rank_bonus > 0) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">職等獎金:</span>
                            <span class="result-value currency">${formatCurrency(data.rank_bonus)}</span>
                        </div>
                    `;
                }

                if (data.position_allowance > 0) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">職務津貼:</span>
                            <span class="result-value currency">${formatCurrency(data.position_allowance)}</span>
                        </div>
                    `;
                }

                // 櫃檯特殊獎金
                if (position === '櫃檯') {
                    if (data.high_target_bonus > 0) {
                        html += `
                            <div class="result-item">
                                <span class="result-label">高標達標獎金:</span>
                                <span class="result-value currency">${formatCurrency(data.high_target_bonus)}</span>
                            </div>
                        `;
                    }

                    if (data.consumption_achievement_bonus > 0) {
                        html += `
                            <div class="result-item">
                                <span class="result-label">門店業績達標+消耗300萬獎金:</span>
                                <span class="result-value currency">${formatCurrency(data.consumption_achievement_bonus)}</span>
                            </div>
                        `;
                    }

                    if (data.performance_500w_bonus > 0) {
                        html += `
                            <div class="result-item">
                                <span class="result-label">業績500萬獎金:</span>
                                <span class="result-value currency">${formatCurrency(data.performance_500w_bonus)}</span>
                            </div>
                        `;
                    }

                    if (data.store_performance_incentive > 0) {
                        html += `
                            <div class="result-item">
                                <span class="result-label">門店業績激勵獎金:</span>
                                <span class="result-value currency">${formatCurrency(data.store_performance_incentive)}</span>
                            </div>
                        `;
                    }
                }

                html += `
                        <div class="result-item" style="border-top: 2px solid #e2e8f0; padding-top: 10px; margin-top: 10px;">
                            <span class="result-label"><strong>當月總薪資:</strong></span>
                            <span class="result-value result-highlight currency">${formatCurrency(data.total_salary)}</span>
                        </div>
                    </div>
                `;

                // 不計入當月總薪資的項目
                if (position !== '櫃檯') {
                    const separateItems = [];
                    if (data.team_performance_bonus > 0) {
                        separateItems.push(`團體業績獎金: ${formatCurrency(data.team_performance_bonus)}`);
                    }
                    if (data.team_consumption_bonus > 0) {
                        separateItems.push(`團體消耗獎金: ${formatCurrency(data.team_consumption_bonus)}`);
                    }
                    if (position === '護理師' && data.full_attendance_bonus > 0) {
                        separateItems.push(`全勤獎金: ${formatCurrency(data.full_attendance_bonus)}`);
                    }
                    if (data.high_target_bonus > 0) {
                        separateItems.push(`高標達標獎金: ${formatCurrency(data.high_target_bonus)}`);
                    }

                    if (separateItems.length > 0) {
                        html += `
                            <div class="result-card" style="background: #fff3cd; border-left-color: #ffc107;">
                                <h5>不計入當月總薪資的項目:</h5>
                                ${separateItems.map(item => `<div style="margin: 5px 0;">${item}</div>`).join('')}
                            </div>
                        `;
                    }
                }
            });
        }
    });

    container.innerHTML = html;
}

// 顯示統計摘要
function displaySummaryResults(results) {
    const container = document.getElementById('summaryResults');

    // 計算總計數據
    let totalConsultantBonus = 0;
    let totalConsultants = 0;

    if (results.consultant_bonuses) {
        Object.values(results.consultant_bonuses).forEach(data => {
            totalConsultantBonus += data.performance_bonus + data.consumption_bonus;
            totalConsultants++;
        });
    }

    let totalStaffSalary = 0;
    let totalStaff = 0;

    if (results.individual_staff_salaries) {
        Object.values(results.individual_staff_salaries).forEach(data => {
            totalStaffSalary += data.total_salary;
            totalStaff++;
        });
    }

    const html = `
        <div class="result-card">
            <h4>總計統計</h4>
            <div class="result-item">
                <span class="result-label">顧問人數:</span>
                <span class="result-value">${totalConsultants} 人</span>
            </div>
            <div class="result-item">
                <span class="result-label">顧問總獎金:</span>
                <span class="result-value currency">${formatCurrency(totalConsultantBonus)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">員工人數:</span>
                <span class="result-value">${totalStaff} 人</span>
            </div>
            <div class="result-item">
                <span class="result-label">員工總薪資:</span>
                <span class="result-value currency">${formatCurrency(totalStaffSalary)}</span>
            </div>
            <div class="result-item" style="border-top: 2px solid #e2e8f0; padding-top: 10px; margin-top: 10px;">
                <span class="result-label"><strong>總支出:</strong></span>
                <span class="result-value result-highlight currency">${formatCurrency(totalConsultantBonus + totalStaffSalary)}</span>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// 格式化貨幣
function formatCurrency(amount) {
    if (typeof amount !== 'number') {
        amount = parseFloat(amount) || 0;
    }
    return amount.toLocaleString('zh-TW');
}

// 選項卡切換
function showTab(tabName) {
    // 隱藏所有選項卡內容
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // 移除所有選項卡按鈕的active class
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });

    // 顯示指定選項卡
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // 設定對應按鈕為active
    const activeButton = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// 重新計算
function resetCalculation() {
    uploadedFile = null;
    calculationResults = null;

    // 重置表單
    document.getElementById('configForm').reset();
    document.getElementById('fileInput').value = '';
    document.getElementById('fileStatus').textContent = '';
    document.getElementById('fileStatus').className = 'file-status';

    // 回到第一步
    showStep(1);
}

// 匯出結果
function exportResults() {
    if (!calculationResults) {
        showError('沒有可匯出的結果');
        return;
    }

    // 這裡可以實作匯出功能，例如：
    // 1. 產生Excel檔案
    // 2. 產生PDF報告
    // 3. 產生JSON格式

    alert('匯出功能開發中...');

    // 簡單的JSON匯出示例
    const dataStr = JSON.stringify(calculationResults, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'salary_calculation_results.json';
    link.click();

    URL.revokeObjectURL(url);
}

// 顯示錯誤訊息
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    errorText.textContent = message;
    errorMessage.style.display = 'block';

    // 5秒後自動隱藏
    setTimeout(() => {
        hideError();
    }, 5000);
}

// 隱藏錯誤訊息
function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.style.display = 'none';
}

// 顯示載入遮罩
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex';
}

// 隱藏載入遮罩
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'none';
}