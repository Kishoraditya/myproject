// Main JavaScript file for Shoshin AI

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.md\\:hidden');
    const mobileMenu = document.createElement('div');
    mobileMenu.className = 'fixed inset-0 bg-white z-50 transform translate-x-full transition-transform duration-300 ease-in-out';
    mobileMenu.innerHTML = `
        <div class="flex justify-end p-6">
            <button class="mobile-close focus:outline-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
        <nav class="flex flex-col items-center gap-6 mt-8">
            <a href="/" class="text-xl font-medium hover:text-primary transition-colors">Home</a>
            <a href="/features" class="text-xl font-medium hover:text-primary transition-colors">Features</a>
            <a href="/pricing" class="text-xl font-medium hover:text-primary transition-colors">Pricing</a>
            <a href="/about" class="text-xl font-medium hover:text-primary transition-colors">About</a>
            <a href="#" class="mt-4 px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 transition-colors">
                Get Started
            </a>
        </nav>
    `;
    document.body.appendChild(mobileMenu);
    
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.remove('translate-x-full');
        });
        
        mobileMenu.querySelector('.mobile-close').addEventListener('click', function() {
            mobileMenu.classList.add('translate-x-full');
        });
    }
    
    // Animate elements when they come into view
    if ('IntersectionObserver' in window) {
        const animateItems = document.querySelectorAll('.animate-on-scroll');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animateItems.forEach(item => {
            observer.observe(item);
        });
    }
    
    // Handle newsletter form submission
    const newsletterForm = document.querySelector('form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            if (!emailInput || !emailInput.value) return;
            
            // Simple email validation
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(emailInput.value)) {
                showMessage('Please enter a valid email address', 'error');
                return;
            }
            
            // In a real implementation, you would send this to your backend
            // For demo purposes, we'll just show a success message
            showMessage('Thank you for subscribing to our newsletter!', 'success');
            emailInput.value = '';
        });
    }
    
    // Function to show messages
    function showMessage(message, type = 'success') {
        const messageContainer = document.createElement('div');
        messageContainer.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} animate-fade-in`;
        messageContainer.innerText = message;
        document.body.appendChild(messageContainer);
        
        setTimeout(() => {
            messageContainer.style.opacity = '0';
            messageContainer.style.transition = 'opacity 0.5s ease-in-out';
            setTimeout(() => {
                document.body.removeChild(messageContainer);
            }, 500);
        }, 3000);
    }
    
    // Add accessibility features
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-to-content';
    skipLink.innerText = 'Skip to content';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ID to main content area for skip link
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.id = 'main-content';
    }
});
