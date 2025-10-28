// ============================================
// LOGIN.JS - Lógica específica de login
// ============================================

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    hideMessages();
    disableSubmitButton('submitBtn', 'Iniciando sesión...');

    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    // Agregar token de reCAPTCHA si está habilitado
    if (typeof grecaptcha !== 'undefined') {
        const recaptchaResponse = grecaptcha.getResponse();
        if (recaptchaResponse) {
            formData.recaptcha_token = recaptchaResponse;
        }
    }

    // Validaciones básicas
    if (!isValidEmail(formData.email)) {
        showError('Por favor ingresa un email válido');
        enableSubmitButton('submitBtn');
        return;
    }

    if (!isValidPassword(formData.password)) {
        showError('La contraseña debe tener al menos 6 caracteres');
        enableSubmitButton('submitBtn');
        return;
    }

    try {
        const data = await apiPost('/login', formData);

        if (data.success !== false) {
            showSuccess('Login exitoso! Redirigiendo...');
            redirectAfterDelay('/dashboard', 1000);
        } else {
            showError(data.message || 'Error al iniciar sesión');
            // Reset reCAPTCHA si falla
            if (typeof grecaptcha !== 'undefined') {
                grecaptcha.reset();
            }
            enableSubmitButton('submitBtn');
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        showError('Error de conexión. Intenta nuevamente.');
        // Reset reCAPTCHA si hay error
        if (typeof grecaptcha !== 'undefined') {
            grecaptcha.reset();
        }
        enableSubmitButton('submitBtn');
    }
});

// Auto-focus en email al cargar
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('email').focus();
});
