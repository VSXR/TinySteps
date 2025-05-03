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
    
    // Animated counters
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const plusSign = counter.textContent.includes('+');
        
        // Set initial text content
        if (target >= 1000) {
            counter.textContent = '0K' + (plusSign ? '+' : '');
        } else {
            counter.textContent = '0' + (plusSign ? '+' : '');
        }
        
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const updateCounter = () => {
                        const counterValue = parseInt(counter.textContent.replace(/\D/g, '')) || 0;
                        const increment = target / 20; // Speed of counting
                        
                        if (counterValue < target) {
                            if (target >= 1000) {
                                counter.textContent = Math.ceil(Math.min(counterValue + increment, target) / 1000) + 'K' + (plusSign ? '+' : '');
                            } else {
                                counter.textContent = Math.ceil(Math.min(counterValue + increment, target)) + (plusSign ? '+' : '');
                            }
                            setTimeout(updateCounter, 50);
                        } else {
                            if (target >= 1000) {
                                counter.textContent = (target / 1000) + 'K' + (plusSign ? '+' : '');
                            } else {
                                counter.textContent = target + (plusSign ? '+' : '');
                            }
                        }
                    };
                    
                    updateCounter();
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counterObserver.observe(counter);
    });
});