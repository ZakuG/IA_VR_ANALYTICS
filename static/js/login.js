// ============================================
// LOGIN.JS - Lógica específica de login con detección adaptativa
// ============================================

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    hideMessages();
    disableSubmitButton('submitBtn', 'Iniciando sesión...');

    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

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

    // ✨ NUEVO: Verificación adaptativa de reCAPTCHA
    // Solo pide reCAPTCHA si detecta comportamiento sospechoso
    const needsCaptcha = await shouldRequireCaptcha();
    
    if (needsCaptcha) {
        // Mostrar widget de reCAPTCHA si estaba oculto
        showCaptchaWidget();
        
        // Verificar que el usuario haya resuelto el captcha
        if (typeof grecaptcha !== 'undefined') {
            const recaptchaResponse = grecaptcha.getResponse();
            if (!recaptchaResponse) {
                showError('Por favor, completa la verificación de seguridad');
                enableSubmitButton('submitBtn');
                return;
            }
            formData.recaptcha_token = recaptchaResponse;
        }
    } else {
        // Usuario legítimo detectado - ocultar captcha si estaba visible
        hideCaptchaWidget();
    }

    // Agregar datos de comportamiento para análisis backend
    if (typeof behaviorTracker !== 'undefined') {
        formData.behavior_data = behaviorTracker.getBehaviorData();
    }

    try {
        const data = await apiPost('/login', formData);

        if (data.success !== false) {
            showSuccess('Login exitoso! Redirigiendo...');
            redirectAfterDelay('/dashboard', 1000);
        } else {
            // Si falla, resetear reCAPTCHA y mostrarlo la próxima vez
            if (typeof grecaptcha !== 'undefined') {
                grecaptcha.reset();
                showCaptchaWidget(); // Mostrar captcha tras fallo
            }
            showError(data.message || 'Error al iniciar sesión');
            enableSubmitButton('submitBtn');
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        showError('Error de conexión. Intenta nuevamente.');
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
