class CalendarService {
    constructor() {
        this.apiBaseUrl = '/api'; // Base URL for the API
    }

    // Helper method to get CSRF token
    getCsrfToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    }

    // Fetch events from API
    async getEvents(childId, start, end) {
        try {
            console.log(`Fetching events for child ${childId} from ${start} to ${end}`);
            let url = `${this.apiBaseUrl}/children/${childId}/events/`;
            if (start && end) {
                url += `?start=${start}&end=${end}`;
            }
            
            const response = await fetch(url, {
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
            console.error('Error fetching events:', error);
            return { events: [] }; // Return empty events on error
        }
    }

    // Create a new event
    async createEvent(eventData) {
        try {
            console.log('Creating event with data:', eventData);
            const response = await fetch(`${this.apiBaseUrl}/children/${eventData.child}/events/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(eventData)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating event:', error);
            throw error;
        }
    }

    // Update an existing event
    async updateEvent(id, eventData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/calendar-events/${id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(eventData)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating event:', error);
            throw error;
        }
    }

    // Delete an event
    async deleteEvent(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/calendar-events/${id}/`, {
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
            console.error('Error deleting event:', error);
            throw error;
        }
    }

    // Get a specific event
    async getEvent(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/calendar-events/${id}/`, {
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
            console.error('Error fetching event:', error);
            throw error;
        }
    }

    // Get upcoming events
    async getUpcomingEvents(childId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/children/${childId}/events/upcoming_events/`, {
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
            console.error('Error fetching upcoming events:', error);
            return { reminders: [] };
        }
    }

    // Get event statistics
    async getEventStats(childId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/children/${childId}/events/event_stats/`, {
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
            console.error('Error fetching event stats:', error);
            return {
                total: 0,
                doctor: 0,
                vaccine: 0,
                milestone: 0,
                feeding: 0,
                other: 0
            };
        }
    }
}

const calendarService = new CalendarService();
export default calendarService;