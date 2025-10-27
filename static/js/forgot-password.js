// forgot-password.js - Lógica para recuperación de contraseña

document.getElementById('forgotPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    disableSubmitButton('submitBtn', 'Enviando...');

    const email = document.getElementById('email').value.trim();

    // Validación
    if (!isValidEmail(email)) {
        showError('Por favor ingresa un email válido');
        enableSubmitButton('submitBtn');
        return;
    }

    try {
        const data = await apiPost('/forgot-password', { email });
        
        if (data.success !== false) {
            showSuccess('Se ha enviado un correo con instrucciones para recuperar tu contraseña');
            // Limpiar el formulario
            document.getElementById('forgotPasswordForm').reset();
        } else {
            showError(data.message || 'Error al enviar el correo');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión. Por favor intenta nuevamente.');
    } finally {
        enableSubmitButton('submitBtn');
    }
});

// Auto-focus en el campo email
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('email').focus();
});
