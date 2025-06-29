// Dynamic database API client
let currentToken = '';
let currentSchema = '';
let currentTable = '';
let tableColumns = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    setupTokenHandling();
    loadSchemas();
});

function setupTokenHandling() {
    const tokenInput = document.getElementById('apiToken');
    const toggleBtn = document.getElementById('toggleToken');
    
    // Toggle token visibility
    toggleBtn.addEventListener('click', function() {
        const icon = this.querySelector('i');
        if (tokenInput.type === 'password') {
            tokenInput.type = 'text';
            icon.className = 'fas fa-eye-slash';
        } else {
            tokenInput.type = 'password';
            icon.className = 'fas fa-eye';
        }
    });
    
    // Update token on input
    tokenInput.addEventListener('input', function() {
        currentToken = this.value.trim();
    });
}

// API request wrapper
async function makeRequest(url, options = {}) {
    if (!currentToken) {
        throw new Error('Bearer токен не указан');
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${currentToken}`
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    if (finalOptions.headers) {
        finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
    }
    
    const response = await fetch(url, finalOptions);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
    }
    
    return data;
}

// Load schemas
async function loadSchemas() {
    try {
        showLoading('Загрузка схем...');
        const data = await makeRequest('/api/db/schemas');
        
        const select = document.getElementById('schemaSelect');
        select.innerHTML = '<option value="">Выберите схему</option>';
        
        data.schemas.forEach(schema => {
            const option = document.createElement('option');
            option.value = schema;
            option.textContent = schema;
            select.appendChild(option);
        });
        
        showSuccess(`Загружено ${data.count} схем`);
        
    } catch (error) {
        showError('Ошибка загрузки схем: ' + error.message);
    }
}

// Load tables for selected schema
async function loadTables() {
    const schemaSelect = document.getElementById('schemaSelect');
    const tableSelect = document.getElementById('tableSelect');
    
    currentSchema = schemaSelect.value;
    
    if (!currentSchema) {
        tableSelect.innerHTML = '<option value="">Выберите таблицу</option>';
        hideColumns();
        return;
    }
    
    try {
        showLoading('Загрузка таблиц...');
        const data = await makeRequest(`/api/db/schemas/${currentSchema}/tables`);
        
        tableSelect.innerHTML = '<option value="">Выберите таблицу</option>';
        
        data.tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table;
            tableSelect.appendChild(option);
        });
        
        showSuccess(`Загружено ${data.count} таблиц для схемы ${currentSchema}`);
        hideColumns();
        
    } catch (error) {
        showError('Ошибка загрузки таблиц: ' + error.message);
    }
}

// Load columns for selected table
async function loadColumns() {
    const tableSelect = document.getElementById('tableSelect');
    currentTable = tableSelect.value;
    
    if (!currentTable) {
        hideColumns();
        return;
    }
    
    try {
        showLoading('Загрузка колонок...');
        const data = await makeRequest(`/api/db/schemas/${currentSchema}/tables/${currentTable}/columns`);
        
        tableColumns = data.columns;
        showColumns(data.columns);
        showDataOperations();
        
        showSuccess(`Загружено ${data.count} колонок для таблицы ${currentTable}`);
        
    } catch (error) {
        showError('Ошибка загрузки колонок: ' + error.message);
    }
}

// Show columns information
function showColumns(columns) {
    const columnsInfo = document.getElementById('columnsInfo');
    const columnsList = document.getElementById('columnsList');
    
    let html = '<div class="table-responsive"><table class="table table-sm table-dark">';
    html += '<thead><tr><th>Название</th><th>Тип</th><th>Nullable</th><th>По умолчанию</th></tr></thead><tbody>';
    
    columns.forEach(col => {
        html += `<tr>
            <td><code>${col.name}</code></td>
            <td>${col.type}</td>
            <td>${col.nullable ? 'Да' : 'Нет'}</td>
            <td>${col.default || '-'}</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    columnsList.innerHTML = html;
    columnsInfo.style.display = 'block';
}

function hideColumns() {
    document.getElementById('columnsInfo').style.display = 'none';
    document.getElementById('dataOperations').style.display = 'none';
}

function showDataOperations() {
    document.getElementById('dataOperations').style.display = 'block';
}

// Load table data
async function loadTableData() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    try {
        showLoading('Загрузка данных...');
        const data = await makeRequest(`/api/db/schemas/${currentSchema}/tables/${currentTable}/data?limit=50`);
        
        displayTableData(data.data);
        
    } catch (error) {
        showError('Ошибка загрузки данных: ' + error.message);
    }
}

