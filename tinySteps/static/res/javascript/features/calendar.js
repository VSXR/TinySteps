document.addEventListener('DOMContentLoaded', function() {
    const childId = document.getElementById('child-id').value;
    const calendarEl = document.getElementById('calendar');
    const eventForm = document.getElementById('event-form');
    const eventIdInput = document.getElementById('event-id');
    const btnDelete = document.getElementById('btn-delete');
    const btnCancel = document.getElementById('btn-cancel');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
    // Inicializa FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: `/child/${childId}/events/`,  // Llama a la API para obtener los eventos
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale: 'es',
        eventClick: function(info) {
            // Al hacer click en un evento se rellenan los campos del formulario para editar
            console.log("Evento seleccionado:", info.event);
            eventIdInput.value = info.event.id;
            document.getElementById('event-title').value = info.event.title;
  
            // Asigna el tipo de evento (usando extendedProps)
            if (info.event.extendedProps && info.event.extendedProps.event_type) {
                document.getElementById('event-type').value = info.event.extendedProps.event_type;
            }
  
            // Extrae la fecha y la hora del evento
            let start = new Date(info.event.start);
            document.getElementById('event-date').value = start.toISOString().split('T')[0];
            let hours = start.getHours().toString().padStart(2, '0');
            let minutes = start.getMinutes().toString().padStart(2, '0');
            document.getElementById('event-time').value = hours + ":" + minutes;
  
            // Rellena la descripción
            document.getElementById('event-description').value = info.event.extendedProps.description || "";
  
            // Maneja la opción de recordatorio
            if (info.event.extendedProps.has_reminder) {
                document.getElementById('event-reminder').checked = true;
                document.getElementById('reminder-options').style.display = 'block';
                if (info.event.extendedProps.reminder_minutes) {
                    document.getElementById('reminder-time').value = info.event.extendedProps.reminder_minutes;
                }
            } else {
                document.getElementById('event-reminder').checked = false;
                document.getElementById('reminder-options').style.display = 'none';
                document.getElementById('reminder-time').value = 60;
            }
  
            // Muestra los botones de eliminar y cancelar
            btnDelete.style.display = 'block';
            btnCancel.style.display = 'block';
        }
    });
  
    calendar.render();
  
    // Funcionalidad de los botones de vista del calendario
    document.getElementById('view-month').addEventListener('click', function() {
        calendar.changeView('dayGridMonth');
    });
    document.getElementById('view-week').addEventListener('click', function() {
        calendar.changeView('timeGridWeek');
    });
    document.getElementById('view-day').addEventListener('click', function() {
        calendar.changeView('timeGridDay');
    });
    document.getElementById('view-list').addEventListener('click', function() {
        calendar.changeView('listWeek');
    });
  
    // Botón "Today"
    document.getElementById('calendar-today').addEventListener('click', function() {
        calendar.today();
    });
  
    // Mostrar/Ocultar opciones de recordatorio al marcar el checkbox
    document.getElementById('event-reminder').addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('reminder-options').style.display = 'block';
        } else {
            document.getElementById('reminder-options').style.display = 'none';
        }
    });
  
    // Envío del formulario para crear o actualizar un evento
    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
  
        const payload = {
            id: eventIdInput.value || null,
            title: document.getElementById('event-title').value,
            event_type: document.getElementById('event-type').value,
            date: document.getElementById('event-date').value,
            time: document.getElementById('event-time').value,
            description: document.getElementById('event-description').value,
            has_reminder: document.getElementById('event-reminder').checked,
            reminder_minutes: document.getElementById('reminder-time').value
        };
  
        fetch(`/child/${childId}/events/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Evento guardado:', data);
            calendar.refetchEvents();
            eventForm.reset();
            eventIdInput.value = "";
            // Oculta los botones de eliminar y cancelar tras guardar
            btnDelete.style.display = 'none';
            btnCancel.style.display = 'none';
            document.getElementById('reminder-options').style.display = 'none';
        })
        .catch(error => console.error('Error al guardar el evento:', error));
    });
  
    // Botón de cancelar: reinicia el formulario
    btnCancel.addEventListener('click', function() {
        eventForm.reset();
        eventIdInput.value = "";
        btnDelete.style.display = 'none';
        btnCancel.style.display = 'none';
        document.getElementById('reminder-options').style.display = 'none';
    });
  
    // Funcionalidad para eliminar un evento
    btnDelete.addEventListener('click', function() {
        const eventId = eventIdInput.value;
        if (eventId && confirm("¿Estás seguro de eliminar este evento?")) {
            fetch(`/child/${childId}/events/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ id: eventId })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Evento eliminado:', data);
                calendar.refetchEvents();
                eventForm.reset();
                eventIdInput.value = "";
                btnDelete.style.display = 'none';
                btnCancel.style.display = 'none';
                document.getElementById('reminder-options').style.display = 'none';
            })
            .catch(error => console.error('Error al eliminar el evento:', error));
        }
    });
});
