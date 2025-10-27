// ============================================
// FUNCIONES COMPARTIDAS PARA AUTH
// ============================================

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    // Intentar con diferentes IDs (para compatibilidad con diferentes páginas)
    const errorDiv = document.getElementById('error') || 
                     document.getElementById('alertError');
    
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Auto-hide después de 5 segundos
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

/**
 * Muestra un mensaje de éxito
 */
function showSuccess(message) {
    // Intentar con diferentes IDs (para compatibilidad con diferentes páginas)
    const successDiv = document.getElementById('success') || 
                       document.getElementById('alertSuccess');
    
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }
}

/**
 * Oculta todos los mensajes
 */
function hideMessages() {
    const errorDiv = document.getElementById('error') || 
                     document.getElementById('alertError');
    const successDiv = document.getElementById('success') || 
                       document.getElementById('alertSuccess');
    
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
}

/**
 * Deshabilita el botón de submit y muestra loading
 */
function disableSubmitButton(buttonId = 'submitBtn', loadingText = 'Procesando...') {
    const submitBtn = document.getElementById(buttonId);
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.innerHTML = loadingText + ' <span class="spinner"></span>';
    }
}

/**
 * Habilita el botón de submit
 */
function enableSubmitButton(buttonId = 'submitBtn') {
    const submitBtn = document.getElementById(buttonId);
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = submitBtn.dataset.originalText || 'Enviar';
    }
}

/**
 * Valida email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Valida contraseña (mínimo 6 caracteres)
 */
function isValidPassword(password) {
    return password && password.length >= 6;
}

/**
 * Calcula la fortaleza de la contraseña
 * @returns {string} 'weak', 'medium', 'strong'
 */
function getPasswordStrength(password) {
    if (!password) return 'weak';
    
    let strength = 0;
    
    // Longitud
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Mayúsculas
    if (/[A-Z]/.test(password)) strength++;
    
    // Minúsculas
    if (/[a-z]/.test(password)) strength++;
    
    // Números
    if (/[0-9]/.test(password)) strength++;
    
    // Caracteres especiales
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    if (strength <= 2) return 'weak';
    if (strength <= 4) return 'medium';
    return 'strong';
}

/**
 * Muestra indicador de fortaleza de contraseña
 */
function showPasswordStrength(password, strengthBarId = 'passwordStrengthBar') {
    const strengthBar = document.getElementById(strengthBarId);
    if (!strengthBar) return;
    
    const strengthContainer = strengthBar.parentElement;
    
    if (!password || password.length === 0) {
        // Ocultar indicador si no hay contraseña
        if (strengthContainer) {
            strengthContainer.classList.remove('active');
        }
        return;
    }
    
    // Mostrar indicador
    if (strengthContainer) {
        strengthContainer.classList.add('active');
    }
    
    const strength = getPasswordStrength(password);
    
    // Remover clases anteriores
    strengthBar.className = 'password-strength-bar';
    
    // Agregar clase según fortaleza
    if (strength === 'weak') {
        strengthBar.classList.add('password-strength-weak');
    } else if (strength === 'medium') {
        strengthBar.classList.add('password-strength-medium');
    } else {
        strengthBar.classList.add('password-strength-strong');
    }
}

/**
 * Realiza una petición POST a la API
 */
async function apiPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    
    return response.json();
}

/**
 * Redirige después de un delay
 */
function redirectAfterDelay(url, delay = 1500) {
    setTimeout(() => {
        window.location.href = url;
    }, delay);
}

/**
 * Sanitiza input para prevenir XSS
 */
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}
