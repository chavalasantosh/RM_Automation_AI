// Modern JavaScript with ES6+ features
'use strict';

// Theme Management
class ThemeManager {
    static init() {
        this.themeSwitch = document.querySelector('.theme-switch');
        this.prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        this.currentTheme = localStorage.getItem('theme') || 
            (this.prefersDarkScheme.matches ? 'dark' : 'light');
        
        this.applyTheme(this.currentTheme);
        this.setupListeners();
    }

    static applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.currentTheme = theme;
    }

    static toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    static setupListeners() {
        if (this.themeSwitch) {
            this.themeSwitch.addEventListener('click', () => this.toggleTheme());
        }
        
        this.prefersDarkScheme.addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
}

// Toast Notification System
class ToastSystem {
    static container = null;

    static init() {
        if (!this.container) {
            this.container = document.querySelector('.toast-container') || 
                (() => {
                    const container = document.createElement('div');
                    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                    document.body.appendChild(container);
                    return container;
                })();
        }
    }

    static show(message, type = 'info', duration = 3000) {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast fade-in`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const icons = {
            success: 'mdi-check-circle',
            error: 'mdi-alert-circle',
            warning: 'mdi-alert',
            info: 'mdi-information'
        };

        const colors = {
            success: 'var(--success-gradient)',
            error: 'var(--error-gradient)',
            warning: 'var(--warning-gradient)',
            info: 'var(--primary-gradient)'
        };

        toast.innerHTML = `
            <div class="toast-header" style="background: ${colors[type]}">
                <i class="mdi ${icons[type]} me-2 text-white"></i>
                <strong class="me-auto text-white">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;

        this.container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { 
            autohide: true, 
            delay: duration,
            animation: true
        });
        
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        return bsToast;
    }
}

// Modern API Client
class APIClient {
    static async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };

        try {
            const response = await fetch(endpoint, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'An error occurred');
            }

            return data;
        } catch (error) {
            ToastSystem.show(error.message, 'error');
            throw error;
        }
    }

    static async uploadFile(endpoint, file, onProgress) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentCompleted = Math.round((e.loaded * 100) / e.total);
                    onProgress?.(percentCompleted);
                }
            });

            const response = await new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(JSON.parse(xhr.response));
                    } else {
                        reject(new Error(xhr.response || 'Upload failed'));
                    }
                };
                xhr.onerror = () => reject(new Error('Network error'));
                xhr.open('POST', endpoint);
                xhr.send(formData);
            });

            return response;
        } catch (error) {
            ToastSystem.show(error.message, 'error');
            throw error;
        }
    }
}

// Form Validation System
class FormValidator {
    static rules = {
        required: value => !!value.trim() || 'This field is required',
        email: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Please enter a valid email address',
        minLength: (value, length) => value.length >= length || `Minimum length is ${length} characters`,
        maxLength: (value, length) => value.length <= length || `Maximum length is ${length} characters`,
        pattern: (value, pattern) => pattern.test(value) || 'Invalid format',
        match: (value, field) => value === field.value || 'Fields do not match'
    };

    static validate(form, customRules = {}) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        this.clearErrors(form);

        inputs.forEach(input => {
            const rules = { ...this.rules, ...customRules };
            const inputRules = input.dataset.validate ? input.dataset.validate.split(' ') : [];

            for (const rule of inputRules) {
                const [ruleName, ...params] = rule.split(':');
                if (rules[ruleName]) {
                    const result = rules[ruleName](input.value, ...params);
                    if (result !== true) {
                        this.showError(input, result);
                isValid = false;
                        break;
                    }
                }
            }
        });

        return isValid;
    }

    static showError(input, message) {
        const formGroup = input.closest('.form-group');
        const errorDiv = formGroup.querySelector('.invalid-feedback') || document.createElement('div');
        
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        if (!formGroup.querySelector('.invalid-feedback')) {
            formGroup.appendChild(errorDiv);
        }
        
        input.classList.add('is-invalid');
        input.setAttribute('aria-invalid', 'true');
    }

    static clearErrors(form) {
        form.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
            input.removeAttribute('aria-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(error => error.remove());
    }
}

// File Upload System
class FileUploader {
    static init(dropZone, input, options = {}) {
        if (!dropZone || !input) return;

        const {
            onUpload,
            maxSize = 10 * 1024 * 1024, // 10MB
            allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            maxFiles = 1
        } = options;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.highlight(dropZone), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.unhighlight(dropZone), false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => this.handleDrop(e, input, { maxSize, allowedTypes, maxFiles, onUpload }), false);
        input.addEventListener('change', (e) => this.handleFiles(e.target.files, { maxSize, allowedTypes, maxFiles, onUpload }), false);
    }

    static preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

    static highlight(element) {
        element.classList.add('highlight');
    }

    static unhighlight(element) {
        element.classList.remove('highlight');
    }

    static async handleDrop(e, input, options) {
        const dt = e.dataTransfer;
        const files = dt.files;
        await this.handleFiles(files, options);
    }

    static async handleFiles(files, { maxSize, allowedTypes, maxFiles, onUpload }) {
        if (files.length > maxFiles) {
            ToastSystem.show(`Maximum ${maxFiles} file${maxFiles > 1 ? 's' : ''} allowed`, 'error');
            return;
        }

        for (const file of files) {
            if (file.size > maxSize) {
                ToastSystem.show(`File ${file.name} is too large. Maximum size is ${maxSize / 1024 / 1024}MB`, 'error');
                continue;
            }

            if (!allowedTypes.includes(file.type)) {
                ToastSystem.show(`File type ${file.type} is not allowed`, 'error');
                continue;
            }

            try {
                await onUpload?.(file);
            } catch (error) {
                console.error('Upload error:', error);
            }
        }
    }
}

