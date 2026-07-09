export const API_BASE_URL = '';

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    // Only set Content-Type if it's not FormData
    if (!(options.body instanceof URLSearchParams) && !(options.body instanceof FormData)) {
        if (!headers.has('Content-Type')) {
            headers.set('Content-Type', 'application/json');
        }
    }

    const config: RequestInit = {
        ...options,
        headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errorMessage = 'An error occurred';
        if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((e: any) => e.msg).join(', ');
        }
        throw new Error(errorMessage);
    }
    
    return response.json();
}
