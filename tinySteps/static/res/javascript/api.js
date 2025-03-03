class TinySteps_API {
    constructor() {
        this.csrftoken = this.getCookie_for_CSRF('csrftoken');
        this.baseUrl = '/api/';
    }

    // HELPER TO GET CSRF TOKEN FROM COOKIE
    getCookie_for_CSRF(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Generic fetch method with CSRF protection
    async fetchAPI(endpoint, method = 'GET', data = null) {
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        };

        // Add CSRF token for non-GET requests
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            headers['X-CSRFToken'] = this.csrftoken;
        }

        const options = {
            method,
            headers,
            credentials: 'same-origin',
        };

        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API error: ${response.status}`);
            }
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Children API methods
    async getChildren() {
        return this.fetchAPI('children/');
    }

    async getChild(id) {
        return this.fetchAPI(`children/${id}/`);
    }

    async createChild(data) {
        return this.fetchAPI('children/', 'POST', data);
    }

    async updateChild(id, data) {
        return this.fetchAPI(`children/${id}/`, 'PUT', data);
    }

    async deleteChild(id) {
        return this.fetchAPI(`children/${id}/`, 'DELETE');
    }
    
    // Milestone API methods
    async getMilestones(childId) {
        return this.fetchAPI(`milestones/?child=${childId}`);
    }
    
    async createMilestone(data) {
        return this.fetchAPI('milestones/', 'POST', data);
    }
    
    async updateMilestone(id, data) {
        return this.fetchAPI(`milestones/${id}/`, 'PUT', data);
    }
    
    async deleteMilestone(id) {
        return this.fetchAPI(`milestones/${id}/`, 'DELETE');
    }
    
    // Forum API methods
    async getForumPosts() {
        return this.fetchAPI('forums/');
    }

    async getForumPost(id) {
        return this.fetchAPI(`forums/${id}/`);
    }
    
    async getForumPostComments(id) {
        return this.fetchAPI(`forums/${id}/comments/`);
    }

    async createForumPost(data) {
        return this.fetchAPI('forums/', 'POST', data);
    }
    
    async updateForumPost(id, data) {
        return this.fetchAPI(`forums/${id}/`, 'PUT', data);
    }
    
    async deleteForumPost(id) {
        return this.fetchAPI(`forums/${id}/`, 'DELETE');
    }

    async addForumComment(postId, text) {
        return this.fetchAPI(`forums/${postId}/add_comment/`, 'POST', { text });
    }
    
    async likeForumPost(postId) {
        return this.fetchAPI(`forums/${postId}/like/`, 'POST');
    }
        
    // Guide API methods
    async getParentsGuides() {
        return this.fetchAPI('parents-guides/');
    }
    
    async getParentsGuide(id) {
        return this.fetchAPI(`parents-guides/${id}/`);
    }
    
    async getParentsGuideComments(id) {
        return this.fetchAPI(`parents-guides/${id}/comments/`);
    }
    
    async addParentsGuideComment(guideId, text) {
        return this.fetchAPI(`parents-guides/${guideId}/add_comment/`, 'POST', { text });
    }
    
    async getNutritionGuides() {
        return this.fetchAPI('nutrition-guides/');
    }
    
    async getNutritionGuide(id) {
        return this.fetchAPI(`nutrition-guides/${id}/`);
    }
    
    async getNutritionGuideComments(id) {
        return this.fetchAPI(`nutrition-guides/${id}/comments/`);
    }
    
    async addNutritionGuideComment(guideId, text) {
        return this.fetchAPI(`nutrition-guides/${guideId}/add_comment/`, 'POST', { text });
    }
    
    // Notification API methods
    async getNotifications() {
        return this.fetchAPI('notifications/');
    }
    
    async markNotificationAsRead(id) {
        return this.fetchAPI(`notifications/${id}/mark_read/`, 'POST');
    }
    
    // Info request API methods
    async createInfoRequest(data) {
        return this.fetchAPI('info-requests/', 'POST', data);
    }
}

const api = new TinySteps_API();