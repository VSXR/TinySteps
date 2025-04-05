import calendarService from '../services/calendar-service.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const calendarEl = document.getElementById('calendar');
    const loadingEl = document.getElementById('loading-indicator');
    const eventForm = document.getElementById('event-form');
    const notificationEl = document.getElementById('notification');
    
    // Check if all required elements exist
    if (!calendarEl) {
        console.error('Calendar element not found');
        return;
    }
    
    // Global variables
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    const childId = document.getElementById('child-id')?.value || '1';
    let currentEvent = null;
    
    // Add global error handler to debug issues
    window.addEventListener('error', function(event) {
        console.error('Global error caught:', event.error);
    });
    
    // Set initial view based on screen size
    let initialView = 'dayGridMonth';
    if (window.innerWidth < 768) {
        initialView = 'listWeek';
    }

    // Color map for event types
    const eventColorMap = {
        'doctor': '#2196f3',    // Blue - medical appointments
        'vaccine': '#ff9800',   // Orange - vaccines
        'milestone': '#4caf50', // Green - developmental milestones
        'feeding': '#9c27b0',   // Purple - feeding
        'other': '#757575'      // Gray - others
    };

    // Initialize the calendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: initialView,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale: document.documentElement.lang || 'en', 
        height: 'auto',
        expandRows: true,
        navLinks: true,
        editable: true,
        dayMaxEvents: true,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            if (loadingEl) loadingEl.style.display = 'block';
            
            calendarService.getEvents(childId, fetchInfo.startStr, fetchInfo.endStr)
                .then(data => {
                    console.log('Events received:', data.events, 'count:', data.events.length);
                    if (loadingEl) loadingEl.style.display = 'none';
                    
                    const events = data.events.map(event => ({
                        id: event.id,
                        title: event.title,
                        start: event.time ? `${event.date}T${event.time}` : event.date,
                        allDay: !event.time,
                        backgroundColor: eventColorMap[event.type] || eventColorMap.other,
                        borderColor: eventColorMap[event.type] || eventColorMap.other,
                        extendedProps: {
                            type: event.type,
                            location: event.location,
                            description: event.description,
                            hasReminder: event.has_reminder,
                            reminderMinutes: event.reminder_minutes
                        }
                    }));

                    successCallback(events);
                    
                    // Hide empty message
                    const emptyMessage = document.getElementById('empty-calendar-message');
                    if (emptyMessage) {
                        if (events.length > 0) {
                            emptyMessage.style.display = 'none';
                        } else {
                            emptyMessage.style.display = 'flex';
                        }
                    }
                    
                    // Update the upcoming events list
                    updateUpcomingEvents();
                    
                })
                .catch(error => {
                    console.error('Error fetching events:', error);
                    if (loadingEl) loadingEl.style.display = 'none';
                    failureCallback(error);
                    showNotification('Error loading events', 'danger');
                });
        },
        eventClick: function(info) {
            // Show event details in form
            showEventDetails(info.event);
        },
        eventDidMount: function(info) {
            // Add double-click handler to show event details in dialog
            info.el.addEventListener('dblclick', function() {
                showEventDetailsDialog(info.event);
            });
        },
        dateClick: function(info) {
            // Prepare form for new event
            resetEventForm();
            const dateInput = document.getElementById('event-date');
            if (dateInput) dateInput.value = info.dateStr;
            
            const formTitle = document.getElementById('form-title');
            if (formTitle) formTitle.innerHTML = '<i class="fa-solid fa-plus text-primary me-2" aria-hidden="true"></i> Add Event';
        },
        eventDrop: function(info) {
            // Handle drag and drop event
            updateEventDate(info.event);
        },
        eventResize: function(info) {
            // Handle event resize
            updateEventDate(info.event);
        }
    });

    // Render the calendar
    calendar.render();

    // Check if we need to hide the empty message based on existing events
    setTimeout(() => {
        const hasEvents = calendar.getEvents().length > 0;
        const emptyMessage = document.getElementById('empty-calendar-message');
        
        if (hasEvents && emptyMessage) {
            console.log('Initial check: Calendar has events, hiding empty message');
            emptyMessage.style.display = 'none';
        } else if (emptyMessage) {
            console.log('Initial check: Calendar is empty, showing empty message');
            emptyMessage.style.display = 'flex';
        }
    }, 1000); // Wait for calendar to fully initialize
    
    // Initialize form elements
    initializeForm();
    
    // Load initial event statistics
    updateEventStats(); 
    updateUpcomingReminders();

    // Handler for view buttons
    const viewMonthBtn = document.getElementById('view-month');
    if (viewMonthBtn) {
        viewMonthBtn.addEventListener('click', function() {
            calendar.changeView('dayGridMonth');
            updateActiveViewButton(this);
        });
    }

    const viewWeekBtn = document.getElementById('view-week');
    if (viewWeekBtn) {
        viewWeekBtn.addEventListener('click', function() {
            calendar.changeView('timeGridWeek');
            updateActiveViewButton(this);
        });
    }

    const viewDayBtn = document.getElementById('view-day');
    if (viewDayBtn) {
        viewDayBtn.addEventListener('click', function() {
            calendar.changeView('timeGridDay');
            updateActiveViewButton(this);
        });
    }

    const viewListBtn = document.getElementById('view-list');
    if (viewListBtn) {
        viewListBtn.addEventListener('click', function() {
            calendar.changeView('listWeek');
            updateActiveViewButton(this);
        });
    }

    const viewTodayBtn = document.getElementById('view-today');
    if (viewTodayBtn) {
        viewTodayBtn.addEventListener('click', function() {
            calendar.today();
        });
    }

    // Form event handlers
    const reminderCheckbox = document.getElementById('event-reminder');
    const reminderOptions = document.getElementById('reminder-options');
    
    if (reminderCheckbox && reminderOptions) {
        reminderCheckbox.addEventListener('change', function() {
            reminderOptions.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Event form submission
    if (eventForm) {
        // Add a flag to track if submission is in progress
        let isSubmitting = false;
        
        eventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Prevent multiple submissions
            if (isSubmitting) {
                console.log('Submission already in progress, ignoring duplicate submit');
                return;
            }
            
            isSubmitting = true;
            saveEvent().finally(() => {
                // Reset submission flag when complete (whether success or error)
                setTimeout(() => {
                    isSubmitting = false;
                }, 500); // Small delay to prevent accidental double-clicks
            });
        });
    }

    // Delete event button
    const deleteBtn = document.getElementById('btn-delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteEventModal'));
            deleteModal.show();
        });
    }

    // Confirm delete button
    const confirmDeleteBtn = document.getElementById('btn-confirm-delete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            deleteEvent();
        });
    }

    // Form cancel button
    const cancelBtn = document.getElementById('btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            resetEventForm();
        });
    }

    // Edit event button in modal
    const editEventBtn = document.getElementById('btn-edit-event');
    if (editEventBtn) {
        editEventBtn.addEventListener('click', function() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
            if (modal) modal.hide();
            showEventDetails(currentEvent);
        });
    }

    // Function to initialize form elements
    function initializeForm() {
        const typeSelect = document.getElementById('event-type');
        if (!typeSelect) return;
        
        // Clear existing options
        typeSelect.innerHTML = '';
        
        // Add event type options
        const eventTypes = {
            'doctor': 'Medical Appointment',
            'vaccine': 'Vaccine',
            'milestone': 'Development Milestone',
            'feeding': 'Feeding',
            'other': 'Other'
        };
        
        for (const [value, label] of Object.entries(eventTypes)) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            typeSelect.appendChild(option);
        }
    }

    // Function to update active view button
    function updateActiveViewButton(clickedBtn) {
        const buttons = document.querySelectorAll('.btn-group button');
        if (buttons.length > 0) {
            buttons.forEach(btn => {
                btn.classList.remove('active');
            });
            clickedBtn.classList.add('active');
        }
    }

    // Function to update event statistics
    function updateEventStats() {
        calendarService.getEventStats(childId)
            .then(data => {
                updateStatsUI(data);
            })
            .catch(error => {
                console.error('Error fetching event stats:', error);
                // Generate simple mock statistics on error
                const stats = {
                    total: 0,
                    doctor: 0,
                    vaccine: 0,
                    milestone: 0,
                    feeding: 0,
                    other: 0
                };
                updateStatsUI(stats);
            });
    }
    
    function updateStatsUI(data) {
        const statsContainer = document.getElementById('event-stats');
        if (!statsContainer) return;
        
        const stats = statsContainer.querySelectorAll('.event-stat');
        if (stats.length < 5) return;
        
        // Update total events
        const totalCountEl = stats[0].querySelector('.event-stat-count');
        if (totalCountEl) totalCountEl.textContent = data.total || 0;
        
        // Update event type counts
        const doctorCountEl = stats[1].querySelector('.event-stat-count');
        if (doctorCountEl) doctorCountEl.textContent = data.doctor || 0;
        
        const vaccineCountEl = stats[2].querySelector('.event-stat-count');
        if (vaccineCountEl) vaccineCountEl.textContent = data.vaccine || 0;
        
        const milestoneCountEl = stats[3].querySelector('.event-stat-count');
        if (milestoneCountEl) milestoneCountEl.textContent = data.milestone || 0;
        
        const feedingCountEl = stats[4].querySelector('.event-stat-count');
        if (feedingCountEl) feedingCountEl.textContent = data.feeding || 0;
    }

    // Function to update upcoming reminders with improved reliability
    function updateUpcomingReminders() {
        console.log('Updating upcoming reminders for child ID:', childId);
        
        // Show a subtle loading indicator on the reminders section
        const reminderHeader = document.querySelector('.card-header .badge');
        if (reminderHeader) {
            reminderHeader.classList.add('pulse-animation');
        }
        
        calendarService.getUpcomingEvents(childId)
            .then(data => {
                console.log(`Received ${data.reminders?.length || 0} upcoming reminders`);
                updateRemindersUI(data);
                
                // Update the count badge in the header
                if (reminderHeader) {
                    reminderHeader.textContent = data.reminders?.length || 0;
                    reminderHeader.classList.remove('pulse-animation');
                }
            })
            .catch(error => {
                console.error('Error fetching reminders:', error);
                // Use empty reminders on error
                updateRemindersUI({ reminders: [] });
                
                if (reminderHeader) {
                    reminderHeader.textContent = '0';
                    reminderHeader.classList.remove('pulse-animation');
                }
            });
    }

    // Improved updateRemindersUI function with better styling
    function updateRemindersUI(data) {
        const remindersList = document.getElementById('upcoming-reminders');
        if (!remindersList) {
            console.error('Reminders list element not found');
            return;
        }
        
        // Clear existing reminders
        remindersList.innerHTML = '';
        
        if (data.reminders && data.reminders.length > 0) {
            data.reminders.forEach(reminder => {
                const li = document.createElement('li');
                li.className = 'list-group-item reminder-item d-flex justify-content-between align-items-start';
                li.dataset.eventId = reminder.id;
                
                // Improve the styling of reminder items with custom badges based on type
                const badgeColorClass = getBadgeColorForEventType(reminder.type);
                
                li.innerHTML = `
                    <div>
                        <h4 class="h6 mb-1">${reminder.title}</h4>
                        <p class="small text-muted mb-0 d-flex align-items-center">
                            <i class="fa-solid fa-calendar-day me-1" aria-hidden="true"></i>
                            ${formatDate(reminder.date)}
                            ${reminder.time ? `<span class="mx-1">•</span>
                            <i class="fa-solid fa-clock me-1" aria-hidden="true"></i>
                            ${formatTime(reminder.time)}` : ''}
                        </p>
                    </div>
                    <span class="badge ${badgeColorClass}">${capitalizeFirstLetter(reminder.type)}</span>
                `;
                
                li.addEventListener('click', function() {
                    handleReminderClick(this.dataset.eventId);
                });
                
                remindersList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'list-group-item text-center py-3';
            li.id = 'no-reminders';
            li.innerHTML = '<p class="mb-0 text-muted">No upcoming reminders</p>';
            remindersList.appendChild(li);
        }
    }

    // Function to update the list of upcoming non-reminder events
    function updateUpcomingEvents() {
        const upcomingList = document.getElementById('upcoming-events');
        const countBadge = document.getElementById('upcoming-events-count');
        
        if (!upcomingList || !countBadge) return;
        
        // Get all events
        const allEvents = calendar.getEvents();
        
        // Filter for future events without reminders
        const now = new Date();
        const upcomingNonReminderEvents = allEvents.filter(event => {
            const eventDate = event.start;
            return eventDate > now && !event.extendedProps.hasReminder;
        }).sort((a, b) => a.start - b.start).slice(0, 5); // Get the next 5 events
        
        // Update the badge count
        countBadge.textContent = upcomingNonReminderEvents.length;
        
        // Clear the list
        upcomingList.innerHTML = '';
        
        if (upcomingNonReminderEvents.length === 0) {
            // Show "no events" message
            const li = document.createElement('li');
            li.className = 'list-group-item text-center py-3';
            li.id = 'no-events';
            li.innerHTML = '<p class="mb-0 text-muted">No upcoming events without reminders</p>';
            upcomingList.appendChild(li);
            return;
        }
        
        // Add each event to the list
        upcomingNonReminderEvents.forEach(event => {
            const li = document.createElement('li');
            li.className = 'list-group-item event-item d-flex justify-content-between align-items-start';
            li.dataset.eventId = event.id;
            
            const badgeColorClass = getBadgeColorForEventType(event.extendedProps.type);
            
            li.innerHTML = `
                <div>
                    <h4 class="h6 mb-1">${event.title}</h4>
                    <p class="small text-muted mb-0 d-flex align-items-center">
                        <i class="fa-solid fa-calendar-day me-1" aria-hidden="true"></i>
                        ${formatDate(event.start.toISOString().split('T')[0])}
                        ${!event.allDay ? `<span class="mx-1">•</span>
                        <i class="fa-solid fa-clock me-1" aria-hidden="true"></i>
                        ${formatTime(event.start.toTimeString().slice(0, 5))}` : ''}
                    </p>
                </div>
                <span class="badge ${badgeColorClass}">${capitalizeFirstLetter(event.extendedProps.type)}</span>
            `;
            
            li.addEventListener('click', function() {
                showEventDetailsDialog(event);
            });
            
            upcomingList.appendChild(li);
        });
    }

    // Helper function to get badge color class based on event type
    function getBadgeColorForEventType(type) {
        const badgeClasses = {
            'doctor': 'bg-primary',
            'vaccine': 'bg-warning text-dark',
            'milestone': 'bg-success',
            'feeding': 'bg-purple',
            'other': 'bg-secondary'
        };
        
        return badgeClasses[type] || 'bg-secondary';
    }

    // Add this CSS to make the badge pulse when updating
    document.head.insertAdjacentHTML('beforeend', `
    <style>
        .pulse-animation {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .bg-purple {
            background-color: #9c27b0;
            color: white;
        }
    </style>
    `);
    
    // Function to show event details in dialog
    function showEventDetailsDialog(event) {
        // Get event details
        const title = event.title;
        const type = event.extendedProps.type;
        const date = event.start ? formatDate(event.start.toISOString().split('T')[0]) : '';
        const time = event.allDay ? 'All day' : formatTime(event.start.toTimeString().slice(0, 5));
        const location = event.extendedProps.location || 'Not specified';
        const description = event.extendedProps.description || 'No description';
        const hasReminder = event.extendedProps.hasReminder;
        const reminderMinutes = event.extendedProps.reminderMinutes;
        
        // Format the type for display
        const typeDisplay = type.charAt(0).toUpperCase() + type.slice(1);
        
        // Generate the modal content
        const detailsContent = document.getElementById('event-details-content');
        if (detailsContent) {
            detailsContent.innerHTML = `
                <div class="event-details">
                    <div class="mb-3 pb-2 border-bottom">
                        <h4 class="event-title mb-1">${title}</h4>
                        <span class="badge ${getBadgeColorForEventType(type)}">${typeDisplay}</span>
                    </div>
                    
                    <div class="mb-3">
                        <p class="mb-1"><i class="fa-solid fa-calendar-day me-2"></i><strong>Date:</strong> ${date}</p>
                        <p class="mb-1"><i class="fa-solid fa-clock me-2"></i><strong>Time:</strong> ${time}</p>
                        <p class="mb-1"><i class="fa-solid fa-location-dot me-2"></i><strong>Location:</strong> ${location}</p>
                    </div>
                    
                    <div class="mb-3">
                        <p class="mb-1"><strong>Description:</strong></p>
                        <p class="bg-light p-2 rounded">${description}</p>
                    </div>
                    
                    ${hasReminder ? `
                    <div class="alert alert-info">
                        <i class="fa-solid fa-bell me-2"></i>Reminder set for ${formatReminderTime(reminderMinutes)} before the event
                    </div>
                    ` : ''}
                </div>
            `;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
        modal.show();
        
        // Set the current event to allow editing from the modal
        currentEvent = event;
    }

    // Function to show event details in form
    function showEventDetails(event) {
        currentEvent = event;
        
        // Get event data
        const id = event.id;
        const title = event.title;
        const type = event.extendedProps.type;
        const date = event.start ? formatDateForInput(event.start) : '';
        const time = event.allDay ? '' : formatTimeForInput(event.start);
        const location = event.extendedProps.location || '';
        const description = event.extendedProps.description || '';
        const hasReminder = event.extendedProps.hasReminder;
        const reminderMinutes = event.extendedProps.reminderMinutes;
        
        // Update form elements
        const formTitleEl = document.getElementById('form-title');
        if (formTitleEl) {
            formTitleEl.innerHTML = '<i class="fa-solid fa-edit text-primary me-2" aria-hidden="true"></i> Edit Event';
        }
        
        const titleInput = document.getElementById('event-title');
        if (titleInput) titleInput.value = title;
        
        const typeSelect = document.getElementById('event-type');
        if (typeSelect) typeSelect.value = type;
        
        const dateInput = document.getElementById('event-date');
        if (dateInput) dateInput.value = date;
        
        const timeInput = document.getElementById('event-time');
        if (timeInput) timeInput.value = time;
        
        const locationInput = document.getElementById('event-location');
        if (locationInput) locationInput.value = location;
        
        const notesInput = document.getElementById('event-notes');
        if (notesInput) notesInput.value = description;
        
        const reminderCheckbox = document.getElementById('event-reminder');
        if (reminderCheckbox) reminderCheckbox.checked = hasReminder;
        
        const reminderOptions = document.getElementById('reminder-options');
        const reminderTime = document.getElementById('reminder-time');
        
        if (hasReminder && reminderMinutes && reminderOptions && reminderTime) {
            reminderTime.value = reminderMinutes;
            reminderOptions.style.display = 'block';
        } else if (reminderOptions) {
            reminderOptions.style.display = 'none';
        }
        
        // Show delete and cancel buttons
        const deleteBtn = document.getElementById('btn-delete');
        const cancelBtn = document.getElementById('btn-cancel');
        const saveBtn = document.getElementById('btn-save');
        
        if (deleteBtn) deleteBtn.style.display = 'block';
        if (cancelBtn) cancelBtn.style.display = 'block';
        if (saveBtn) saveBtn.innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Update Event';
        
        // Scroll to the form
        if (formTitleEl) formTitleEl.scrollIntoView({ behavior: 'smooth' });
    }

    // Function to reset event form
    function resetEventForm() {
        currentEvent = null;
        if (eventForm) eventForm.reset();
        
        const reminderOptions = document.getElementById('reminder-options');
        if (reminderOptions) reminderOptions.style.display = 'none';
        
        // Hide delete and cancel buttons
        const deleteBtn = document.getElementById('btn-delete');
        const cancelBtn = document.getElementById('btn-cancel');
        
        if (deleteBtn) deleteBtn.style.display = 'none';
        if (cancelBtn) cancelBtn.style.display = 'none';
        
        // Reset form title and button text
        const formTitle = document.getElementById('form-title');
        const saveBtn = document.getElementById('btn-save');
        
        if (formTitle) formTitle.innerHTML = '<i class="fa-solid fa-plus text-primary me-2" aria-hidden="true"></i> Add Event';
        if (saveBtn) saveBtn.innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Save Event';
    }

    // Function to save an event
    function saveEvent() {
        console.log('===== DEBUGGING STEPS =====');
        console.log('Step 1: Beginning saveEvent function');
    
        const titleInput = document.getElementById('event-title');
        const typeSelect = document.getElementById('event-type');
        const dateInput = document.getElementById('event-date');
        const timeInput = document.getElementById('event-time');
        const locationInput = document.getElementById('event-location');
        const notesInput = document.getElementById('event-notes');
        const reminderCheckbox = document.getElementById('event-reminder');
        const reminderTime = document.getElementById('reminder-time');
        
        if (!titleInput || !typeSelect || !dateInput) {
            showNotification('Missing required form elements', 'danger');
            return Promise.resolve();
        }
        
        const eventData = {
            title: titleInput.value,
            type: typeSelect.value,
            date: dateInput.value,
            time: timeInput?.value || null,
            location: locationInput?.value || '',
            description: notesInput?.value || '',
            has_reminder: reminderCheckbox?.checked || false,
            reminder_minutes: reminderCheckbox?.checked ? (reminderTime?.value || 30) : null,
            child: childId
        };
        
        console.log('Saving event:', eventData);
        
        // Determine if this is a new event or an update
        const isNewEvent = !currentEvent;
        
        if (isNewEvent) {
            // Check for duplicates before saving
            const allEvents = calendar.getEvents();
            const isDuplicate = allEvents.some(existingEvent => {
                // Improved duplicate detection
                if (!existingEvent.id) return false; // Skip temporary events
                
                const sameTitle = existingEvent.title === eventData.title;
                const sameDate = existingEvent.startStr.substring(0, 10) === eventData.date;
                
                // More reliable time comparison
                let sameTime;
                if (eventData.time) {
                    const eventTimeStr = eventData.time.substring(0, 5);
                    const existingTimeStr = existingEvent.startStr.includes('T') ? 
                        existingEvent.startStr.split('T')[1].substring(0, 5) : '';
                    sameTime = existingTimeStr === eventTimeStr;
                } else {
                    sameTime = existingEvent.allDay === true;
                }
                
                return sameTitle && sameDate && sameTime;
            });
            
            if (isDuplicate) {
                showNotification('An event with the same title, date and time already exists', 'warning');
                return Promise.resolve(); // Return resolved promise to continue chain
            }
            
            return calendarService.createEvent(eventData)
                .then(savedEvent => {
                    console.log('Event saved successfully:', savedEvent);
                    // Refresh calendar to show the new event
                    calendar.refetchEvents();
                    
                    // Hide empty message when we create an event
                    forceHideEmptyMessage();
                    
                    // Update stats and reminders (with specific focus on reminders if it has one)
                    updateEventStats();
                    if (eventData.has_reminder) {
                        console.log('New event has a reminder, updating reminders list');
                    }
                    updateUpcomingReminders();
                    updateUpcomingEvents();
                    
                    // Reset form
                    resetEventForm();
                    
                    // Show success notification
                    showNotification('Event created successfully', 'success');
                })
                .catch(error => {
                    console.error('Error saving event:', error);
                    showNotification('Error creating event. Please try again.', 'danger');
                    throw error; // Re-throw to continue promise chain
                });
        } else {
            // For update, no duplicate check needed
            return calendarService.updateEvent(currentEvent.id, eventData)
                .then(updatedEvent => {
                    // Refresh calendar
                    calendar.refetchEvents();
                    
                    // Make sure empty message is hidden
                    forceHideEmptyMessage();
                    
                    // Update stats and reminders (with specific focus on reminders if changed)
                    updateEventStats();
                    const reminderChanged = 
                        currentEvent.extendedProps.hasReminder !== eventData.has_reminder || 
                        currentEvent.extendedProps.reminderMinutes !== eventData.reminder_minutes;
                        
                    if (reminderChanged) {
                        console.log('Reminder settings changed, updating reminders list');
                    }
                    updateUpcomingReminders();
                    updateUpcomingEvents();
                    
                    // Reset form
                    resetEventForm();
                    
                    showNotification('Event updated successfully', 'success');
                })
                .catch(error => {
                    console.error('Error updating event:', error);
                    showNotification('Error updating event. Please try again.', 'danger');
                    throw error; // Re-throw to continue promise chain
                });
        }
    }

    function forceHideEmptyMessage() {
        console.log('Forcing hide of empty message');
        const emptyMessage = document.getElementById('empty-calendar-message');
        if (emptyMessage) {
            emptyMessage.style.display = 'none';
            console.log('Empty message hidden');
        } else {
            console.log('Empty message element not found');
        }
    }

    // Function to delete an event
    function deleteEvent() {
        if (!currentEvent) return;
        
        calendarService.deleteEvent(currentEvent.id)
            .then(response => {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteEventModal'));
                if (modal) modal.hide();
                
                // Check if event had a reminder before removing
                const hadReminder = currentEvent.extendedProps.hasReminder;
                
                // Remove from calendar
                const event = calendar.getEventById(currentEvent.id);
                if (event) event.remove();
                
                // Reset form
                resetEventForm();
                
                // Update statistics and reminders (with specific focus on reminders if it had one)
                updateEventStats();
                if (hadReminder) {
                    console.log('Deleted event had a reminder, updating reminders list');
                }
                updateUpcomingReminders();
                updateUpcomingEvents();
                
                // Show success notification
                showNotification('Event deleted successfully', 'success');
            })
            .catch(error => {
                console.error('Error deleting event:', error);
                showNotification('Error deleting event. Please try again.', 'danger');
            });
    
    }
    

    // Function to update event date (after drag & drop or resize)
    function updateEventDate(event) {
        const eventId = event.id;
        const newStart = event.start;
        
        // Prepare the data
        const dateData = {
            date: formatDateForInput(newStart),
            time: event.allDay ? null : formatTimeForInput(newStart),
            allDay: event.allDay
        };
        
        calendarService.updateEvent(eventId, dateData)
            .then(data => {
                showNotification('Event updated successfully', 'success');
                updateUpcomingReminders();
                updateUpcomingEvents();
            })
            .catch(error => {
                console.error('Error updating event date:', error);
                showNotification('Error updating event. Please try again.', 'danger');
                calendar.refetchEvents(); // Revert the change
            });
    }

    // Function to handle reminder click
    function handleReminderClick(eventId) {
        calendarService.getEvent(eventId)
            .then(data => {
                displayEventDetails(data);
            })
            .catch(error => {
                console.error('Error fetching event details:', error);
                showNotification('Error loading event details', 'danger');
            });
    }
    
    function displayEventDetails(data) {
        // Create a FullCalendar event object
        const fcEvent = {
            id: data.id,
            title: data.title,
            start: data.time ? new Date(`${data.date}T${data.time}`) : new Date(data.date),
            allDay: !data.time,
            extendedProps: {
                type: data.type,
                location: data.location,
                description: data.description,
                hasReminder: data.has_reminder,
                reminderMinutes: data.reminder_minutes
            }
        };
        
        // Show event details
        const modalContent = document.getElementById('event-details-content');
        if (!modalContent) {
            console.error('Modal content element not found');
            return;
        }
        
        modalContent.innerHTML = `
            <div class="event-details">
                <div class="mb-3">
                    <h4 class="event-title h5">${data.title}</h4>
                    <div class="badge event-type-${data.type} mb-2">${capitalizeFirstLetter(data.type)}</div>
                </div>
                <div class="mb-3">
                    <p class="mb-1"><i class="fa-solid fa-calendar me-2"></i> <strong>Date:</strong> ${formatDate(data.date)}</p>
                    ${data.time ? `<p class="mb-1"><i class="fa-solid fa-clock me-2"></i> <strong>Time:</strong> ${formatTime(data.time)}</p>` : ''}
                    ${data.location ? `<p class="mb-1"><i class="fa-solid fa-location-dot me-2"></i> <strong>Location:</strong> ${data.location}</p>` : ''}
                    ${data.has_reminder ? `<p class="mb-1"><i class="fa-solid fa-bell me-2"></i> <strong>Reminder:</strong> ${formatReminderTime(data.reminder_minutes)}</p>` : ''}
                </div>
                ${data.description ? `
                <div class="mb-0">
                    <h5 class="h6">Description:</h5>
                    <p class="mb-0">${data.description}</p>
                </div>
                ` : ''}
            </div>
        `;
        
        // Store the event
        currentEvent = fcEvent;
        
        // Show the modal
        const eventModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
        eventModal.show();
    }

    // Utility functions
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString(document.documentElement.lang || 'en', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
    
    function formatTime(timeStr) {
        if (!timeStr) return '';
        const [hours, minutes] = timeStr.split(':');
        return new Date(0, 0, 0, hours, minutes).toLocaleTimeString(
            document.documentElement.lang || 'en', 
            { hour: '2-digit', minute: '2-digit' }
        );
    }
    
    function formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }
    
    function formatTimeForInput(date) {
        return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }).replace(/\s/g, '');
    }
    
    function formatReminderTime(minutes) {
        if (!minutes) return 'None';
        
        if (minutes === 30) return '30 minutes before';
        if (minutes === 60) return '1 hour before';
        if (minutes === 1440) return '1 day before';
        if (minutes === 10080) return '1 week before';
        
        return `${minutes} minutes before`;
    }
    
    function capitalizeFirstLetter(string) {
        return string?.charAt(0).toUpperCase() + string?.slice(1);
    }

    // Show notification function
    function showNotification(message, type) {
        if (!notificationEl) return;
        
        notificationEl.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3 shadow-sm rounded-3`;
        notificationEl.innerHTML = message;
        notificationEl.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notificationEl.style.display = 'none';
        }, 3000);
    }
});