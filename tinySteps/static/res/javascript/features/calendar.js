document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const calendarEl = document.getElementById('calendar');
    const miniCalendarEl = document.getElementById('mini-calendar');
    const eventForm = document.getElementById('event-form');
    const notificationEl = document.getElementById('notification');
    
    // Variables globales
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const childId = document.getElementById('child-id').value;
    const loadingEl = document.getElementById('calendar-loading');
    let currentEvent = null;
    
    // Set initial view based on screen size
    let initialView = 'dayGridMonth';
    if (window.innerWidth < 768) {
        initialView = 'listWeek';
    }

    // Mapa de colores para tipos de eventos
    const eventColorMap = {
        'doctor': '#2196f3',    // Azul - citas médicas
        'vaccine': '#ff9800',   // Naranja - vacunas
        'milestone': '#4caf50', // Verde - hitos de desarrollo
        'feeding': '#9c27b0',   // Púrpura - alimentación
        'other': '#757575'      // Gris - otros
    };

    // Inicializar calendario principal
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: initialView,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale: document.documentElement.lang, // Obtener idioma de la página
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
            // Mostrar indicador de carga
            if (loadingEl) loadingEl.classList.remove('d-none');
            
            // Fetch events from backend
            fetch(`/api/children/${childId}/events?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error fetching events');
                }
                return response.json();
            })
            .then(data => {
                // Mapear eventos del backend al formato de FullCalendar
                const events = data.map(event => ({
                    id: event.id,
                    title: event.title,
                    start: event.time ? `${event.date}T${event.time}` : event.date,
                    allDay: !event.time,
                    description: event.description,
                    backgroundColor: eventColorMap[event.type] || eventColorMap.other,
                    borderColor: eventColorMap[event.type] || eventColorMap.other,
                    extendedProps: {
                        type: event.type,
                        location: event.location,
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
                showNotification('Error al cargar eventos. Inténtalo de nuevo.', 'danger');
            });
        },
        eventClick: function(info) {
            // Mostrar detalles del evento en el formulario
            showEventDetails(info.event);
        },
        dateClick: function(info) {
            // Preparar formulario para nuevo evento
            resetEventForm();
            document.getElementById('event-date').value = info.dateStr;
            document.getElementById('form-title').innerHTML = '<i class="fa-solid fa-plus text-primary me-2" aria-hidden="true"></i> Añadir Evento';
        },
        eventDrop: function(info) {
            // Manejar arrastrar y soltar evento
            updateEventDate(info.event);
        },
        eventResize: function(info) {
            // Manejar cambio de tamaño del evento
            updateEventDate(info.event);
        }
    });

    // Renderizar calendario principal
    calendar.render();
    
    // Inicializar mini-calendario
    const miniCalendar = new FullCalendar.Calendar(miniCalendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev',
            center: 'title',
            right: 'next'
        },
        locale: document.documentElement.lang,
        height: 'auto',
        contentHeight: 'auto',
        dayMaxEvents: 0, // Ocultar visualización de eventos para un aspecto más limpio
        selectable: true,
        selectMirror: true,
        select: function(info) {
            // Al seleccionar fecha en mini-calendario, navegar al calendario principal
            calendar.gotoDate(info.start);
            
            // Si está en una vista diferente, cambiar a vista diaria
            if (calendar.view.type !== 'timeGridDay') {
                calendar.changeView('timeGridDay');
                updateActiveViewButton(document.getElementById('view-day'));
            }
        }
    });
    
    // Renderizar mini-calendario
    miniCalendar.render();
    
    // Sincronizar cambios de fecha del calendario principal con el mini calendario
    calendar.on('datesSet', function(info) {
        // Solo actualizar mini-calendario si la vista es diferente
        if (!areDatesEqual(miniCalendar.getDate(), info.view.currentStart)) {
            miniCalendar.gotoDate(info.view.currentStart);
        }
    });
    
    // Función para verificar si dos fechas son iguales
    function areDatesEqual(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    // Actualizar botón de vista activo
    function updateActiveViewButton(clickedBtn) {
        const viewButtons = document.querySelectorAll('.view-button');
        viewButtons.forEach(btn => btn.classList.remove('active'));
        clickedBtn.classList.add('active');
    }

    // Manejar botones de vista
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

    // Toggle del campo de recordatorio cuando se cambia el checkbox
    const reminderCheckbox = document.getElementById('event-reminder');
    const reminderOptions = document.getElementById('reminder-options');
    
    reminderCheckbox.addEventListener('change', function() {
        reminderOptions.style.display = this.checked ? 'block' : 'none';
    });

    // Manejar envío del formulario de evento
    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveEvent();
    });

    // Botón para eliminar evento
    document.getElementById('btn-delete').addEventListener('click', function() {
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteEventModal'));
        deleteModal.show();
    });

    // Confirmar eliminación de evento
    document.getElementById('btn-confirm-delete').addEventListener('click', function() {
        if (currentEvent) {
            deleteEvent(currentEvent.id);
        }
    });

    // Botón cancelar en el formulario
    document.getElementById('btn-cancel').addEventListener('click', function() {
        resetEventForm();
    });

    // Función para mostrar detalles del evento en el formulario
    function showEventDetails(event) {
        currentEvent = event;
        
        // Actualizar título del formulario
        document.getElementById('form-title').innerHTML = '<i class="fa-solid fa-edit text-primary me-2" aria-hidden="true"></i> Editar Evento';
        
        // Completar formulario con datos del evento
        document.getElementById('event-title').value = event.title;
        document.getElementById('event-type').value = event.extendedProps.type || 'other';
        
        // Formatear fecha para input date (YYYY-MM-DD)
        const eventDate = new Date(event.start);
        const formattedDate = eventDate.toISOString().split('T')[0];
        document.getElementById('event-date').value = formattedDate;
        
        // Manejar hora si existe
        if (!event.allDay && event.start) {
            const hours = eventDate.getHours().toString().padStart(2, '0');
            const minutes = eventDate.getMinutes().toString().padStart(2, '0');
            document.getElementById('event-time').value = `${hours}:${minutes}`;
        } else {
            document.getElementById('event-time').value = '';
        }
        
        // Ubicación y notas
        document.getElementById('event-location').value = event.extendedProps.location || '';
        document.getElementById('event-notes').value = event.description || '';
        
        // Recordatorio
        const hasReminder = event.extendedProps.hasReminder || false;
        document.getElementById('event-reminder').checked = hasReminder;
        reminderOptions.style.display = hasReminder ? 'block' : 'none';
        
        if (hasReminder && event.extendedProps.reminderMinutes) {
            document.getElementById('reminder-time').value = event.extendedProps.reminderMinutes;
        }
        
        // Mostrar botones de edición
        document.getElementById('btn-delete').style.display = 'block';
        document.getElementById('btn-cancel').style.display = 'block';
        document.getElementById('btn-save').innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Actualizar Evento';
    }

    // Función para guardar evento (crear o actualizar)
    function saveEvent() {
        const eventData = {
            title: document.getElementById('event-title').value,
            type: document.getElementById('event-type').value,
            date: document.getElementById('event-date').value,
            time: document.getElementById('event-time').value || null,
            location: document.getElementById('event-location').value,
            description: document.getElementById('event-notes').value,
            has_reminder: document.getElementById('event-reminder').checked,
            reminder_minutes: document.getElementById('event-reminder').checked ? 
                              document.getElementById('reminder-time').value : null,
            child: childId
        };
        
        let url = `/api/children/${childId}/events/`;
        let method = 'POST';
        
        if (currentEvent) {
            url = `/api/calendar-events/${currentEvent.id}/`;
            method = 'PUT';
        }
        
        fetch(url, {
            method: method,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error saving event');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar calendario
            calendar.refetchEvents();
            
            // Actualizar estadísticas y recordatorios
            updateEventStats();
            updateUpcomingReminders();
            
            // Resetear formulario
            resetEventForm();
            
            // Mostrar notificación
            showNotification(
                currentEvent ? 'Evento actualizado correctamente.' : 'Evento creado correctamente.', 
                'success'
            );
            
            currentEvent = null;
        })
        .catch(error => {
            console.error('Error saving event:', error);
            showNotification('Error al guardar el evento. Inténtalo de nuevo.', 'danger');
        });
    }

    // Función para eliminar evento
    function deleteEvent(eventId) {
        fetch(`/api/calendar-events/${eventId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error deleting event');
            }
            
            // Cerrar modal de confirmación
            const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteEventModal'));
            deleteModal.hide();
            
            // Actualizar calendario
            calendar.refetchEvents();
            
            // Actualizar estadísticas y recordatorios
            updateEventStats();
            updateUpcomingReminders();
            
            // Resetear formulario
            resetEventForm();
            
            // Mostrar notificación
            showNotification('Evento eliminado correctamente.', 'success');
            
            currentEvent = null;
        })
        .catch(error => {
            console.error('Error deleting event:', error);
            showNotification('Error al eliminar el evento. Inténtalo de nuevo.', 'danger');
        });
    }

    // Función para actualizar fecha de evento (arrastrar y soltar)
    function updateEventDate(event) {
        const eventStart = event.start;
        const eventData = {
            date: eventStart.toISOString().split('T')[0]
        };
        
        if (!event.allDay && eventStart) {
            const hours = eventStart.getHours().toString().padStart(2, '0');
            const minutes = eventStart.getMinutes().toString().padStart(2, '0');
            eventData.time = `${hours}:${minutes}`;
        } else {
            eventData.time = null;
        }
        
        fetch(`/api/calendar-events/${event.id}/update-date/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error updating event date');
            }
            
            // Mostrar notificación
            showNotification('Fecha del evento actualizada correctamente.', 'success');
            
            // Actualizar recordatorios
            updateUpcomingReminders();
        })
        .catch(error => {
            console.error('Error updating event date:', error);
            showNotification('Error al actualizar la fecha. Inténtalo de nuevo.', 'danger');
            calendar.refetchEvents(); // Revertir cambio visual
        });
    }

    // Función para actualizar estadísticas de eventos
    function updateEventStats() {
        fetch(`/api/children/${childId}/events/event_stats/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching event stats');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar contadores en la UI
            if (document.getElementById('doctor-count')) {
                document.getElementById('doctor-count').textContent = data.doctor || 0;
            }
            if (document.getElementById('vaccine-count')) {
                document.getElementById('vaccine-count').textContent = data.vaccine || 0;
            }
            if (document.getElementById('milestone-count')) {
                document.getElementById('milestone-count').textContent = data.milestone || 0;
            }
            if (document.getElementById('total-events')) {
                document.getElementById('total-events').textContent = data.total || 0;
            }
            if (document.getElementById('upcoming-count')) {
                document.getElementById('upcoming-count').textContent = data.upcoming || 0;
            }
        })
        .catch(error => {
            console.error('Error fetching event stats:', error);
        });
    }

    // Función para actualizar lista de recordatorios próximos
    function updateUpcomingReminders() {
        fetch(`/api/children/${childId}/events/upcoming_events/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching upcoming events');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar lista de recordatorios
            const remindersList = document.getElementById('upcoming-reminders');
            if (!remindersList) return;
            
            if (data.reminders && data.reminders.length > 0) {
                let html = '';
                data.reminders.forEach(reminder => {
                    const reminderDate = new Date(reminder.date);
                    const formattedDate = reminderDate.toLocaleDateString();
                    
                    html += `
                    <li class="list-group-item reminder-item d-flex justify-content-between align-items-start" data-event-id="${reminder.id}">
                        <div>
                            <h4 class="h6 mb-1">${reminder.title}</h4>
                            <p class="small text-muted mb-0 d-flex align-items-center">
                                <i class="fa-solid fa-calendar-day me-1" aria-hidden="true"></i>
                                ${formattedDate}
                                ${reminder.time ? `<span class="mx-1">•</span><i class="fa-solid fa-clock me-1" aria-hidden="true"></i>${reminder.time}` : ''}
                            </p>
                        </div>
                        <span class="badge event-type-${reminder.type}">${getEventTypeName(reminder.type)}</span>
                    </li>`;
                });
                
                remindersList.innerHTML = html;
                
                // Añadir listener para click en recordatorios
                document.querySelectorAll('.reminder-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const eventId = this.getAttribute('data-event-id');
                        const fcEvent = calendar.getEventById(eventId);
                        if (fcEvent) {
                            showEventDetails(fcEvent);
                        } else {
                            // Si no está en la vista actual, cargar directamente
                            fetch(`/api/calendar-events/${eventId}/`, {
                                method: 'GET',
                                headers: {
                                    'X-CSRFToken': csrfToken
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                // Crear objeto de evento temporal
                                const tempEvent = {
                                    id: data.id,
                                    title: data.title,
                                    start: data.time ? new Date(`${data.date}T${data.time}`) : new Date(data.date),
                                    allDay: !data.time,
                                    description: data.description,
                                    extendedProps: {
                                        type: data.type,
                                        location: data.location,
                                        hasReminder: data.has_reminder,
                                        reminderMinutes: data.reminder_minutes
                                    }
                                };
                                showEventDetails(tempEvent);
                            })
                            .catch(error => {
                                console.error('Error loading event details:', error);
                            });
                        }
                    });
                });
                
                // Mostrar contador actualizado
                const reminderBadge = document.querySelector('.card-header .badge');
                if (reminderBadge) {
                    reminderBadge.textContent = data.reminders.length;
                }
                
                // Ocultar mensaje de "no hay recordatorios"
                if (document.getElementById('no-reminders')) {
                    document.getElementById('no-reminders').style.display = 'none';
                }
            } else {
                // Mostrar mensaje de "no hay recordatorios"
                remindersList.innerHTML = `
                <li class="list-group-item text-center py-3" id="no-reminders">
                    <p class="mb-0 text-muted">No hay recordatorios próximos</p>
                </li>`;
                
                // Actualizar contador a 0
                const reminderBadge = document.querySelector('.card-header .badge');
                if (reminderBadge) {
                    reminderBadge.textContent = '0';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching upcoming events:', error);
        });
    }

    // Función para obtener nombre legible del tipo de evento
    function getEventTypeName(type) {
        const typeMap = {
            'doctor': 'Médico',
            'vaccine': 'Vacuna',
            'milestone': 'Hito',
            'feeding': 'Alimentación',
            'other': 'Otro'
        };
        return typeMap[type] || 'Otro';
    }

    // Función para resetear formulario
    function resetEventForm() {
        eventForm.reset();
        document.getElementById('form-title').innerHTML = '<i class="fa-solid fa-plus text-primary me-2" aria-hidden="true"></i> Añadir Evento';
        document.getElementById('btn-delete').style.display = 'none';
        document.getElementById('btn-cancel').style.display = 'none';
        document.getElementById('btn-save').innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Guardar Evento';
        document.getElementById('reminder-options').style.display = 'none';
        currentEvent = null;
    }

    // Función para mostrar notificaciones
    function showNotification(message, type) {
        if (!notificationEl) return;
        
        notificationEl.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3 shadow-sm rounded-3`;
        notificationEl.innerHTML = message;
        notificationEl.style.display = 'block';
        
        // Auto-ocultar después de 3 segundos
        setTimeout(() => {
            notificationEl.style.display = 'none';
        }, 3000);
    }

    // Inicializar datos
    updateEventStats();
    updateUpcomingReminders();
});