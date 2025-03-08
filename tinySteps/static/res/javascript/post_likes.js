document.addEventListener('DOMContentLoaded', function() {
    // Find all like buttons
    const likeButtons = document.querySelectorAll('.like-button');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const contentTypeId = this.dataset.contentType;
            const objectId = this.dataset.objectId;
            
            fetch(`/like/${contentTypeId}/${objectId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update like count
                    const countElement = this.querySelector('.like-count');
                    countElement.textContent = data.likes_count;
                    
                    // Update like button appearance
                    if (data.liked) {
                        this.classList.add('liked');
                    } else {
                        this.classList.remove('liked');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
    
    // Function to get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});