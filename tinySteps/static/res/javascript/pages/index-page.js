document.addEventListener('DOMContentLoaded', function() {
    const revealSections = document.querySelectorAll('.reveal-section');
    
    const revealOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const revealObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const section = entry.target;
                const items = section.querySelectorAll('.reveal-item');
                
                items.forEach((item, index) => {
                    const delay = item.getAttribute('data-delay') || index * 100;
                    setTimeout(() => {
                        if (item.classList.contains('fade-up')) {
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        } else if (item.classList.contains('fade-left')) {
                            item.style.opacity = '1';
                            item.style.transform = 'translateX(0)';
                        } else if (item.classList.contains('fade-right')) {
                            item.style.opacity = '1';
                            item.style.transform = 'translateX(0)';
                        }
                    }, delay);
                });
                
                observer.unobserve(section);
            }
        });
    }, revealOptions);
    
    revealSections.forEach(section => {
        const items = section.querySelectorAll('.reveal-item');
        
        items.forEach(item => {
            if (item.classList.contains('fade-up')) {
                item.style.opacity = '0';
                item.style.transform = 'translateY(30px)';
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            } else if (item.classList.contains('fade-left')) {
                item.style.opacity = '0';
                item.style.transform = 'translateX(30px)';
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            } else if (item.classList.contains('fade-right')) {
                item.style.opacity = '0';
                item.style.transform = 'translateX(-30px)';
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            }
        });
        
        revealObserver.observe(section);
    });
});