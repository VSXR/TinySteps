import { GrowthChartService } from '../services/growth-chart-service.js';

// Class following Single Responsibility Principle
class GrowthChartManager {
    constructor(childId, childGender) {
        this.childId = childId;
        this.childGender = childGender || 'M';
        this.service = new GrowthChartService();
        this.chartModal = document.getElementById('chartModal');
        this.weightChart = null;
        this.heightChart = null;
    }

    init() {
        this.setupModalExpansion();
        this.initializeChildCharts();
        this.setupResizeHandler();
    }
    
    // Handle window resize for responsive charts
    setupResizeHandler() {
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (this.weightChart) this.weightChart.resize();
                if (this.heightChart) this.heightChart.resize();
            }, 250);
        });
    }

    // Modal setup with accessibility improvements
    setupModalExpansion() {
        if (!this.chartModal) return;
        
        this.chartModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const chartType = button.getAttribute('data-chart-type');
            const modalImage = document.getElementById('modal-chart-image');
            const modalTitle = document.getElementById('chartModalLabel');
            const downloadLink = document.getElementById('download-chart');
            
            // Set appropriate image and title based on chart type
            let imagePath, title, altText;
            switch(chartType) {
                case 'weight-boys':
                    imagePath = `/static/res/img/growth/weight-boys-0-5.jpg`;
                    title = "Weight Chart - Boys (0-5 Years)";
                    altText = "Detailed weight chart for boys aged 0-5 years showing percentiles";
                    break;
                case 'weight-girls':
                    imagePath = `/static/res/img/growth/weight-girls-0-5.jpg`;
                    title = "Weight Chart - Girls (0-5 Years)";
                    altText = "Detailed weight chart for girls aged 0-5 years showing percentiles";
                    break;
                case 'height-boys':
                    imagePath = `/static/res/img/growth/height-boys-0-5.jpg`;
                    title = "Height Chart - Boys (0-5 Years)";
                    altText = "Detailed height chart for boys aged 0-5 years showing percentiles";
                    break;
                case 'height-girls':
                    imagePath = `/static/res/img/growth/height-girls-0-5.jpg`;
                    title = "Height Chart - Girls (0-5 Years)";
                    altText = "Detailed height chart for girls aged 0-5 years showing percentiles";
                    break;
            }
            
            if (modalImage) {
                modalImage.src = imagePath;
                modalImage.alt = altText;
            }
            
            if (modalTitle) modalTitle.textContent = title;
            
            if (downloadLink) {
                downloadLink.href = imagePath;
                downloadLink.download = chartType + '.jpg';
                downloadLink.setAttribute('aria-label', 'Download ' + title);
            }
        });
    }

    // Chart initialization with improved error handling
    initializeChildCharts() {
        const weightCtx = document.getElementById('weight-percentile-chart');
        const heightCtx = document.getElementById('height-percentile-chart');
        
        if (!weightCtx || !heightCtx) return;
        
        // Show loading state
        this.showChartLoading(weightCtx);
        this.showChartLoading(heightCtx);
        
        // Get growth data from service
        this.service.getChildGrowthData(this.childId)
            .then(data => {
                this.createWeightChart(weightCtx, data);
                this.createHeightChart(heightCtx, data);
            })
            .catch(error => {
                console.error("Error fetching growth data", error);
                this.showChartError(weightCtx);
                this.showChartError(heightCtx);
            });
    }
    
    // Display loading state on charts
    showChartLoading(container) {
        if (!container) return;
        container.innerHTML = '<div class="d-flex justify-content-center align-items-center h-100"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    }
    
    // Display error state on charts
    showChartError(container) {
        if (!container) return;
        container.innerHTML = '<div class="text-center text-muted p-3"><i class="fa-solid fa-triangle-exclamation fs-2 mb-2"></i><p>Unable to load chart data</p></div>';
    }
    
    // Create weight chart - separate responsibility
    createWeightChart(canvas, data) {
        if (!canvas) return;
        
        this.weightChart = new Chart(canvas, {
            type: 'line',
            data: this.getWeightChartData(data),
            options: this.getChartOptions('Weight (kg)')
        });
    }
    
    // Create height chart - separate responsibility
    createHeightChart(canvas, data) {
        if (!canvas) return;
        
        this.heightChart = new Chart(canvas, {
            type: 'line',
            data: this.getHeightChartData(data),
            options: this.getChartOptions('Height (cm)')
        });
    }

    // Data preparation methods
    getWeightChartData(data) {
        return {
            labels: ['Birth', '3m', '6m', '9m', '12m', '18m', '24m', '36m', '48m', '60m'],
            datasets: [
                {
                    label: 'Your Child',
                    data: data.weightHistory || [data.birthWeight, 5.2, 7.1, 8.3, 9.5, 10.8, 12.1, 14.2, 16.1, data.currentWeight],
                    borderColor: 'rgba(66, 133, 244, 1)',
                    backgroundColor: 'rgba(66, 133, 244, 0.1)',
                    pointBackgroundColor: 'rgba(66, 133, 244, 1)',
                    borderWidth: 3,
                    pointRadius: 4,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: '50th Percentile',
                    data: [3.3, 6.0, 7.6, 8.9, 9.6, 10.9, 12.2, 14.3, 16.3, 18.3],
                    borderColor: 'rgba(128, 128, 128, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    borderWidth: 2,
                    fill: false
                }
            ]
        };
    }
    
    getHeightChartData(data) {
        return {
            labels: ['Birth', '3m', '6m', '9m', '12m', '18m', '24m', '36m', '48m', '60m'],
            datasets: [
                {
                    label: 'Your Child',
                    data: data.heightHistory || [data.birthHeight, 61, 67, 72, 76, 82, 88, 96, 103, data.currentHeight],
                    borderColor: 'rgba(234, 67, 53, 1)',
                    backgroundColor: 'rgba(234, 67, 53, 0.1)',
                    pointBackgroundColor: 'rgba(234, 67, 53, 1)',
                    borderWidth: 3,
                    pointRadius: 4,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: '50th Percentile',
                    data: [49.9, 61.1, 67.6, 72.3, 75.7, 82.3, 87.8, 96.1, 103.3, 110],
                    borderColor: 'rgba(128, 128, 128, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    borderWidth: 2,
                    fill: false
                }
            ]
        };
    }
    
    // Common chart options - reusable configuration
    getChartOptions(yAxisLabel) {
        return {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: yAxisLabel
                    },
                    beginAtZero: false
                },
                x: {
                    title: {
                        display: true,
                        text: 'Age'
                    }
                }
            }
        };
    }
}

// Initialize on document load with enhanced error handling
document.addEventListener('DOMContentLoaded', function() {
    try {
        const childId = document.getElementById('child-id')?.value;
        const childGender = document.getElementById('child-gender')?.value;
        
        if (childId) {
            const growthChartManager = new GrowthChartManager(childId, childGender);
            growthChartManager.init();
        } else {
            console.error("Child ID not found in page");
        }
    } catch (error) {
        console.error("Error initializing growth charts:", error);
    }
});