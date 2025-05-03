import vaccineCardService from '../services/vaccine-card-service.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const vaccineForm = document.getElementById('vaccine-form');
    const vaccineListDesktop = document.getElementById('vaccine-list-desktop');
    const vaccineListMobile = document.getElementById('vaccine-list-mobile');
    const upcomingVaccinesList = document.getElementById('upcoming-vaccines-list');
    const notificationEl = document.getElementById('notification');
    
    // Global variables
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    const childId = document.getElementById('child-id')?.value;
    const vaccineCardId = document.getElementById('vaccine-card-id')?.value;
    let currentVaccine = null;
    
    // Initialize
    loadVaccines();
    updateVaccineStats();
    updateUpcomingVaccines();
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // === Filter Buttons ===
    const btnFilterAll = document.getElementById('btn-filter-all');
    const btnFilterAdministered = document.getElementById('btn-filter-administered');
    const btnFilterPending = document.getElementById('btn-filter-pending');
    
    if (btnFilterAll) {
        btnFilterAll.addEventListener('click', function() {
            setActiveFilter(this);
            filterVaccines('all');
        });
    }
    
    if (btnFilterAdministered) {
        btnFilterAdministered.addEventListener('click', function() {
            setActiveFilter(this);
            filterVaccines('administered');
        });
    }
    
    if (btnFilterPending) {
        btnFilterPending.addEventListener('click', function() {
            setActiveFilter(this);
            filterVaccines('pending');
        });
    }
    
    // === Search Input ===
    const vaccineSearch = document.getElementById('vaccine-search');
    if (vaccineSearch) {
        vaccineSearch.addEventListener('input', function() {
            searchVaccines(this.value.toLowerCase().trim());
        });
    }
    
    // === Form Submission ===
    if (vaccineForm) {
        // Add a flag to track if submission is in progress
        let isSubmitting = false;
        
        vaccineForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Prevent multiple submissions
            if (isSubmitting) {
                console.log('Submission already in progress, ignoring duplicate submit');
                return;
            }
            
            isSubmitting = true;
            saveVaccine().finally(() => {
                // Reset submission flag when complete (whether success or error)
                setTimeout(() => {
                    isSubmitting = false;
                }, 500);
            });
        });
    }
    
    // === Delete Button ===
    const deleteBtn = document.getElementById('btn-delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            if (currentVaccine) {
                const deleteModal = new bootstrap.Modal(document.getElementById('deleteVaccineModal'));
                deleteModal.show();
            }
        });
    }
    
    // === Confirm Delete Button ===
    const confirmDeleteBtn = document.getElementById('btn-confirm-delete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            deleteVaccine();
        });
    }
    
    // === Cancel Button ===
    const cancelBtn = document.getElementById('btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            resetVaccineForm();
        });
    }
    
    // === Add First Vaccine Buttons ===
    const addFirstVaccineDesktop = document.getElementById('btn-add-first-vaccine-desktop');
    if (addFirstVaccineDesktop) {
        addFirstVaccineDesktop.addEventListener('click', function() {
            resetVaccineForm();
            scrollToForm();
        });
    }
    
    const addFirstVaccineMobile = document.getElementById('btn-add-first-vaccine-mobile');
    if (addFirstVaccineMobile) {
        addFirstVaccineMobile.addEventListener('click', function() {
            resetVaccineForm();
            scrollToForm();
        });
    }

    // === Functions ===
    
    // Set active filter button
    function setActiveFilter(button) {
        const filterButtons = document.querySelectorAll('.filter-button');
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }
    
    // Load vaccines
    function loadVaccines() {
        vaccineCardService.getVaccines(vaccineCardId)
            .then(data => {
                console.log('Vaccines loaded:', data.vaccines);
                renderVaccines(data.vaccines);
            })
            .catch(error => {
                console.error('Error loading vaccines:', error);
                showNotification('Error loading vaccines. Please try again.', 'danger');
            });
    }
    
    // Render vaccines
    function renderVaccines(vaccines) {
        // Clear existing vaccines
        if (vaccineListDesktop) {
            // Display empty state if no vaccines
            if (vaccines.length === 0) {
                const emptyState = `
                    <tr>
                        <td colspan="5" class="p-0">
                            <div class="empty-container mt-3 mb-4">
                                <div class="empty-card">
                                    <div class="empty-icon-wrapper">
                                        <i class="fa-solid fa-syringe empty-icon" aria-hidden="true"></i>
                                    </div>
                                    <div class="empty-content">
                                        <h2 class="empty-title">No Vaccines Registered</h2>
                                        <p class="empty-message">Start recording your child's vaccines to keep track of their immunization history.</p>
                                        
                                        <button id="btn-add-first-vaccine-desktop" class="empty-button">
                                            <i class="fa-solid fa-plus me-2" aria-hidden="true"></i> Add First Vaccine
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
                vaccineListDesktop.innerHTML = emptyState;
                
                // Add event listener for the new button
                const newAddBtn = document.getElementById('btn-add-first-vaccine-desktop');
                if (newAddBtn) {
                    newAddBtn.addEventListener('click', function() {
                        resetVaccineForm();
                        scrollToForm();
                    });
                }
            } else {
                vaccineListDesktop.innerHTML = '';
                
                // Add each vaccine
                vaccines.forEach((vaccine, index) => {
                    const row = document.createElement('tr');
                    row.className = 'vaccine-row animate-entry';
                    row.dataset.vaccineId = vaccine.id;
                    row.tabIndex = 0;
                    row.role = 'button';
                    row.setAttribute('aria-label', `Vaccine: ${vaccine.name}`);
                    row.style.animationDelay = `${index * 0.05}s`; // Staggered animation
                    
                row.innerHTML = `
                    <td>${vaccine.name}</td>
                    <td>${formatDate(vaccine.date)}</td>
                    <td>
                        <span class="badge rounded-pill ${vaccine.administered ? 'bg-success' : 'bg-warning text-dark'}">
                            ${vaccine.administered ? 'Yes' : 'No'}
                        </span>
                    </td>
                    <td>${vaccine.next_dose_date ? formatDate(vaccine.next_dose_date) : ''}</td>
                    <td class="text-end">
                        <div class="action-buttons d-flex justify-content-end gap-1">
                            <button class="btn btn-sm btn-outline-primary rounded-pill btn-edit-vaccine" 
                                    aria-label="Edit vaccine ${vaccine.name}">
                                <i class="fas fa-edit me-1" aria-hidden="true"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger rounded-pill btn-delete-vaccine" 
                                    aria-label="Delete vaccine ${vaccine.name}">
                                <i class="fas fa-trash-alt me-1" aria-hidden="true"></i> Delete
                            </button>
                        </div>
                    </td>
                `;
                    
                    vaccineListDesktop.appendChild(row);
                    
                    // Add event listener for row click
                    row.addEventListener('click', function(e) {
                        // Only proceed if not clicking on the buttons
                        if (!e.target.closest('button')) {
                            showVaccineDetails(vaccine);
                        }
                    });
                    
                    // Add event listeners for edit and delete buttons
                    const editBtn = row.querySelector('.btn-edit-vaccine');
                    const deleteBtn = row.querySelector('.btn-delete-vaccine');
                    
                    if (editBtn) {
                        editBtn.addEventListener('click', function(e) {
                            e.stopPropagation(); // Prevent row click
                            showVaccineDetails(vaccine);
                        });
                    }
                    
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', function(e) {
                            e.stopPropagation(); // Prevent row click
                            currentVaccine = vaccine;
                            const deleteModal = new bootstrap.Modal(document.getElementById('deleteVaccineModal'));
                            deleteModal.show();
                        });
                    }
                });
            }
        }
        
        // Mobile view
        if (vaccineListMobile) {
            if (vaccines.length === 0) {
                const emptyState = `
                    <div class="empty-container mt-3 mb-5">
                        <div class="empty-card">
                            <div class="empty-icon-wrapper">
                                <i class="fa-solid fa-syringe empty-icon" aria-hidden="true"></i>
                            </div>
                            <div class="empty-content">
                                <h2 class="empty-title">No Vaccines Registered</h2>
                                <p class="empty-message">Start recording your child's vaccines to keep track of their immunization history.</p>
                                
                                <button id="btn-add-first-vaccine-mobile" class="empty-button">
                                    <i class="fa-solid fa-plus me-2" aria-hidden="true"></i> Add First Vaccine
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                vaccineListMobile.innerHTML = emptyState;
                
                // Add event listener for the new button
                const newAddBtn = document.getElementById('btn-add-first-vaccine-mobile');
                if (newAddBtn) {
                    newAddBtn.addEventListener('click', function() {
                        resetVaccineForm();
                        scrollToForm();
                    });
                }
            } else {
                vaccineListMobile.innerHTML = '';
                
                // Add each vaccine as a card
                vaccines.forEach((vaccine, index) => {
                    const card = document.createElement('div');
                    card.className = 'card vaccine-card border-0 shadow-sm rounded-3 mb-3 animate-entry';
                    card.dataset.vaccineId = vaccine.id;
                    
                    card.innerHTML = `
                        <div class="card-body">
                            <h3 class="card-title h5 d-flex align-items-center">
                                <div class="event-type-indicator me-2" style="background-color: ${vaccine.administered ? '#34A853' : '#FBBC05'};"></div>
                                ${vaccine.name}
                            </h3>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge rounded-pill ${vaccine.administered ? 'bg-success' : 'bg-warning text-dark'}">
                                    ${vaccine.administered ? 'Administered' : 'Pending'}
                                </span>
                                <small class="text-muted d-flex align-items-center">
                                    <i class="fa-solid fa-calendar-day me-1" aria-hidden="true"></i>
                                    ${formatDate(vaccine.date)}
                                </small>
                            </div>
                            ${vaccine.next_dose_date ? `
                            <p class="card-text small mb-2 d-flex align-items-center">
                                <i class="fa-solid fa-calendar-plus me-1 text-primary" aria-hidden="true"></i>
                                <strong>Next dose:</strong> <span class="ms-1">${formatDate(vaccine.next_dose_date)}</span>
                            </p>
                            ` : ''}
                            <div class="d-flex justify-content-end mt-3 gap-2 w-100">
                                <button class="btn btn-sm btn-outline-primary rounded-pill btn-edit-vaccine" 
                                        aria-label="Edit vaccine ${vaccine.name}">
                                    <i class="fas fa-edit me-1" aria-hidden="true"></i> Edit
                                </button>
                                <button class="btn btn-sm btn-outline-danger rounded-pill btn-delete-vaccine" 
                                        aria-label="Delete vaccine ${vaccine.name}">
                                    <i class="fas fa-trash-alt me-1" aria-hidden="true"></i> Delete
                                </button>
                            </div>
                        </div>
                    `;
                    
                    vaccineListMobile.appendChild(card);
                    
                    // Add click event to show vaccine details
                    card.addEventListener('click', function(e) {
                        // Prevent click if the user clicked a button
                        if (e.target.closest('button')) return;
                        
                        vaccineCardService.getVaccine(vaccine.id)
                            .then(vaccineDetails => {
                                showVaccineDetails(vaccineDetails);
                            })
                            .catch(error => {
                                console.error('Error fetching vaccine details:', error);
                            });
                    });
                    
                    // Add click events for edit and delete buttons
                    const editBtn = card.querySelector('.btn-edit-vaccine');
                    if (editBtn) {
                        editBtn.addEventListener('click', function() {
                            vaccineCardService.getVaccine(vaccine.id)
                                .then(vaccineDetails => {
                                    showVaccineDetails(vaccineDetails);
                                })
                                .catch(error => {
                                    console.error('Error fetching vaccine details:', error);
                                });
                        });
                    }
                    
                    const deleteBtn = card.querySelector('.btn-delete-vaccine');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', function() {
                            vaccineCardService.getVaccine(vaccine.id)
                                .then(vaccineDetails => {
                                    currentVaccine = vaccineDetails;
                                    const deleteModal = new bootstrap.Modal(document.getElementById('deleteVaccineModal'));
                                    deleteModal.show();
                                })
                                .catch(error => {
                                    console.error('Error fetching vaccine details:', error);
                                });
                        });
                    }
                });
            }
        }
    }
    
    // Filter vaccines
    function filterVaccines(filterType) {
        const vaccineRows = document.querySelectorAll('.vaccine-row');
        const vaccineCards = document.querySelectorAll('.vaccine-card');
        
        // First, show all
        vaccineRows.forEach(row => row.style.display = '');
        vaccineCards.forEach(card => card.style.display = '');
        
        // Always remove any existing empty state messages for all filter types
        const emptyMessagesDesktop = vaccineListDesktop?.querySelector('.empty-filter-message');
        if (emptyMessagesDesktop) {
            emptyMessagesDesktop.remove();
        }
        
        const emptyMessagesMobile = vaccineListMobile?.querySelector('.empty-filter-message');
        if (emptyMessagesMobile) {
            emptyMessagesMobile.remove();
        }
        
        // Apply filtering logic for administered or pending
        if (filterType === 'administered' || filterType === 'pending') {
            // Filter desktop view
            vaccineRows.forEach(row => {
                const vaccineSpan = row.querySelector('.badge');
                const isAdministered = vaccineSpan?.classList.contains('bg-success');
                
                if ((filterType === 'administered' && !isAdministered) || 
                    (filterType === 'pending' && isAdministered)) {
                    row.style.display = 'none';
                }
            });
            
            // Filter mobile view
            vaccineCards.forEach(card => {
                const vaccineSpan = card.querySelector('.badge');
                const isAdministered = vaccineSpan?.classList.contains('bg-success');
                
                if ((filterType === 'administered' && !isAdministered) || 
                    (filterType === 'pending' && isAdministered)) {
                    card.style.display = 'none';
                }
            });
        }
    }
    
    // Check if we need to show empty state after filtering or searching
    function checkEmptyState() {
        const visibleRows = document.querySelectorAll('.vaccine-row[style=""]').length;
        const visibleCards = document.querySelectorAll('.vaccine-card[style=""]').length;
        
        // Desktop view
        if (vaccineListDesktop && visibleRows === 0) {
            // Check if there's already an empty message
            if (!vaccineListDesktop.querySelector('.empty-filter-message')) {
                const emptyRow = document.createElement('tr');
                emptyRow.className = 'empty-filter-message';
                emptyRow.innerHTML = `
                    <td colspan="5" class="text-center py-4">
                        <div class="empty-state" style="padding: 2rem 1rem;">
                            <i class="fa-solid fa-filter fa-2x mb-3 text-secondary" aria-hidden="true"></i>
                            <h3 class="h5 mb-2">No matching vaccines found</h3>
                            <p class="text-muted">Try a different filter or add a new vaccine</p>
                        </div>
                    </td>
                `;
                vaccineListDesktop.appendChild(emptyRow);
            }
        } else if (vaccineListDesktop) {
            // Remove any empty message
            const emptyMessage = vaccineListDesktop.querySelector('.empty-filter-message');
            if (emptyMessage) {
                emptyMessage.remove();
            }
        }
        
        // Mobile view
        if (vaccineListMobile && visibleCards === 0) {
            // Check if there's already an empty message
            if (!vaccineListMobile.querySelector('.empty-filter-message')) {
                const emptyDiv = document.createElement('div');
                emptyDiv.className = 'empty-filter-message text-center py-4';
                emptyDiv.innerHTML = `
                    <div class="empty-state" style="padding: 2rem 1rem;">
                        <i class="fa-solid fa-filter fa-2x mb-3 text-secondary" aria-hidden="true"></i>
                        <h3 class="h5 mb-2">No matching vaccines found</h3>
                        <p class="text-muted">Try a different filter or add a new vaccine</p>
                    </div>
                `;
                vaccineListMobile.appendChild(emptyDiv);
            }
        } else if (vaccineListMobile) {
            // Remove any empty message
            const emptyMessage = vaccineListMobile.querySelector('.empty-filter-message');
            if (emptyMessage) {
                emptyMessage.remove();
            }
        }
    }
    
    // Search vaccines
    function searchVaccines(searchTerm) {
        const vaccineRows = document.querySelectorAll('.vaccine-row');
        const vaccineCards = document.querySelectorAll('.vaccine-card');
        
        // Reset display
        vaccineRows.forEach(row => row.style.display = '');
        vaccineCards.forEach(card => card.style.display = '');
        
        if (searchTerm.length > 0) {
            // Search in rows
            vaccineRows.forEach(row => {
                const vaccineName = row.querySelector('td:first-child').textContent.toLowerCase();
                if (!vaccineName.includes(searchTerm)) {
                    row.style.display = 'none';
                }
            });
            
            // Search in cards
            vaccineCards.forEach(card => {
                const vaccineName = card.querySelector('.card-title').textContent.toLowerCase();
                if (!vaccineName.includes(searchTerm)) {
                    card.style.display = 'none';
                }
            });
        }
        
        // Check if we need to show empty state after searching
        checkEmptyState();
    }
    
    // Show vaccine details in the form
    function showVaccineDetails(vaccine) {
        currentVaccine = vaccine;
        
        // Update form elements
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.innerHTML = '<i class="fa-solid fa-edit text-primary me-2" aria-hidden="true"></i> Edit Vaccine';
        }
        
        const vaccineIdInput = document.getElementById('vaccine-id');
        if (vaccineIdInput) {
            vaccineIdInput.value = vaccine.id;
        }
        
        const vaccineNameInput = document.getElementById('vaccine-name');
        if (vaccineNameInput) {
            vaccineNameInput.value = vaccine.name;
        }
        
        const vaccineDateInput = document.getElementById('vaccine-date');
        if (vaccineDateInput) {
            vaccineDateInput.value = formatDateForInput(vaccine.date);
        }
        
        const vaccineAdministeredCheckbox = document.getElementById('vaccine-administered');
        if (vaccineAdministeredCheckbox) {
            vaccineAdministeredCheckbox.checked = vaccine.administered;
        }
        
        const vaccineNextDoseInput = document.getElementById('vaccine-next-dose');
        if (vaccineNextDoseInput) {
            vaccineNextDoseInput.value = vaccine.next_dose_date ? formatDateForInput(vaccine.next_dose_date) : '';
        }
        
        const vaccineNotesInput = document.getElementById('vaccine-notes');
        if (vaccineNotesInput) {
            vaccineNotesInput.value = vaccine.notes || '';
        }
        
        // Show delete and cancel buttons
        const deleteBtn = document.getElementById('btn-delete');
        const cancelBtn = document.getElementById('btn-cancel');
        const saveBtn = document.getElementById('btn-save');
        
        if (deleteBtn) {
            deleteBtn.style.display = 'block';
        }
        
        if (cancelBtn) {
            cancelBtn.style.display = 'block';
        }
        
        if (saveBtn) {
            saveBtn.innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Update Vaccine';
        }
        
        // Scroll to the form
        scrollToForm();
    }
    
    // Reset vaccine form
    function resetVaccineForm() {
        currentVaccine = null;
        
        // Reset form inputs
        const vaccineForm = document.getElementById('vaccine-form');
        if (vaccineForm) {
            vaccineForm.reset();
        }
        
        const vaccineIdInput = document.getElementById('vaccine-id');
        if (vaccineIdInput) {
            vaccineIdInput.value = '';
        }
        
        // Hide delete and cancel buttons
        const deleteBtn = document.getElementById('btn-delete');
        const cancelBtn = document.getElementById('btn-cancel');
        
        if (deleteBtn) {
            deleteBtn.style.display = 'none';
        }
        
        if (cancelBtn) {
            cancelBtn.style.display = 'none';
        }
        
        // Reset form title and button text
        const formTitle = document.getElementById('form-title');
        const saveBtn = document.getElementById('btn-save');
        
        if (formTitle) {
            formTitle.innerHTML = '<i class="fa-solid fa-plus text-primary me-2" aria-hidden="true"></i> Add Vaccine';
        }
        
        if (saveBtn) {
            saveBtn.innerHTML = '<i class="fa-solid fa-check me-1" aria-hidden="true"></i> Save Vaccine';
        }
    }
    
    // Save vaccine
    function saveVaccine() {
        const vaccineNameInput = document.getElementById('vaccine-name');
        const vaccineDateInput = document.getElementById('vaccine-date');
        const vaccineAdministeredCheckbox = document.getElementById('vaccine-administered');
        const vaccineNextDoseInput = document.getElementById('vaccine-next-dose');
        const vaccineNotesInput = document.getElementById('vaccine-notes');
        
        if (!vaccineNameInput || !vaccineDateInput) {
            showNotification('Missing required form elements', 'danger');
            return Promise.resolve();
        }
        
        const vaccineData = {
            name: vaccineNameInput.value,
            date: vaccineDateInput.value,
            administered: vaccineAdministeredCheckbox?.checked || false,
            next_dose_date: vaccineNextDoseInput?.value || null,
            notes: vaccineNotesInput?.value || '',
            vaccine_card: vaccineCardId
        };
        
        console.log('Saving vaccine:', vaccineData);
        
        // Determine if this is a new vaccine or an update
        const isNewVaccine = !currentVaccine;
        
        if (isNewVaccine) {
            return vaccineCardService.addVaccine(vaccineCardId, vaccineData)
                .then(savedVaccine => {
                    console.log('Vaccine saved successfully:', savedVaccine);
                    
                    // Reload vaccines to show the new one
                    loadVaccines();
                    
                    // Update stats
                    updateVaccineStats();
                    updateUpcomingVaccines();
                    
                    // Reset form
                    resetVaccineForm();
                    
                    // Show success notification
                    showNotification('Vaccine created successfully', 'success');
                })
                .catch(error => {
                    console.error('Error saving vaccine:', error);
                    // Check if there's a response with error details
                    if (error.response) {
                        console.error('Server error details:', error.response);
                    }
                    showNotification('Error creating vaccine. Please try again.', 'danger');
                    throw error;
                });
        } else {
            const vaccineId = currentVaccine.id;
            
            return vaccineCardService.updateVaccine(vaccineId, vaccineData)
                .then(updatedVaccine => {
                    console.log('Vaccine updated successfully:', updatedVaccine);
                    
                    // Reload vaccines
                    loadVaccines();
                    
                    // Update stats
                    updateVaccineStats();
                    updateUpcomingVaccines();
                    
                    // Reset form
                    resetVaccineForm();
                    
                    // Show success notification
                    showNotification('Vaccine updated successfully', 'success');
                })
                .catch(error => {
                    console.error('Error updating vaccine:', error);
                    // Check if there's a response with error details
                    if (error.response) {
                        console.error('Server error details:', error.response);
                    }
                    showNotification('Error updating vaccine. Please try again.', 'danger');
                    throw error;
                });
        }
    }
    
    // Delete vaccine
    function deleteVaccine() {
        if (!currentVaccine) return;
        
        vaccineCardService.deleteVaccine(currentVaccine.id)
            .then(response => {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteVaccineModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Reload vaccines
                loadVaccines();
                
                // Update stats
                updateVaccineStats();
                updateUpcomingVaccines();
                
                // Reset form if the deleted vaccine is currently being edited
                if (currentVaccine && document.getElementById('vaccine-id').value === currentVaccine.id) {
                    resetVaccineForm();
                }
                
                // Show success notification
                showNotification('Vaccine deleted successfully', 'success');
            })
            .catch(error => {
                console.error('Error deleting vaccine:', error);
                showNotification('Error deleting vaccine. Please try again.', 'danger');
            });
    }
    
    // Update vaccine statistics
    function updateVaccineStats() {
        vaccineCardService.getVaccineStats(vaccineCardId)
            .then(data => {
                updateStatsUI(data);
            })
            .catch(error => {
                console.error('Error fetching vaccine stats:', error);
                // Use default values on error
                updateStatsUI({
                    total: 0,
                    administered: 0,
                    pending: 0,
                    upcoming: 0
                });
            });
    }
    
    // Update the stats UI
    function updateStatsUI(data) {
        const statsContainer = document.getElementById('vaccine-stats');
        if (!statsContainer) return;
        
        const stats = statsContainer.querySelectorAll('.vaccine-stat');
        if (stats.length < 4) return;
        
        // Update total vaccines
        const totalCountEl = stats[0].querySelector('.vaccine-stat-count');
        if (totalCountEl) {
            totalCountEl.textContent = data.total || 0;
        }
        
        // Update administered vaccines
        const administeredCountEl = stats[1].querySelector('.vaccine-stat-count');
        if (administeredCountEl) {
            administeredCountEl.textContent = data.administered || 0;
        }
        
        // Update pending vaccines
        const pendingCountEl = stats[2].querySelector('.vaccine-stat-count');
        if (pendingCountEl) {
            pendingCountEl.textContent = data.pending || 0;
        }
        
        // Update upcoming vaccines
        const upcomingCountEl = stats[3].querySelector('.vaccine-stat-count');
        if (upcomingCountEl) {
            upcomingCountEl.textContent = data.upcoming || 0;
        }
        
        // Also update the badge in the upcoming vaccines section
        const upcomingBadge = document.querySelector('.card-header .badge[aria-label*="Number of upcoming vaccines"]');
        if (upcomingBadge) {
            upcomingBadge.textContent = data.upcoming || 0;
        }
    }
    
    // Update upcoming vaccines
    function updateUpcomingVaccines() {
        vaccineCardService.getUpcomingVaccines(vaccineCardId)
            .then(data => {
                updateUpcomingVaccinesUI(data);
            })
            .catch(error => {
                console.error('Error fetching upcoming vaccines:', error);
                // Use empty data on error
                updateUpcomingVaccinesUI({ vaccines: [] });
            });
    }
    
    // Update the upcoming vaccines UI
    function updateUpcomingVaccinesUI(data) {
        if (!upcomingVaccinesList) return;
        
        // Clear existing items
        upcomingVaccinesList.innerHTML = '';
        
        if (data.vaccines && data.vaccines.length > 0) {
            data.vaccines.forEach(vaccine => {
                const li = document.createElement('li');
                li.className = 'list-group-item upcoming-vaccine-item d-flex justify-content-between align-items-start';
                li.dataset.vaccineId = vaccine.id;
                li.tabIndex = 0;
                li.role = 'button';
                li.setAttribute('aria-label', `Upcoming vaccine: ${vaccine.name} on ${formatDate(vaccine.next_dose_date)}`);
                
                li.innerHTML = `
                    <div>
                        <h4 class="h6 mb-1">${vaccine.name}</h4>
                        <p class="small text-muted mb-0 d-flex align-items-center">
                            <i class="fa-solid fa-calendar-day me-1" aria-hidden="true"></i>
                            ${formatDate(vaccine.next_dose_date)}
                        </p>
                        ${vaccine.notes ? `
                        <p class="small text-muted mb-0 mt-1">
                            ${vaccine.notes.length > 50 ? vaccine.notes.substring(0, 50) + '...' : vaccine.notes}
                        </p>
                        ` : ''}
                    </div>
                    <span class="badge ${vaccine.administered ? 'bg-success' : 'bg-warning text-dark'}">
                        ${vaccine.administered ? 'Administered' : 'Pending'}
                    </span>
                `;
                
                upcomingVaccinesList.appendChild(li);
                
                // Add click event to show vaccine details
                li.addEventListener('click', function() {
                    // Fetch the complete vaccine data and show details
                    vaccineCardService.getVaccine(vaccine.id)
                        .then(vaccineData => {
                            showVaccineDetails(vaccineData);
                        })
                        .catch(error => {
                            console.error('Error fetching vaccine details:', error);
                            showNotification('Error loading vaccine details', 'danger');
                        });
                });
            });
        } else {
            // Show "no upcoming vaccines" message
            const li = document.createElement('li');
            li.className = 'list-group-item text-center py-3';
            li.id = 'no-upcoming-vaccines';
            li.innerHTML = '<p class="text-muted mb-0">No upcoming vaccines</p>';
            upcomingVaccinesList.appendChild(li);
        }
    }
    
    // Helper function to scroll to the form
    function scrollToForm() {
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Show notification
    function showNotification(message, type) {
        if (!notificationEl) return;
        
        notificationEl.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3 shadow-sm rounded-3`;
        notificationEl.innerHTML = message;
        notificationEl.style.display = 'block';
        notificationEl.style.opacity = '0';
        
        // Fade in
        setTimeout(() => {
            notificationEl.style.transition = 'opacity 0.3s ease-in-out';
            notificationEl.style.opacity = '1';
        }, 10);
        
        // Fade out and hide after 3 seconds
        setTimeout(() => {
            notificationEl.style.opacity = '0';
            setTimeout(() => {
                notificationEl.style.display = 'none';
            }, 300);
        }, 3000);
    }
    
    // Utility functions
    function formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString(document.documentElement.lang || 'en', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
    }
    
    function formatDateForInput(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toISOString().split('T')[0];
    }
});