document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality with improved handling
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleInitial = document.getElementById('theme-toggle-initial');
    const html = document.documentElement;

    // Get the current theme from localStorage or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Set initial states
    themeToggleInitial.checked = currentTheme === 'dark';
    themeToggle.checked = currentTheme === 'dark';

    // Make the main toggle visible once we've set its state
    requestAnimationFrame(() => {
        themeToggle.style.opacity = '1';
        themeToggleInitial.remove(); // Remove the initial toggle
    });

    // Update theme classes and attributes
    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        html.className = theme + '-theme';
        localStorage.setItem('theme', theme);
    }

    // Theme toggle handler with smoother transition
    themeToggle.addEventListener('change', function() {
        const newTheme = this.checked ? 'dark' : 'light';
        applyTheme(newTheme);
    });

    // Ensure theme is correctly applied on page load
    applyTheme(currentTheme);

    // CSRF token handling
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    console.log('CSRF Token:', csrfToken);

    document.querySelectorAll('form').forEach(form => {
        if (!form.querySelector('input[name="csrf_token"]')) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfToken;
            form.appendChild(input);
        }
    });

    // Add the CSRF token to all forms with the POST method
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        if (!form.querySelector('input[name="csrf_token"]')) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            console.log('CSRF token added to form:', form);
        }
    });

    // Flash message handling
    var alerts = document.getElementsByClassName('alert');
    Array.from(alerts).forEach(function(alert) {
        alert.style.display = 'block';
        alert.style.opacity = '1';

        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 500);
        }, 3000);
    });

    // Loader functionality
    const loaderOverlay = document.getElementById('loader-overlay');
    const mainContent = document.getElementById('main-content');
    let isNavigating = false;
    let loaderTimer = null;
    const MINIMUM_LOADER_DURATION = 1500; // Increased minimum time to 1.5 seconds

    function showLoader() {
        if (!isNavigating) {
            isNavigating = true;
            loaderTimer = Date.now();
            document.body.style.overflow = 'hidden';
            requestAnimationFrame(() => {
                loaderOverlay.style.display = 'flex';
                requestAnimationFrame(() => {
                    loaderOverlay.classList.add('show');
                });
            });
        }
    }

    function hideLoader() {
        const currentTime = Date.now();
        const elapsedTime = currentTime - (loaderTimer || currentTime);
        const remainingTime = Math.max(0, MINIMUM_LOADER_DURATION - elapsedTime);

        setTimeout(() => {
            loaderOverlay.classList.add('fade-out');
            setTimeout(() => {
                loaderOverlay.classList.remove('show', 'fade-out');
                loaderOverlay.style.display = 'none';
                document.body.style.overflow = '';
                isNavigating = false;
                loaderTimer = null;
            }, 300); // Match this with CSS transition duration
        }, remainingTime);
    }

    // Hide loader on initial page load with a slight delay
    setTimeout(hideLoader, 500);

    // Handle browser back/forward navigation
    window.addEventListener('popstate', () => {
        showLoader();
        window.location.reload();
    });

    // Handle clicks on links
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && !link.hasAttribute('download') && !link.hasAttribute('target') &&
            link.href && link.href.startsWith(window.location.origin)) {
            e.preventDefault();
            showLoader();
            setTimeout(() => {
                window.location.href = link.href;
            }, 100);
        }
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
        if (e.target.method === 'get') return; // Don't show loader for GET forms
        showLoader();
    });

    // Handle AJAX requests
    const originalFetch = window.fetch;
    window.fetch = function() {
        showLoader();
        const promise = originalFetch.apply(this, arguments);
        promise.finally(() => {
            if (!document.querySelector('form[data-no-loader]')) {
                hideLoader();
            }
        });
        return promise;
    };

    // Handle errors and make sure loader is hidden
    window.addEventListener('error', () => setTimeout(hideLoader, MINIMUM_LOADER_DURATION));
    window.addEventListener('unhandledrejection', () => setTimeout(hideLoader, MINIMUM_LOADER_DURATION));

    // Ensure loader is hidden if page has been in background
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && isNavigating) {
            hideLoader();
        }
    });

    // Function to update the loader background based on the theme
    function updateLoaderBackground() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        if (currentTheme === 'dark') {
            loaderOverlay.style.backgroundColor = 'var(--bg-primary)';
        } else {
            loaderOverlay.style.backgroundColor = 'var(--bg-primary)';
        }
    }

    // Update the loader background on page load
    updateLoaderBackground();

    // Listen for theme changes and update the loader background
    if (themeToggle) {
        themeToggle.addEventListener('change', updateLoaderBackground);
    }
});

async function handlePointsSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const points = form.points.value;
    const reason = form.reason.value;
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    // Disable the form and show a loading state
    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Updating...';

    try {
        const response = await fetch(`{{ url_for('parent.update_child_points', child_id=child.id) }}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ points: parseInt(points), reason }),
        });

        const data = await response.json();
        if (data.success) {
            // Reload the page to show updated points
            window.location.reload();
        } else {
            alert(data.error || 'Failed to update points');
        }
    } catch (error) {
        alert('Error updating points');
        console.error('Error:', error);
    } finally {
        // Re-enable the form and reset the button text
        submitButton.disabled = false;
        submitButton.textContent = 'Update Points';
    }
}

<meta name="csrf-token" content="YOUR_CSRF_TOKEN_HERE"></meta>
