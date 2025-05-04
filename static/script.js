document.addEventListener('DOMContentLoaded', () => {
    const handleFormSubmit = async (formId, endpoint, successCallback) => {
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
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    let errorMessage = 'Something went wrong';
                    try {
                        const result = await response.json();
                        errorMessage = result.message || errorMessage;
                    } catch(e) {/* Ignore JSON parse errors */}
                    
                    if (response.status === 401) {
                        alert('Please login first');
                        localStorage.removeItem('access_token');
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error(errorMessage);
                }
                
                successCallback(result);
            } catch (error) {
                alert(error.message);
            }
        });
    };

    // Handle login
    if (document.getElementById('loginForm')) {
        handleFormSubmit('loginForm', '/login', (result) => {
            localStorage.setItem('access_token', result.access_token);
            window.location.href = '/';
        });
    }

    // Handle signup
    if (document.getElementById('signupForm')) {
        handleFormSubmit('signupForm', '/signup', () => {
            alert('Signup successful! Please login.');
            window.location.href = '/login';
        });
    }

    // Handle news generation
    if (document.getElementById('newsForm')) {
        const newsForm = document.getElementById('newsForm');
        const newsResult = document.getElementById('newsResult');
        
        newsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = document.getElementById('prompt').value;
            const token = localStorage.getItem('access_token');
            
            try {
                const response = await fetch('/generate-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Authorization': `Bearer ${token}`
                    },
                    body: new URLSearchParams({ prompt }),
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    let errorMessage = 'Please login again to continue..';
                    try {
                        const result = await response.json();
                        errorMessage = result.message || errorMessage ;
                        
                    } catch(e) {/* Ignore JSON parse errors */}
                    
                    if (response.status === 401) {
                        alert('Please login first');
                        localStorage.removeItem('access_token');
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error(errorMessage);
                }
                
                newsResult.textContent = result.news;
            } catch (error) {
                alert(error.message);
                if (error.message.includes('re-authenticate')) {
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                }
            }
        });
    }
});