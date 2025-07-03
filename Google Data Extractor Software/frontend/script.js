// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
    START_SCRAPING: `${API_BASE_URL}/start_scraping`,
    GET_PROGRESS: (sessionId) => `${API_BASE_URL}/progress/${sessionId}`,
    GET_RESULTS: (sessionId) => `${API_BASE_URL}/results/${sessionId}`,
    DOWNLOAD_CSV: (sessionId) => `${API_BASE_URL}/download_csv/${sessionId}`,
    DOWNLOAD_JSON: (sessionId) => `${API_BASE_URL}/download_json/${sessionId}`
};

// DOM Elements
const elements = {
    form: document.getElementById('scrapeForm'),
    startButton: document.getElementById('startButton'),
    cancelButton: document.getElementById('cancelButton'),
    retryButton: document.getElementById('retryButton'),
    downloadCsv: document.getElementById('downloadCsv'),
    downloadJson: document.getElementById('downloadJson'),
    progressSection: document.getElementById('progressSection'),
    resultsSection: document.getElementById('resultsSection'),
    errorSection: document.getElementById('errorSection'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    progressDetails: document.getElementById('progressDetails'),
    statusText: document.getElementById('statusText'),
    spinner: document.getElementById('spinner'),
    errorMessage: document.getElementById('errorMessage'),
    resultsTableBody: document.getElementById('resultsTableBody'),
    summaryKeywords: document.getElementById('summaryKeywords'),
    summaryLocation: document.getElementById('summaryLocation'),
    summaryTotal: document.getElementById('summaryTotal')
};

// State management
let currentState = {
    sessionId: null,
    isRunning: false,
    progressInterval: null,
    keywords: '',
    location: '',
    maxResults: 0
};

// Event Listeners
elements.form.addEventListener('submit', handleFormSubmit);
elements.cancelButton.addEventListener('click', handleCancel);
elements.retryButton.addEventListener('click', handleRetry);
elements.downloadCsv.addEventListener('click', () => handleDownload('csv'));
elements.downloadJson.addEventListener('click', () => handleDownload('json'));

// Form submission handler
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        keywords: formData.get('keywords'),
        location: formData.get('location'),
        max_results: parseInt(formData.get('maxResults'))
    };
    
    // Save to state
    currentState.keywords = data.keywords;
    currentState.location = data.location;
    currentState.maxResults = data.max_results;
    
    try {
        // Start scraping
        const response = await fetch(API_ENDPOINTS.START_SCRAPING, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Failed to start scraping');
        }
        
        const result = await response.json();
        currentState.sessionId = result.session_id;
        
        // Show progress section
        showSection('progress');
        startProgressTracking();
        
    } catch (error) {
        showError(error.message);
    }
}

// Progress tracking
function startProgressTracking() {
    currentState.isRunning = true;
    
    // Clear any existing interval
    if (currentState.progressInterval) {
        clearInterval(currentState.progressInterval);
    }
    
    // Start new tracking interval
    currentState.progressInterval = setInterval(checkProgress, 1000);
}

async function checkProgress() {
    if (!currentState.isRunning || !currentState.sessionId) {
        return;
    }
    
    try {
        const response = await fetch(API_ENDPOINTS.GET_PROGRESS(currentState.sessionId));
        const progress = await response.json();
        
        updateProgress(progress);
        
        // Check if scraping is complete or failed
        if (progress.status === 'completed') {
            await handleCompletion();
        } else if (progress.status === 'error') {
            showError(progress.error_message || 'Scraping failed');
        }
        
    } catch (error) {
        showError('Failed to fetch progress');
    }
}

function updateProgress(progress) {
    const percentage = Math.round((progress.completed / progress.total) * 100);
    
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = `${percentage}%`;
    elements.progressDetails.textContent = `${progress.completed} of ${progress.total} results`;
    elements.statusText.textContent = capitalizeFirstLetter(progress.status);
}

// Handle scraping completion
async function handleCompletion() {
    stopProgressTracking();
    
    try {
        const response = await fetch(API_ENDPOINTS.GET_RESULTS(currentState.sessionId));
        const data = await response.json();
        
        // Update summary
        elements.summaryKeywords.textContent = currentState.keywords;
        elements.summaryLocation.textContent = currentState.location;
        elements.summaryTotal.textContent = data.total_results;
        
        // Populate results table
        populateResultsTable(data.results);
        
        // Show results section
        showSection('results');
        
    } catch (error) {
        showError('Failed to fetch results');
    }
}

function populateResultsTable(results) {
    elements.resultsTableBody.innerHTML = '';
    
    results.forEach((result, index) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${escapeHtml(result.name)}</td>
            <td>${escapeHtml(result.address)}</td>
            <td>${escapeHtml(result.phone)}</td>
            <td>
                <div class="rating">
                    <span class="stars">${getStarRating(result.rating)}</span>
                    <span>${result.rating}</span>
                </div>
            </td>
            <td>${formatReviewCount(result.reviews_count)}</td>
            <td>${formatCategories(result.categories)}</td>
            <td>${formatWebsite(result.website)}</td>
        `;
        
        elements.resultsTableBody.appendChild(row);
    });
}

// Handle download requests
async function handleDownload(format) {
    if (!currentState.sessionId) return;
    
    const endpoint = format === 'csv' 
        ? API_ENDPOINTS.DOWNLOAD_CSV(currentState.sessionId)
        : API_ENDPOINTS.DOWNLOAD_JSON(currentState.sessionId);
    
    try {
        window.location.href = endpoint;
    } catch (error) {
        showError(`Failed to download ${format.toUpperCase()} file`);
    }
}

// Cancel and retry handlers
function handleCancel() {
    stopProgressTracking();
    showSection('form');
}

function handleRetry() {
    stopProgressTracking();
    showSection('form');
}

// Helper functions
function showSection(section) {
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
    
    switch (section) {
        case 'progress':
            elements.progressSection.style.display = 'block';
            break;
        case 'results':
            elements.resultsSection.style.display = 'block';
            break;
        case 'error':
            elements.errorSection.style.display = 'block';
            break;
    }
}

function showError(message) {
    stopProgressTracking();
    elements.errorMessage.textContent = message;
    showSection('error');
}

function stopProgressTracking() {
    currentState.isRunning = false;
    if (currentState.progressInterval) {
        clearInterval(currentState.progressInterval);
        currentState.progressInterval = null;
    }
}

function getStarRating(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    return '*'.repeat(fullStars) + 
           (halfStar ? '.' : '') + 
           '-'.repeat(emptyStars);
}

function formatReviewCount(count) {
    return count ? count.toLocaleString() : '0';
}

function formatCategories(categories) {
    if (!categories || !categories.length) return '-';
    return categories.join(', ');
}

function formatWebsite(url) {
    if (!url) return '-';
    return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">Visit Site</a>`;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function escapeHtml(unsafe) {
    if (!unsafe) return '-';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '<')
        .replace(/>/g, '>')
        .replace(/"/g, '"')
        .replace(/'/g, '&#039;');
}