// Perform search by single column
async function performSearch() {
    const column = document.getElementById('searchColumn').value.trim();
    const value = document.getElementById('searchValue').value.trim();
    const limit = parseInt(document.getElementById('searchLimit').value) || 50;
    const offset = parseInt(document.getElementById('searchOffset').value) || 0;
    
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    if (!column || !value) {
        showError('Укажите колонку и значение для поиска');
        return;
    }
    
    try {
        showLoading(`Поиск по ${column} = ${value}...`);
        
        const filters = {};
        filters[column] = value;
        
        const data = await makeRequest('/api/db/search', {
            method: 'POST',
            body: JSON.stringify({
                schema: currentSchema,
                table: currentTable,
                filters: filters,
                limit: limit,
                offset: offset
            })
        });
        
        displaySearchResults(data);
        
    } catch (error) {
        showError('Ошибка поиска: ' + error.message);
    }
}

// Perform search with multiple filters
async function performMultipleSearch() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    const filters = {};
    const filterRows = document.querySelectorAll('.filter-row');
    
    filterRows.forEach(row => {
        const column = row.querySelector('.filter-column').value.trim();
        const value = row.querySelector('.filter-value').value.trim();
        
        if (column && value) {
            filters[column] = value;
        }
    });
    
    if (Object.keys(filters).length === 0) {
        showError('Добавьте хотя бы один фильтр');
        return;
    }
    
    try {
        showLoading('Поиск с множественными фильтрами...');
        
        const data = await makeRequest('/api/db/search', {
            method: 'POST',
            body: JSON.stringify({
                schema: currentSchema,
                table: currentTable,
                filters: filters,
                limit: 100,
                offset: 0
            })
        });
        
        displaySearchResults(data);
        
    } catch (error) {
        showError('Ошибка поиска: ' + error.message);
    }
}

// Add filter row
function addFilterRow() {
    const container = document.getElementById('filtersContainer');
    const newRow = document.createElement('div');
    newRow.className = 'filter-row mb-2';
    newRow.innerHTML = `
        <div class="row">
            <div class="col-md-5">
                <input type="text" class="form-control filter-column" placeholder="Колонка">
            </div>
            <div class="col-md-5">
                <input type="text" class="form-control filter-value" placeholder="Значение">
            </div>
            <div class="col-md-2">
                <button class="btn btn-danger btn-sm" onclick="removeFilterRow(this)">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        </div>
    `;
    container.appendChild(newRow);
}

function removeFilterRow(button) {
    button.closest('.filter-row').remove();
}

// Data operations
async function insertData() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    try {
        const jsonData = JSON.parse(document.getElementById('operationData').value);
        
        if (!jsonData.data) {
            throw new Error('JSON должен содержать поле "data"');
        }
        
        showLoading('Вставка данных...');
        
        const result = await makeRequest(`/api/db/schemas/${currentSchema}/tables/${currentTable}/data`, {
            method: 'POST',
            body: JSON.stringify(jsonData)
        });
        
        displayOperationResult(result);
        
    } catch (error) {
        showError('Ошибка вставки: ' + error.message);
    }
}

async function updateData() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    try {
        const jsonData = JSON.parse(document.getElementById('operationData').value);
        
        if (!jsonData.data || !jsonData.filters) {
            throw new Error('JSON должен содержать поля "data" и "filters"');
        }
        
        showLoading('Обновление данных...');
        
        const result = await makeRequest(`/api/db/schemas/${currentSchema}/tables/${currentTable}/data`, {
            method: 'PUT',
            body: JSON.stringify(jsonData)
        });
        
        displayOperationResult(result);
        
    } catch (error) {
        showError('Ошибка обновления: ' + error.message);
    }
}

