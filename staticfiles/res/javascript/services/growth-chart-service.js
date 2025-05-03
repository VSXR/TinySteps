export class GrowthChartService {
    constructor() {
        this.baseUrl = '/api';
        this.csrfToken = this.getCsrfToken();
    }
    
    getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
    
    async getChildGrowthData(childId) {
        try {
            const response = await fetch(`${this.baseUrl}/children/${childId}/growth-data/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.warn('Using fallback data for growth charts:', error);
            return this.getFallbackData();
        }
    }
    
    getFallbackData() {
        // Get data from DOM meta tags as fallback
        const birthWeight = parseFloat(document.querySelector('meta[name="birth-weight"]')?.content) || 3.5;
        const currentWeight = parseFloat(document.querySelector('meta[name="current-weight"]')?.content) || 18.3;
        const birthHeight = parseFloat(document.querySelector('meta[name="birth-height"]')?.content) || 50;
        const currentHeight = parseFloat(document.querySelector('meta[name="current-height"]')?.content) || 110;
        
        return {
            birthWeight,
            currentWeight,
            birthHeight,
            currentHeight,
            gender: document.getElementById('child-gender')?.value || 'M'
        };
    }
}