// RME Enterprise AI Platform - Main JavaScript

// Utility Functions
const utils = {
    // Show loading overlay
    showLoading() {
        document.getElementById('loading-overlay').classList.remove('d-none');
    },

    // Hide loading overlay
    hideLoading() {
        document.getElementById('loading-overlay').classList.add('d-none');
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        const container = document.getElementById('toast-container') || document.body;
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Format date
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Format number with commas
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Form Handling
const formHandler = {
    // Initialize form validation
    initValidation(form) {
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }
            
            try {
                utils.showLoading();
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                utils.showToast(result.message || 'Success!', 'success');
                
                // Reset form if needed
                if (form.dataset.resetOnSuccess === 'true') {
                    form.reset();
                    form.classList.remove('was-validated');
                }
                
                // Trigger success callback if exists
                if (typeof window[form.dataset.successCallback] === 'function') {
                    window[form.dataset.successCallback](result);
                }
                
            } catch (error) {
                console.error('Form submission error:', error);
                utils.showToast(error.message || 'An error occurred', 'danger');
            } finally {
                utils.hideLoading();
            }
        });
    },

    // Initialize all forms
    initAllForms() {
        document.querySelectorAll('form[data-validate="true"]').forEach(form => {
            this.initValidation(form);
        });
    }
};

// Chart Handling
const chartHandler = {
    // Initialize charts
    initCharts() {
        // Match Score Distribution
        const scoreChart = document.getElementById('scoreDistributionChart');
        if (scoreChart) {
            new Chart(scoreChart, {
                type: 'bar',
                data: {
                    labels: ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
                    datasets: [{
                        label: 'Number of Matches',
                        data: [12, 19, 3, 5, 2],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(255, 159, 64, 0.2)',
                            'rgba(255, 205, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(54, 162, 235, 0.2)'
                        ],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(54, 162, 235)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Match Score Distribution'
                        }
                    }
                }
            });
        }

        // Skills Match Chart
        const skillsChart = document.getElementById('skillsMatchChart');
        if (skillsChart) {
            new Chart(skillsChart, {
                type: 'radar',
                data: {
                    labels: ['Technical', 'Soft Skills', 'Domain', 'Experience', 'Education'],
                    datasets: [{
                        label: 'Required Skills',
                        data: [90, 85, 75, 80, 70],
                        fill: true,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(54, 162, 235)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Skills Match Analysis'
                        }
                    }
                }
            });
        }
    }
};

// Table Handling
const tableHandler = {
    // Initialize tables
    initTables() {
        document.querySelectorAll('table[data-sortable="true"]').forEach(table => {
            new Sortable(table.querySelector('tbody'), {
                animation: 150,
                ghostClass: 'sortable-ghost',
                onEnd: function(evt) {
                    // Handle reordering if needed
                    console.log('Row reordered:', evt.oldIndex, '->', evt.newIndex);
                }
            });
        });
    },

    // Initialize data tables
    initDataTables() {
        document.querySelectorAll('table[data-datatable="true"]').forEach(table => {
            // Add search, pagination, and sorting functionality
            const searchInput = document.createElement('input');
            searchInput.type = 'search';
            searchInput.className = 'form-control mb-3';
            searchInput.placeholder = 'Search...';
            table.parentNode.insertBefore(searchInput, table);

            searchInput.addEventListener('input', utils.debounce((e) => {
                const searchTerm = e.target.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }, 300));
        });
    }
};

// Document Ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    formHandler.initAllForms();
    chartHandler.initCharts();
    tableHandler.initTables();
    tableHandler.initDataTables();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle offline/online status
    window.addEventListener('online', () => {
        document.body.classList.remove('offline');
        utils.showToast('You are back online!', 'success');
    });

    window.addEventListener('offline', () => {
        document.body.classList.add('offline');
        utils.showToast('You are offline. Some features may be limited.', 'warning');
    });

    // Check initial connection status
    if (!navigator.onLine) {
        document.body.classList.add('offline');
        utils.showToast('You are offline. Some features may be limited.', 'warning');
    }
});

// Export utilities for use in other scripts
window.RME = {
    utils,
    formHandler,
    chartHandler,
    tableHandler
};

// Global API object for dashboard and other components
window.API = {
    async request(endpoint, options = {}) {
        return await APIClient.request(endpoint, options);
    },
    
    async uploadFile(endpoint, formData, onProgress) {
        // Extract file from formData for the uploadFile method
        const file = formData.get('file');
        if (!file) {
            throw new Error('No file found in form data');
        }
        return await APIClient.uploadFile(endpoint, file, onProgress);
    }
};

// Global Toast object for dashboard
window.Toast = {
    show: (message, type = 'info') => ToastSystem.show(message, type)
}; 