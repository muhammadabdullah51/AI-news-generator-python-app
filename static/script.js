document.addEventListener('DOMContentLoaded', () => {
    // Universal error handler
    const handleApiError = (response) => {
        if (response.status === 401 || response.status === 403) {
            alert('Session expired. Please login again.');
            window.location.href = '/login';
            return true;
        }
        return false;
    };

    // Generic form handler
    const handleFormSubmit = (formId, endpoint, successCallback) => {
        const form = document.getElementById(formId);
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams(formData),
                    credentials: 'include'
                });
    
                // Handle non-JSON responses
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Invalid server response');
                }
    
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.message || 'Request failed');
                }
                
                successCallback(result);
            } catch (error) {
                alert(error.message);
                if (error.message.includes('Invalid server response')) {
                    window.location.href = '/login';
                }
            }
        });
    };

    // Login Handler
if (document.getElementById('loginForm')) {
    handleFormSubmit('loginForm', '/login', (result) => {
        if (result.success) {
            window.location.href = '/'; // Redirect on success
        } else {
            alert(result.message || 'Login failed');
        }
    });
}

    // Signup Handler
    if (document.getElementById('signupForm')) {
        handleFormSubmit('signupForm', '/signup', () => {
            alert('Signup successful! Please login.');
            window.location.href = '/login';
        });
    }

    // News Generation Handler
    if (document.getElementById('newsForm')) {
        const newsForm = document.getElementById('newsForm');
        const newsResult = document.getElementById('newsResult');
        
        newsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = document.getElementById('prompt').value;
            
            try {
                const response = await fetch('/generate-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ prompt }),
                    credentials: 'include' // Required for cookies
                });

                if (handleApiError(response)) return;

                const result = await response.json();
                
                if (response.status === 403) {
                    alert('Limit reached! Please login again.');
                    window.location.href = '/login';
                    return;
                }

                newsResult.textContent = result.news;
            } catch (error) {
                alert(error.message);
            }
        });
    }

    // Auto-redirect if not logged in
    (async () => {
        if (window.location.pathname === '/') {
            try {
                await fetch('/check-auth', {
                    credentials: 'include'
                });
            } catch (error) {
                window.location.href = '/login';
            }
        }
    })();
});