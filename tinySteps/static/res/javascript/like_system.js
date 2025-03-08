// Add this to a new file: tinySteps/static/js/like_system.js
function setupLikeButtons() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('data-url');
            const countElement = document.getElementById(this.getAttribute('data-count-id'));
            const iconElement = this.querySelector('i');
            
            fetch(url, {
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
                    countElement.textContent = data.likes_count;
                    
                    if (data.liked) {
                        iconElement.classList.remove('far');
                        iconElement.classList.add('fas');
                        iconElement.classList.add('text-danger');
                    } else {
                        iconElement.classList.remove('fas');
                        iconElement.classList.remove('text-danger');
                        iconElement.classList.add('far');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

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

document.addEventListener('DOMContentLoaded', setupLikeButtons);