/**
 * Vaccine Card - JavaScript functionality
 * Manages the vaccine tracking functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // ----- VARIABLES AND DOM ELEMENTS -----
    // Global variables
    const childId = document.getElementById('child-id')?.value;
    const vaccineCardId = document.getElementById('vaccine-card-id')?.value;
    let currentVaccines = [];
    let editingVaccineId = null;
    
    // DOM Elements
    const vaccineForm = document.getElementById('vaccine-form');
    const formTitle = document.getElementById('form-title');
    const vaccineIdInput = document.getElementById('vaccine-id');
    const vaccineNameInput = document.getElementById('vaccine-name');
    const vaccineDateInput = document.getElementById('vaccine-date');
    const vaccineAdministeredInput = document.getElementById('vaccine-administered');
    const vaccineNextDoseInput = document.getElementById('vaccine-next-dose');
    const vaccineNotesInput = document.getElementById('vaccine-notes');
    const saveButton = document.getElementById('btn-save');
    const cancelButton = document.getElementById('btn-cancel');
    const deleteButton = document.getElementById('btn-delete');
    const vaccineSearch = document.getElementById('vaccine-search');
    const btnFilterAll = document.getElementById('btn-filter-all');
    const btnFilterAdministered = document.getElementById('btn-filter-administered');
    const btnFilterPending = document.getElementById('btn-filter-pending');
    const btnAddFirstVaccine = document.getElementById('btn-add-first-vaccine');
    const deleteVaccineModal = new bootstrap.Modal(document.getElementById('deleteVaccineModal'));
    const btnConfirmDelete = document.getElementById('btn-confirm-delete');
    
    // ----- EVENT LISTENERS -----
    // Form events
    if (vaccineForm) {
        vaccineForm.addEventListener('submit', handleSubmitVaccine);
    }
    
    if (cancelButton) {
        cancelButton.addEventListener('click', resetForm);
    }
    
    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            // Show confirmation modal
            deleteVaccineModal.show();
        });
    }
    
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener('click', handleDeleteVaccine);
    }
    
    // Search and filter events
    if (vaccineSearch) {
        vaccineSearch.addEventListener('input', filterVaccines);
    }
    
    if (btnFilterAll) {
        btnFilterAll.addEventListener('click', function() {
            showAllVaccines();
            setActiveFilterButton(this);
        });
    }
    
    if (btnFilterAdministered) {
        btnFilterAdministered.addEventListener('click', function() {
            filterVaccinesByStatus(true);
            setActiveFilterButton(this);
        });
    }
    
    if (btnFilterPending) {
        btnFilterPending.addEventListener('click', function() {
            filterVaccinesByStatus(false);
            setActiveFilterButton(this);
        });
    }
    
    if (btnAddFirstVaccine) {
        btnAddFirstVaccine.addEventListener('click', function() {
            resetForm();
            vaccineNameInput.focus();
        });
    }
    
    // Connect edit/delete buttons for existing vaccines
    document.querySelectorAll('.btn-edit-vaccine').forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            const vaccineId = this.closest('.vaccine-row').dataset.vaccineId;
            editVaccine(vaccineId);
        });
    });
    
    document.querySelectorAll('.btn-delete-vaccine').forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            const vaccineId = this.closest('.vaccine-row').dataset.vaccineId;
            prepareDeleteVaccine(vaccineId);
        });
    });
    
    // Make entire row clickable to edit
    document.querySelectorAll('.vaccine-row').forEach(row => {
        row.addEventListener('click', function() {
            const vaccineId = this.dataset.vaccineId;
            editVaccine(vaccineId);
        });
        
        // Also make the row accessible via keyboard
        row.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                const vaccineId = this.dataset.vaccineId;
                editVaccine(vaccineId);
            }
        });
    });

    // ----- INITIALIZATION -----
    // Set default filter button
    setActiveFilterButton(btnFilterAll);
    
    // Set default date in form to today
    const today = new Date();
    if (vaccineDateInput) {
        vaccineDateInput.value = formatDateForInput(today);
    }
    
    // ----- MAIN FUNCTIONS -----
    function handleSubmitVaccine(event) {
        event.preventDefault();
        
        const vaccineData = {
            name: vaccineNameInput.value,
            date: vaccineDateInput.value,
            administered: vaccineAdministeredInput.checked,
            next_dose_date: vaccineNextDoseInput.value || null,
            notes: vaccineNotesInput.value,
            vaccine_card: vaccineCardId
        };
        
        if (editingVaccineId) {
            // Update existing vaccine
            updateVaccine(editingVaccineId, vaccineData);
        } else {
            // Create new vaccine
            createVaccine(vaccineData);
        }
    }
    
    function createVaccine(vaccineData) {
        // Show loading state
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Call the API to create the vaccine
        api.addVaccine(vaccineCardId, vaccineData)
            .then(response => {
                // Show success message
                showNotification('Vacuna añadida correctamente', 'success');
                
                // Reset form
                resetForm();
                
                // Reload the page to show the new vaccine
                // In a real app, you might want to update the DOM instead
                setTimeout(() => window.location.reload(), 1000);
            })
            .catch(error => {
                console.error('Error creating vaccine:', error);
                showNotification('Error al crear la vacuna', 'error');
            })
            .finally(() => {
                // Reset button state
                saveButton.disabled = false;
                saveButton.innerHTML = 'Guardar Vacuna';
            });
    }
    
    function updateVaccine(vaccineId, vaccineData) {// filepath: c:\Users\VICTOR\code\UFV\PROYECTOS_2\__PRUEBAS\TinySteps\tinySteps\static\res\javascript\features\vaccine-card.js
/**
 * Vaccine Card - JavaScript functionality
 * Manages the vaccine tracking functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // ----- VARIABLES AND DOM ELEMENTS -----
    // Global variables
    const childId = document.getElementById('child-id')?.value;
    const vaccineCardId = document.getElementById('vaccine-card-id')?.value;
    let currentVaccines = [];
    let editingVaccineId = null;
    
    // DOM Elements
    const vaccineForm = document.getElementById('vaccine-form');
    const formTitle = document.getElementById('form-title');
    const vaccineIdInput = document.getElementById('vaccine-id');
    const vaccineNameInput = document.getElementById('vaccine-name');
    const vaccineDateInput = document.getElementById('vaccine-date');
    const vaccineAdministeredInput = document.getElementById('vaccine-administered');
    const vaccineNextDoseInput = document.getElementById('vaccine-next-dose');
    const vaccineNotesInput = document.getElementById('vaccine-notes');
    const saveButton = document.getElementById('btn-save');
    const cancelButton = document.getElementById('btn-cancel');
    const deleteButton = document.getElementById('btn-delete');
    const vaccineSearch = document.getElementById('vaccine-search');
    const btnFilterAll = document.getElementById('btn-filter-all');
    const btnFilterAdministered = document.getElementById('btn-filter-administered');
    const btnFilterPending = document.getElementById('btn-filter-pending');
    const btnAddFirstVaccine = document.getElementById('btn-add-first-vaccine');
    const deleteVaccineModal = new bootstrap.Modal(document.getElementById('deleteVaccineModal'));
    const btnConfirmDelete = document.getElementById('btn-confirm-delete');
    
    // ----- EVENT LISTENERS -----
    // Form events
    if (vaccineForm) {
        vaccineForm.addEventListener('submit', handleSubmitVaccine);
    }
    
    if (cancelButton) {
        cancelButton.addEventListener('click', resetForm);
    }
    
    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            // Show confirmation modal
            deleteVaccineModal.show();
        });
    }
    
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener('click', handleDeleteVaccine);
    }
    
    // Search and filter events
    if (vaccineSearch) {
        vaccineSearch.addEventListener('input', filterVaccines);
    }
    
    if (btnFilterAll) {
        btnFilterAll.addEventListener('click', function() {
            showAllVaccines();
            setActiveFilterButton(this);
        });
    }
    
    if (btnFilterAdministered) {
        btnFilterAdministered.addEventListener('click', function() {
            filterVaccinesByStatus(true);
            setActiveFilterButton(this);
        });
    }
    
    if (btnFilterPending) {
        btnFilterPending.addEventListener('click', function() {
            filterVaccinesByStatus(false);
            setActiveFilterButton(this);
        });
    }
    
    if (btnAddFirstVaccine) {
        btnAddFirstVaccine.addEventListener('click', function() {
            resetForm();
            vaccineNameInput.focus();
        });
    }
    
    // Connect edit/delete buttons for existing vaccines
    document.querySelectorAll('.btn-edit-vaccine').forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            const vaccineId = this.closest('.vaccine-row').dataset.vaccineId;
            editVaccine(vaccineId);
        });
    });
    
    document.querySelectorAll('.btn-delete-vaccine').forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            const vaccineId = this.closest('.vaccine-row').dataset.vaccineId;
            prepareDeleteVaccine(vaccineId);
        });
    });
    
    // Make entire row clickable to edit
    document.querySelectorAll('.vaccine-row').forEach(row => {
        row.addEventListener('click', function() {
            const vaccineId = this.dataset.vaccineId;
            editVaccine(vaccineId);
        });
        
        // Also make the row accessible via keyboard
        row.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                const vaccineId = this.dataset.vaccineId;
                editVaccine(vaccineId);
            }
        });
    });

    // ----- INITIALIZATION -----
    // Set default filter button
    setActiveFilterButton(btnFilterAll);
    
    // Set default date in form to today
    const today = new Date();
    if (vaccineDateInput) {
        vaccineDateInput.value = formatDateForInput(today);
    }
    
    // ----- MAIN FUNCTIONS -----
    function handleSubmitVaccine(event) {
        event.preventDefault();
        
        const vaccineData = {
            name: vaccineNameInput.value,
            date: vaccineDateInput.value,
            administered: vaccineAdministeredInput.checked,
            next_dose_date: vaccineNextDoseInput.value || null,
            notes: vaccineNotesInput.value,
            vaccine_card: vaccineCardId
        };
        
        if (editingVaccineId) {
            // Update existing vaccine
            updateVaccine(editingVaccineId, vaccineData);
        } else {
            // Create new vaccine
            createVaccine(vaccineData);
        }
    }
    
    function createVaccine(vaccineData) {
        // Show loading state
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Call the API to create the vaccine
        api.addVaccine(vaccineCardId, vaccineData)
            .then(response => {
                // Show success message
                showNotification('Vacuna añadida correctamente', 'success');
                
                // Reset form
                resetForm();
                
                // Reload the page to show the new vaccine
                // In a real app, you might want to update the DOM instead
                setTimeout(() => window.location.reload(), 1000);
            })
            .catch(error => {
                console.error('Error creating vaccine:', error);
                showNotification('Error al crear la vacuna', 'error');
            })
            .finally(() => {
                // Reset button state
                saveButton.disabled = false;
                saveButton.innerHTML = 'Guardar Vacuna';
            });
    }
    
    function updateVaccine(vaccineId, vaccineData) {
        // Show loading state
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Call the API to update the vaccine
        api.updateVaccine(vaccineId, vaccineData)
            .then(response => {
                // Show success message
                showNotification('Vacuna actualizada correctamente', 'success');
                
                // Reset form
                resetForm();
                
                // Reload the page to show the updated vaccine
                // In a real app, you might want to update the DOM instead
                setTimeout(() => window.location.reload(), 1000);
            })
            .catch(error => {
                console.error('Error updating vaccine:', error);
                showNotification('Error al actualizar la vacuna', 'error');
            })
            .finally(() => {
                // Reset button state
                saveButton.disabled = false;
                saveButton.innerHTML = 'Guardar Vacuna';
            });
    }

    