document.addEventListener('DOMContentLoaded', function() {
    const postForm = document.querySelector('form[action*="add_post"]');    
    
    if (postForm) {
        postForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const titleInput = document.getElementById('id_title');
            const descInput = document.getElementById('id_desc');
            
            if (!titleInput.value.trim() || !descInput.value.trim()) {
                showError('Por favor, complete todos los campos obligatorios');
                return;
            }
            
            try {
                showLoading('Creando discusión...');
                const postData = {
                    title: titleInput.value.trim(),
                    content: descInput.value.trim()
                };
                
                const response = await api.createForumPost(postData);
                window.location.href = `/parents_forum/view/${response.id}`; // REDIRECT TO THE NEWLY CREATED POST
            } catch (error) {
                hideLoading();
                showError('Error al crear la discusión. Por favor, inténtelo de nuevo.');
                console.error('Error creating post:', error);
            }
        });
    }
    
    // Funciones de utilidad
    function showLoading(message) {
        let loadingEl = document.getElementById('loading-indicator');
        
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'loading-indicator';
            loadingEl.className = 'loading-overlay';
            loadingEl.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p id="loading-message">${escapeHtml(message)}</p>
            `;
            document.body.appendChild(loadingEl);
        } else {
            document.getElementById('loading-message').textContent = message;
            loadingEl.style.display = 'flex';
        }
    }
    
    function hideLoading() {
        const loadingEl = document.getElementById('loading-indicator');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }
    
    function showError(message) {
        showMessage(message, 'danger');
    }
    
    function showMessage(message, type) {
        let messagesContainer = document.querySelector('.messages');
        
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages mb-3';
            messagesContainer.setAttribute('role', 'alert');
            messagesContainer.setAttribute('aria-live', 'polite');
            
            const heading = document.querySelector('h1') || document.querySelector('h2');
            if (heading && heading.parentNode) {
                heading.parentNode.insertBefore(messagesContainer, heading.nextSibling);
            } else {
                const mainContent = document.querySelector('#main-content');
                if (mainContent) {
                    mainContent.prepend(messagesContainer);
                }
            }
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        messagesContainer.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 150);
            }
        }, 5000);
    }
    
    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});