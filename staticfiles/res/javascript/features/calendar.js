document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado - Iniciando calendario');
    
    // Verificar elementos clave
    const calendarEl = document.getElementById('calendar');
    console.log('Elemento calendario principal:', calendarEl);
    
    const miniCalendarEl = document.getElementById('mini-calendar');
    console.log('Elemento mini-calendario:', miniCalendarEl);
    
    const eventForm = document.getElementById('event-form');
    console.log('Formulario de eventos:', eventForm);
    
    // Get CSRF token for AJAX requests
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const childId = document.getElementById('child-id').value;
    const loadingEl = document.getElementById('calendar-loading');
    
    // Set initial view based on screen size
    let initialView = 'dayGridMonth';
    if (window.innerWidth < 768) {
        initialView = 'listWeek';
    }

    // Function to get event color based on type
    function getEventColor(eventType) {
        const colorMap = {
            'milestone': '#4caf50',  // Green
            'appointment': '#2196f3', // Blue
            'task': '#ff9800',       // Orange
            'reminder': '#9c27b0'    // Purple
        };
        return colorMap[eventType] || '#757575'; // Default gray
    }

    // Initialize the calendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: initialView,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
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
            // Show loading indicator
            if (loadingEl) loadingEl.classList.remove('d-none');
            
            // Fetch events from your Django backend
            fetch(`/api/children/${childId}/events?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Map backend events to FullCalendar format
                const events = data.map(event => ({
                    id: event.id,
                    title: event.title,
                    start: event.time ? `${event.date}T${event.time}` : event.date,
                    allDay: !event.time,
                    description: event.description,
                    backgroundColor: getEventColor(event.type),
                    borderColor: getEventColor(event.type),
                    extendedProps: {
                        type: event.type,
                        hasReminder: event.has_reminder,
                        reminderMinutes: event.reminder_minutes
                    }
                }));
                successCallback(events);
                if (loadingEl) loadingEl.classList.add('d-none');
                updateEventStats();
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                failureCallback(error);
                if (loadingEl) loadingEl.classList.add('d-none');
                showNotification('Error loading events. Please try again.', 'danger');
            });
        },
        eventClick: function(info) {
            // Handle event click - show details in the form
            showEventDetails(info.event);
        },
        dateClick: function(info) {
            // Handle date click - prepare form for new event
            resetEventForm();
            document.getElementById('event-date').value = info.dateStr;
            document.getElementById('form-title').textContent = 'Add Event';
        },
        eventDrop: function(info) {
            // Handle event drag and drop
            updateEventDate(info.event);
        },
        eventResize: function(info) {
            // Handle event resize
            updateEventDate(info.event);
        }
    });

    // Render the calendar
    calendar.render();
    
    // Initialize mini-calendar
    const miniCalendar = new FullCalendar.Calendar(miniCalendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev',
            center: 'title',
            right: 'next'
        },
        height: 'auto',
        contentHeight: 'auto',
        dayMaxEvents: 0, // Hide event display for cleaner look
        selectable: true,
        selectMirror: true,
        select: function(info) {
            // When selecting a date in mini-calendar, navigate main calendar to that date
            calendar.gotoDate(info.start);
            
            // If on a different view than day, switch to day view
            if (calendar.view.type !== 'timeGridDay') {
                calendar.changeView('timeGridDay');
                updateActiveViewButton(document.getElementById('view-day'));
            }
        }
    });
    
    // Render the mini-calendar
    miniCalendar.render();
    
    // Synchronize main calendar date changes with mini calendar
    calendar.on('datesSet', function(info) {
        // Only update mini-calendar if the view is different
        if (!areDatesEqual(miniCalendar.getDate(), info.view.currentStart)) {
            miniCalendar.gotoDate(info.view.currentStart);
        }
    });
    
    // Add a helper function to check if dates are equal
    function areDatesEqual(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    // Update active view button
    function updateActiveViewButton(clickedBtn) {
        const viewButtons = document.querySelectorAll('.view-button');
        viewButtons.forEach(btn => btn.classList.remove('active'));
        clickedBtn.classList.add('active');
    }

    // Handle view buttons
    document.getElementById('view-month').addEventListener('click', function() {
        calendar.changeView('dayGridMonth');
        updateActiveViewButton(this);
    });

    document.getElementById('view-week').addEventListener('click', function() {
        calendar.changeView('timeGridWeek');
        updateActiveViewButton(this);
    });

    document.getElementById('view-day').addEventListener('click', function() {
        calendar.changeView('timeGridDay');
        updateActiveViewButton(this);
    });

    document.getElementById('view-list').addEventListener('click', function() {
        calendar.changeView('listWeek');
        updateActiveViewButton(this);
    });

    // Function stubs for referenced functions that need to be implemented
    function showEventDetails(event) {
        // TODO: Implement this function to show event details in the form
        console.log('Show event details:', event);
    }

    function resetEventForm() {
        // TODO: Implement this function to reset the event form
        console.log('Reset event form');
    }

    function updateEventDate(event) {
        // TODO: Implement this function to update event date on drop or resize
        console.log('Update event date:', event);
    }

    function updateEventStats() {
        // TODO: Implement this function to update event statistics
        console.log('Update event stats');
    }

    function showNotification(message, type) {
        // TODO: Implement this function to show notifications
        console.log(`Notification (${type}):`, message);
    }

    console.log('Inicialización de calendario completada');
});
