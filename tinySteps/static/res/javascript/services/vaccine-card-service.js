class VaccineCardService {
    constructor() {
        this.apiBaseUrl = '/api';
    }

    // Helper method to get CSRF token
    getCsrfToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    }

    // Get all vaccines for a vaccine card
    async getVaccines(vaccineCardId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccine-cards/${vaccineCardId}/vaccines/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching vaccines:', error);
            return { vaccines: [] };
        }
    }

    // Add a new vaccine
    async addVaccine(vaccineCardId, vaccineData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccine-cards/${vaccineCardId}/add_vaccine/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(vaccineData)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error adding vaccine:', error);
            throw error;
        }
    }

    // Update an existing vaccine
    async updateVaccine(id, vaccineData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccines/${id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(vaccineData)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating vaccine:', error);
            throw error;
        }
    }

    // Delete a vaccine
    async deleteVaccine(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccines/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return { success: true };
        } catch (error) {
            console.error('Error deleting vaccine:', error);
            throw error;
        }
    }

    // Get a specific vaccine
    async getVaccine(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccines/${id}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching vaccine:', error);
            throw error;
        }
    }

    // Get vaccine statistics
    async getVaccineStats(vaccineCardId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccine-cards/${vaccineCardId}/stats/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching vaccine stats:', error);
            return {
                total: 0,
                administered: 0,
                pending: 0,
                upcoming: 0
            };
        }
    }

    // Get upcoming vaccines
    async getUpcomingVaccines(vaccineCardId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/vaccine-cards/${vaccineCardId}/upcoming/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching upcoming vaccines:', error);
            return { vaccines: [] };
        }
    }
}

const vaccineCardService = new VaccineCardService();
export default vaccineCardService;