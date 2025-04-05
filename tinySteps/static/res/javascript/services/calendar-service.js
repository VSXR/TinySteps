/**
 * Calendar Service - Provides mock data for the calendar
 */
class CalendarService {
  constructor() {
    this.mockEvents = [
      {
        id: 1,
        title: 'Doctor Appointment',
        date: '2023-06-15',
        time: '10:30:00',
        type: 'doctor',
        location: 'Pediatric Clinic',
        description: 'Regular check-up',
        has_reminder: true,
        reminder_minutes: 60
      },
      {
        id: 2,
        title: 'Vaccine Shot',
        date: '2023-06-22',
        time: '14:00:00',
        type: 'vaccine',
        location: 'Health Center',
        description: 'Scheduled vaccination',
        has_reminder: true,
        reminder_minutes: 1440
      },
      {
        id: 3,
        title: 'First Steps!',
        date: '2023-06-10',
        time: null,
        type: 'milestone',
        location: '',
        description: 'Baby started walking!',
        has_reminder: false,
        reminder_minutes: null
      },
      {
        id: 4,
        title: 'Introduce Solid Foods',
        date: '2023-06-18',
        time: '12:00:00',
        type: 'feeding',
        location: 'Home',
        description: 'Start introducing pureed vegetables',
        has_reminder: true,
        reminder_minutes: 30
      },
      {
        id: 5,
        title: 'Playdate',
        date: '2023-06-25',
        time: '16:00:00',
        type: 'other',
        location: 'Community Park',
        description: 'Socializing with other babies',
        has_reminder: true,
        reminder_minutes: 120
      }
    ];
  }

  // Fetch events in a given date range
  async getEvents(childId, start, end) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Get the current date to replace event dates with dates relative to now
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Clone and adjust mock events to current month
    const adjustedEvents = this.mockEvents.map(event => {
      const eventDate = new Date(event.date);
      // Keep the day but use current month and year
      const newDate = new Date(currentYear, currentMonth, eventDate.getDate());
      
      // Format the date as 'YYYY-MM-DD'
      const formattedDate = newDate.toISOString().split('T')[0];
      
      return {
        ...event,
        date: formattedDate
      };
    });
    
    return {
      events: adjustedEvents
    };
  }

  // Get upcoming events
  async getUpcomingEvents(childId) {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      reminders: this.mockEvents.filter(event => event.has_reminder).slice(0, 3)
    };
  }

  // Get event statistics
  async getEventStats(childId) {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      total: this.mockEvents.length,
      doctor: this.mockEvents.filter(e => e.type === 'doctor').length,
      vaccine: this.mockEvents.filter(e => e.type === 'vaccine').length,
      milestone: this.mockEvents.filter(e => e.type === 'milestone').length,
      feeding: this.mockEvents.filter(e => e.type === 'feeding').length,
      other: this.mockEvents.filter(e => e.type === 'other').length
    };
  }

  // Create a new event
  async createEvent(eventData) {
    await new Promise(resolve => setTimeout(resolve, 400));
    const newId = Math.max(...this.mockEvents.map(e => e.id)) + 1;
    const newEvent = {
      id: newId,
      ...eventData
    };
    this.mockEvents.push(newEvent);
    return newEvent;
  }

  // Update an existing event
  async updateEvent(id, eventData) {
    await new Promise(resolve => setTimeout(resolve, 300));
    const index = this.mockEvents.findIndex(e => e.id == id);
    if (index !== -1) {
      this.mockEvents[index] = {
        ...this.mockEvents[index],
        ...eventData
      };
      return this.mockEvents[index];
    }
    throw new Error('Event not found');
  }

  // Delete an event
  async deleteEvent(id) {
    await new Promise(resolve => setTimeout(resolve, 300));
    const index = this.mockEvents.findIndex(e => e.id == id);
    if (index !== -1) {
      this.mockEvents.splice(index, 1);
      return { success: true };
    }
    throw new Error('Event not found');
  }

  // Get a specific event
  async getEvent(id) {
    await new Promise(resolve => setTimeout(resolve, 200));
    const event = this.mockEvents.find(e => e.id == id);
    if (event) {
      return event;
    }
    throw new Error('Event not found');
  }
}

// Export a single instance
const calendarService = new CalendarService();
export default calendarService;