async function deleteData() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    try {
        const jsonData = JSON.parse(document.getElementById('operationData').value);
        
        if (!jsonData.filters) {
            throw new Error('JSON должен содержать поле "filters"');
        }
        
        if (!confirm('Вы уверены, что хотите удалить данные?')) {
            return;
        }
        
        showLoading('Удаление данных...');
        
        const result = await makeRequest(`/api/db/schemas/${currentSchema}/tables/${currentTable}/data`, {
            method: 'DELETE',
            body: JSON.stringify(jsonData)
        });
        
        displayOperationResult(result);
        
    } catch (error) {
        showError('Ошибка удаления: ' + error.message);
    }
}

// Display functions
function displayTableData(data) {
    const container = document.getElementById('responseContainer');
    
    if (!data.rows || data.rows.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Данные не найдены
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="mb-3">
            <h6>Данные таблицы ${currentSchema}.${currentTable}</h6>
            <small class="text-muted">Найдено записей: ${data.count}</small>
        </div>
        <div class="table-responsive">
            <table class="table table-sm table-dark table-striped">
                <thead>
                    <tr>
    `;
    
    // Headers
    data.columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Rows
    data.rows.forEach(row => {
        html += '<tr>';
        data.columns.forEach(col => {
            const value = row[col];
            html += `<td>${value !== null ? value : '<em>null</em>'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function displaySearchResults(response) {
    const container = document.getElementById('responseContainer');
    const data = response.results;
    
    let html = `
        <div class="mb-3">
            <h6>Результаты поиска</h6>
            <div class="alert alert-success">
                <strong>Параметры:</strong><br>
                Схема: ${response.search_params.schema}<br>
                Таблица: ${response.search_params.table}<br>
                Фильтры: ${JSON.stringify(response.search_params.filters)}<br>
                Найдено: ${data.count} записей
            </div>
        </div>
    `;
    
    if (data.rows && data.rows.length > 0) {
        html += `
            <div class="table-responsive">
                <table class="table table-sm table-dark table-striped">
                    <thead><tr>
        `;
        
        data.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        data.rows.forEach(row => {
            html += '<tr>';
            data.columns.forEach(col => {
                const value = row[col];
                html += `<td>${value !== null ? value : '<em>null</em>'}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
    } else {
        html += '<div class="alert alert-warning">Записи не найдены</div>';
    }
    
    container.innerHTML = html;
}

function displayOperationResult(result) {
    const container = document.getElementById('responseContainer');
    
    let html = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle me-2"></i>${result.message}</h6>
        </div>
        <pre class="bg-dark p-3 rounded"><code>${JSON.stringify(result, null, 2)}</code></pre>
    `;
    
    container.innerHTML = html;
}

function showLoading(message) {
    const container = document.getElementById('responseContainer');
    container.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">${message}</p>
        </div>
    `;
}

function showError(message) {
    const container = document.getElementById('responseContainer');
    container.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

function showSuccess(message) {
    // Можно добавить уведомление в будущем
    console.log('Success:', message);
}

// Show insert form helper
function showInsertForm() {
    if (!currentSchema || !currentTable) {
        showError('Выберите схему и таблицу');
        return;
    }
    
    // Generate example JSON based on table columns
    const exampleData = {};
    tableColumns.forEach(col => {
        if (col.name !== 'id' && col.name !== 'created_at' && col.name !== 'updated_at') {
            switch (col.type) {
                case 'text':
                case 'character varying':
                    exampleData[col.name] = 'example_value';
                    break;
                case 'integer':
                    exampleData[col.name] = 123;
                    break;
                case 'boolean':
                    exampleData[col.name] = true;
                    break;
                default:
                    exampleData[col.name] = 'value';
            }
        }
    });
    
    const exampleJson = {
        data: exampleData
    };
    
    document.getElementById('operationData').value = JSON.stringify(exampleJson, null, 2);
    document.getElementById('dataOperations').scrollIntoView({ behavior: 'smooth' });
}