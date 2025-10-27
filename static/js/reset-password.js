// reset-password.js - Lógica para resetear contraseña

// Obtener token de la URL (está en el path: /reset-password/{token})
const token = window.location.pathname.split('/').pop();

if (!token || token === 'reset-password') {
    showError('Token de recuperación inválido o faltante');
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        disableSubmitButton('submitBtn', 'Token Inválido');
    }
}

document.getElementById('resetPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    disableSubmitButton('submitBtn', 'Actualizando...');

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validaciones
    if (!isValidPassword(password)) {
        showError('La contraseña debe tener al menos 6 caracteres');
        enableSubmitButton('submitBtn');
        return;
    }

    if (password !== confirmPassword) {
        showError('Las contraseñas no coinciden');
        enableSubmitButton('submitBtn');
        return;
    }

    try {
        // El endpoint espera el token en la URL y password + confirm_password en el body
        const response = await fetch(`/reset-password/${token}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                password: password,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            showSuccess('Contraseña actualizada exitosamente. Redirigiendo al login...');
            document.getElementById('resetPasswordForm').reset();
            redirectAfterDelay('/login', 2000);
        } else {
            // Mostrar mensaje de error específico del servidor
            showError(data.message || 'Error al actualizar la contraseña');
            enableSubmitButton('submitBtn');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión. Por favor intenta nuevamente.');
        enableSubmitButton('submitBtn');
    }
});

// Actualizar indicador de fortaleza de contraseña
document.getElementById('password').addEventListener('input', (e) => {
    const password = e.target.value;
    const strengthElement = document.getElementById('passwordStrength');
    if (strengthElement) {
        showPasswordStrength(password, 'passwordStrength');
    }
});

// Auto-focus en el primer campo
window.addEventListener('DOMContentLoaded', () => {
    if (token && token !== 'reset-password') {
        document.getElementById('password').focus();
    }
});
