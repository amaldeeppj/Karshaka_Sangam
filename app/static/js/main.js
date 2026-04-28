// Utility functions for the application

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loader mx-auto"></div>';
    }
}

// Hide loading spinner
function hideLoading(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
    }
}

// Auto-refresh data every 30 seconds (optional)
setInterval(function() {
    if (window.location.pathname === '/') {
        fetch('/filter-listings')
            .then(response => response.json())
            .then(data => {
                console.log('Data auto-refreshed');
            });
    }
}, 30000);

// Toast notification function
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Price trend indicator
function getPriceTrend(currentPrice, previousPrice) {
    if (currentPrice > previousPrice) return 'trend-up';
    if (currentPrice < previousPrice) return 'trend-down';
    return 'trend-stable';
}

// Search/filter functionality
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { formatCurrency, showToast, getPriceTrend, debounce };
}