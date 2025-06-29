// API testing functionality
let currentToken = '';

// Toggle token visibility
document.getElementById('toggleToken').addEventListener('click', function() {
    const tokenInput = document.getElementById('apiToken');
    const icon = this.querySelector('i');
    
    if (tokenInput.type === 'password') {
        tokenInput.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        tokenInput.type = 'password';
        icon.className = 'fas fa-eye';
    }
});

// Get admin token
document.getElementById('getAdminToken').addEventListener('click', async function() {
    const btn = this;
    const originalText = btn.innerHTML;
    
    try {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        btn.disabled = true;
        
        // Make request to get admin token from server logs
        // In a real application, this would be handled differently
        showNotification('Admin token should be available in server logs when the application starts.', 'info');
        
        // For demo purposes, let's try to get health check first
        const response = await fetch('/api/health');
        if (response.ok) {
            showNotification('Server is running. Check server logs for the admin token.', 'info');
        }
        
    } catch (error) {
        showNotification('Error connecting to server: ' + error.message, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Update current token when input changes
document.getElementById('apiToken').addEventListener('input', function() {
    currentToken = this.value.trim();
});

// Test API endpoint
async function testEndpoint(method, endpoint, requiresAuth, dataElementId = null) {
    const responseContainer = document.getElementById('responseContainer');
    
    // Show loading state
    responseContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Testing ${method} ${endpoint}...</p>
        </div>
    `;
    
    try {
        // Validate token if required
        if (requiresAuth && !currentToken) {
            throw new Error('Bearer token is required for this endpoint');
        }
        
        // Prepare request options
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // Add authorization header if required
        if (requiresAuth) {
            options.headers['Authorization'] = `Bearer ${currentToken}`;
        }
        
        // Add request body for POST/PUT requests
        if ((method === 'POST' || method === 'PUT') && dataElementId) {
            const dataElement = document.getElementById(dataElementId);
            if (dataElement) {
                try {
                    const data = JSON.parse(dataElement.value);
                    options.body = JSON.stringify(data);
                } catch (e) {
                    throw new Error('Invalid JSON data: ' + e.message);
                }
            }
        }
        
        // Make the request
        const startTime = performance.now();
        const response = await fetch(endpoint, options);
        const endTime = performance.now();
        const responseTime = Math.round(endTime - startTime);
        
        // Get response data
        let responseData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }
        
        // Display response
        displayResponse({
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            data: responseData,
            responseTime: responseTime,
            url: endpoint,
            method: method
        });
        
    } catch (error) {
        displayError(error.message, endpoint, method);
    }
}

// Display API response
function displayResponse(response) {
    const responseContainer = document.getElementById('responseContainer');
    
    const statusClass = response.status >= 200 && response.status < 300 ? 'success' : 
                       response.status >= 400 && response.status < 500 ? 'warning' : 'danger';
    
    responseContainer.innerHTML = `
        <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">
                    <span class="badge bg-secondary me-2">${response.method}</span>
                    ${response.url}
                </h6>
                <small class="text-muted">${response.responseTime}ms</small>
            </div>
            <div class="alert alert-${statusClass} mb-0 py-2">
                <strong>Status:</strong> ${response.status} ${response.statusText}
            </div>
        </div>
        
        <div class="mb-3">
            <h6>Response Headers:</h6>
            <pre class="bg-dark p-2 rounded"><code>${JSON.stringify(response.headers, null, 2)}</code></pre>
        </div>
        
        <div>
            <h6>Response Body:</h6>
            <pre class="bg-dark p-3 rounded"><code>${typeof response.data === 'object' ? 
                JSON.stringify(response.data, null, 2) : response.data}</code></pre>
        </div>
    `;
}

// Display error
function displayError(errorMessage, endpoint, method) {
    const responseContainer = document.getElementById('responseContainer');
    
    responseContainer.innerHTML = `
        <div class="alert alert-danger">
            <h6>
                <i class="fas fa-exclamation-triangle me-2"></i>
                Request Failed
            </h6>
            <div class="mb-2">
                <strong>Endpoint:</strong> ${method} ${endpoint}
            </div>
            <div>
                <strong>Error:</strong> ${errorMessage}
            </div>
        </div>
    `;
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Set current token from input
    const tokenInput = document.getElementById('apiToken');
    currentToken = tokenInput.value.trim();
    
    // Test health endpoint on page load
    testEndpoint('GET', '/api/health', false);
});
