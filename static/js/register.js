// register.js - Lógica específica de la página de registro

// Cargar lista de profesores para estudiantes
async function loadProfesores() {
    try {
        const response = await fetch('/api/profesores');
        const profesores = await response.json();
        
        const select = document.getElementById('email_profesor');
        profesores.forEach(profesor => {
            const option = document.createElement('option');
            option.value = profesor.email;
            option.textContent = `${profesor.nombre} - ${profesor.institucion || 'Sin institución'}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar profesores:', error);
    }
}

// Manejar selección visual de tipo de usuario
document.querySelectorAll('.tipo-usuario-option').forEach(option => {
    option.addEventListener('click', function() {
        // Remover selección de todas las opciones
        document.querySelectorAll('.tipo-usuario-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Agregar selección a la opción clickeada
        this.classList.add('selected');
        
        // Marcar el radio button correspondiente
        const radio = this.querySelector('input[type="radio"]');
        radio.checked = true;
        
        // Disparar evento change
        radio.dispatchEvent(new Event('change'));
    });
});

// Manejar cambio de tipo de usuario
document.querySelectorAll('input[name="tipo_usuario"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const esProfesor = e.target.value === 'profesor';
        
        // Mostrar/ocultar campos según tipo de usuario
        document.getElementById('institucionGroup').style.display = esProfesor ? 'block' : 'none';
        document.getElementById('nivelGroup').style.display = esProfesor ? 'none' : 'block';
        document.getElementById('profesorGroup').style.display = esProfesor ? 'none' : 'block';
        
        // Actualizar requeridos
        document.getElementById('institucion').required = esProfesor;
        document.getElementById('email_profesor').required = false;
        
        // Cargar profesores si es estudiante
        if (!esProfesor && document.getElementById('email_profesor').options.length === 1) {
            loadProfesores();
        }
    });
});

// Password strength indicator
document.getElementById('password').addEventListener('input', (e) => {
    const password = e.target.value;
    const strengthBar = document.getElementById('strengthBar');
    let strength = 0;

    if (password.length >= 6) strength += 25;
    if (password.length >= 10) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;

    strengthBar.style.width = strength + '%';
    
    if (strength < 50) {
        strengthBar.style.background = '#dc3545';
    } else if (strength < 75) {
        strengthBar.style.background = '#ffc107';
    } else {
        strengthBar.style.background = '#28a745';
    }
});

// Manejar envío del formulario
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    const submitBtn = document.getElementById('submitBtn');
    const errorDiv = document.getElementById('error');
    const successDiv = document.getElementById('success');
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (password !== confirmPassword) {
        showError('Las contraseñas no coinciden');
        return;
    }

    disableSubmitButton('submitBtn', 'Registrando...');

    const tipoUsuario = document.querySelector('input[name="tipo_usuario"]:checked').value;
    
    const formData = {
        tipo_usuario: tipoUsuario,
        nombre: document.getElementById('nombre').value,
        email: document.getElementById('email').value,
        password: password
    };

    // Agregar token de reCAPTCHA si está habilitado
    if (typeof grecaptcha !== 'undefined') {
        const recaptchaResponse = grecaptcha.getResponse();
        if (recaptchaResponse) {
            formData.recaptcha_token = recaptchaResponse;
        }
    }

    // Agregar campos específicos según tipo de usuario
    if (tipoUsuario === 'profesor') {
        formData.institucion = document.getElementById('institucion').value;
    } else {
        formData.nivel_habilidad = parseInt(document.getElementById('nivel').value);
        const emailProfesor = document.getElementById('email_profesor').value;
        if (emailProfesor) {
            formData.email_profesor = emailProfesor;
        }
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            // Mostrar código generado si es estudiante
            if (tipoUsuario === 'estudiante' && data.codigo) {
                successDiv.innerHTML = `¡Registro exitoso!<br>Tu código de estudiante es: <strong>${data.codigo}</strong><br>Redirigiendo al login...`;
            } else {
                successDiv.textContent = '¡Registro exitoso! Redirigiendo al login...';
            }
            successDiv.style.display = 'block';
            setTimeout(() => {
                window.location.href = '/login';
            }, 3000);
        } else {
            showError(data.message || 'Error al registrarse');
            // Reset reCAPTCHA si falla
            if (typeof grecaptcha !== 'undefined') {
                grecaptcha.reset();
            }
            enableSubmitButton('submitBtn');
        }
    } catch (error) {
        showError('Error de conexión. Intenta nuevamente.');
        // Reset reCAPTCHA si hay error
        if (typeof grecaptcha !== 'undefined') {
            grecaptcha.reset();
        }
        enableSubmitButton('submitBtn');
    }
});
