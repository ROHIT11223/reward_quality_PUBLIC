// State Management
let configData = {
    rdes: [],
    errors: []
};

let currentCounts = {};
let recordsDatabase = [];

// DOM Elements
const configFile = document.getElementById('configFile');
const fileStatus = document.getElementById('file-status');
const mainForm = document.getElementById('main-form');
const rdeSelect = document.getElementById('rdeName');
const errorList = document.getElementById('error-list');
const docNameInput = document.getElementById('docName');
const bonusInput = document.getElementById('bonusPoints');
const previewScore = document.getElementById('previewScore');
const submitBtn = document.getElementById('submitBtn');
const exportBtn = document.getElementById('exportBtn');

// Event Listeners
configFile.addEventListener('change', handleFileUpload);
bonusInput.addEventListener('input', updateScore);
submitBtn.addEventListener('click', submitRecord);
exportBtn.addEventListener('click', exportDatabase);

function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    fileStatus.textContent = file.name;
    const reader = new FileReader();

    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            
            // Assume first sheet contains the config
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            
            // Convert to JSON
            const json = XLSX.utils.sheet_to_json(worksheet);
            
            parseConfig(json);
            showNotification('Configuration loaded successfully!', 'success');
        } catch (error) {
            console.error(error);
            showNotification('Error parsing file. Ensure it has RDE_Name, Error_Name, and Error_Weight columns.', 'error');
        }
    };
    reader.readAsArrayBuffer(file);
}

function parseConfig(data) {
    configData.rdes = [];
    configData.errors = [];
    
    data.forEach(row => {
        if (row.RDE_Name) {
            configData.rdes.push(row.RDE_Name);
        }
        if (row.Error_Name && row.Error_Weight !== undefined) {
            configData.errors.push({
                name: row.Error_Name,
                weight: Number(row.Error_Weight)
            });
        }
    });

    // Remove duplicates from RDEs
    configData.rdes = [...new Set(configData.rdes)];

    // If more than 10 errors, just take the first 10 as per requirements
    if (configData.errors.length > 10) {
        configData.errors = configData.errors.slice(0, 10);
    }

    renderUI();
}

function renderUI() {
    // Populate RDE Dropdown
    rdeSelect.innerHTML = '<option value="" disabled selected>Select User...</option>';
    configData.rdes.forEach(rde => {
        const option = document.createElement('option');
        option.value = rde;
        option.textContent = rde;
        rdeSelect.appendChild(option);
    });

    // Render Errors
    errorList.innerHTML = '';
    currentCounts = {};
    
    configData.errors.forEach((err, index) => {
        const errId = `error_${index + 1}`;
        currentCounts[errId] = 0; // Initialize count

        const item = document.createElement('div');
        item.className = 'error-item';
        item.innerHTML = `
            <div class="error-info">
                <span class="error-name">${err.name}</span>
                <span class="error-weight">Weight: ${err.weight}</span>
            </div>
            <div class="counter-controls">
                <button class="counter-btn minus" onclick="changeCount('${errId}', -1)">-</button>
                <span class="count-display" id="${errId}_count">0</span>
                <button class="counter-btn plus" onclick="changeCount('${errId}', 1)">+</button>
            </div>
        `;
        errorList.appendChild(item);
    });

    // Show the form
    mainForm.classList.remove('hidden');
    updateScore();
}

// Make globally available for inline onclick attributes
window.changeCount = function(errId, delta) {
    const newVal = currentCounts[errId] + delta;
    if (newVal >= 0) {
        currentCounts[errId] = newVal;
        document.getElementById(`${errId}_count`).textContent = newVal;
        updateScore();
    }
};

function updateScore() {
    let score = 0; // Starting from 0 as base

    // Add bonus
    const bonus = Number(bonusInput.value) || 0;
    score += bonus;

    // Apply error deductions
    configData.errors.forEach((err, index) => {
        const errId = `error_${index + 1}`;
        const count = currentCounts[errId];
        // Weight is assumed to be negative, so we add it (count * weight)
        // E.g., 2 * -5 = -10
        score += (count * err.weight);
    });

    previewScore.textContent = score;
}

function submitRecord() {
    const docName = docNameInput.value.trim();
    const rdeName = rdeSelect.value;

    if (!docName || !rdeName) {
        showNotification('Please fill in Document Name and select a User.', 'error');
        return;
    }

    // Build the record object
    const record = {
        Document_Name: docName,
        RDE_Name: rdeName
    };

    let totalErrors = 0;
    configData.errors.forEach((err, index) => {
        const errId = `error_${index + 1}`;
        record[`Error_${index + 1}_(${err.name})`] = currentCounts[errId];
        totalErrors += currentCounts[errId];
    });

    record['bonus_point'] = Number(bonusInput.value) || 0;
    record['total_points'] = Number(previewScore.textContent);
    record['Timestamp'] = new Date().toLocaleString();

    recordsDatabase.push(record);
    showNotification('Record submitted successfully! You can download the DB anytime.', 'success');
    
    // Reset Form
    docNameInput.value = '';
    rdeSelect.value = '';
    bonusInput.value = '0';
    configData.errors.forEach((err, index) => {
        const errId = `error_${index + 1}`;
        currentCounts[errId] = 0;
        document.getElementById(`${errId}_count`).textContent = '0';
    });
    updateScore();
}

function exportDatabase() {
    if (recordsDatabase.length === 0) {
        showNotification('No records to export yet!', 'error');
        return;
    }

    const worksheet = XLSX.utils.json_to_sheet(recordsDatabase);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Records");
    
    XLSX.writeFile(workbook, "Quality_Reward_Records.xlsx");
    showNotification('Database downloaded successfully!', 'success');
}

function showNotification(message, type) {
    const notif = document.getElementById('notification');
    notif.textContent = message;
    notif.className = `notification ${type}`;
    
    setTimeout(() => {
        notif.classList.add('hidden');
    }, 3000);
}
