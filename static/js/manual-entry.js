// manual-entry.js - Lógica para registro manual de sesiones VR

// Cargar lista de estudiantes
async function loadStudents() {
    try {
        const response = await fetch('/api/estudiantes');
        const data = await response.json();
        
        const select = document.getElementById('estudiante');
        data.forEach(estudiante => {
            const option = document.createElement('option');
            option.value = estudiante.id;
            option.textContent = `${estudiante.nombre} - ${estudiante.codigo}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar estudiantes:', error);
        showError('Error al cargar la lista de estudiantes');
    }
}

// Mostrar campo personalizado cuando se selecciona "Otro"
document.getElementById('maqueta').addEventListener('change', function() {
    const otraInput = document.getElementById('maqueta_otra');
    if (this.value === 'Otro') {
        otraInput.style.display = 'block';
        otraInput.required = true;
    } else {
        otraInput.style.display = 'none';
        otraInput.required = false;
        otraInput.value = '';
    }
});

// Actualizar valor del puntaje visualmente
document.getElementById('puntaje').addEventListener('input', function() {
    document.getElementById('puntajeValue').textContent = this.value;
});

// ============================================
// FUNCIONES PARA TIEMPO (MINUTOS Y SEGUNDOS)
// ============================================

/**
 * Calcula el tiempo total en segundos
 */
function calcularTiempoTotal() {
    const minutos = parseInt(document.getElementById('tiempo_minutos').value) || 0;
    const segundos = parseInt(document.getElementById('tiempo_segundos').value) || 0;
    return (minutos * 60) + segundos;
}

/**
 * Actualiza el display del tiempo total
 */
function actualizarDisplayTiempo() {
    const totalSegundos = calcularTiempoTotal();
    document.getElementById('tiempoTotal').textContent = totalSegundos + 's';
}

/**
 * Valida que los segundos no excedan 59
 */
function validarSegundos() {
    const inputSegundos = document.getElementById('tiempo_segundos');
    let valor = parseInt(inputSegundos.value) || 0;
    
    if (valor > 59) {
        const minutosExtra = Math.floor(valor / 60);
        const segundosRestantes = valor % 60;
        
        const inputMinutos = document.getElementById('tiempo_minutos');
        const minutosActuales = parseInt(inputMinutos.value) || 0;
        
        inputMinutos.value = minutosActuales + minutosExtra;
        inputSegundos.value = segundosRestantes;
    }
    
    actualizarDisplayTiempo();
}

// Event listeners para actualizar tiempo total en tiempo real
document.getElementById('tiempo_minutos').addEventListener('input', actualizarDisplayTiempo);
document.getElementById('tiempo_segundos').addEventListener('input', validarSegundos);

// Validar que solo se ingresen números
document.getElementById('tiempo_minutos').addEventListener('keypress', function(e) {
    if (!/[0-9]/.test(e.key)) {
        e.preventDefault();
    }
});

document.getElementById('tiempo_segundos').addEventListener('keypress', function(e) {
    if (!/[0-9]/.test(e.key)) {
        e.preventDefault();
    }
});

// Inicializar el display del tiempo total
actualizarDisplayTiempo();

// Funciones helper para alertas
function showSuccess(message) {
    const alertSuccess = document.getElementById('alertSuccess');
    alertSuccess.textContent = `✓ ${message}`;
    alertSuccess.style.display = 'block';
    
    const alertError = document.getElementById('alertError');
    alertError.style.display = 'none';
}

function showError(message) {
    const alertError = document.getElementById('alertError');
    alertError.textContent = `✗ ${message}`;
    alertError.style.display = 'block';
    
    const alertSuccess = document.getElementById('alertSuccess');
    alertSuccess.style.display = 'none';
}

function hideAlerts() {
    document.getElementById('alertSuccess').style.display = 'none';
    document.getElementById('alertError').style.display = 'none';
}

// Enviar formulario
document.getElementById('manualEntryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlerts();

    // Determinar nombre de maqueta
    let nombreMaqueta = document.getElementById('maqueta').value;
    if (nombreMaqueta === 'Otro') {
        nombreMaqueta = document.getElementById('maqueta_otra').value;
        if (!nombreMaqueta || nombreMaqueta.trim() === '') {
            showError('Por favor especifica el nombre de la maqueta');
            return;
        }
    }

    // Preparar datos de respuestas
    let respuestas = [];
    const respuestasText = document.getElementById('respuestas')?.value.trim();
    
    if (respuestasText) {
        try {
            respuestas = JSON.parse(respuestasText);
        } catch (e) {
            // Si no es JSON válido, convertir a array de strings
            respuestas = respuestasText.split('\n').filter(r => r.trim());
        }
    }

    // Obtener tiempo total en segundos (minutos * 60 + segundos)
    const tiempoSegundos = calcularTiempoTotal();
    
    // Validar que el tiempo sea mayor a 0
    if (tiempoSegundos <= 0) {
        showError('El tiempo de sesión debe ser mayor a 0 segundos');
        return;
    }

    const data = {
        estudiante_id: parseInt(document.getElementById('estudiante').value),
        maqueta: nombreMaqueta,
        tiempo_segundos: tiempoSegundos,
        puntaje: parseFloat(document.getElementById('puntaje').value),
        interacciones_ia: parseInt(document.getElementById('interacciones').value) || 0,
        respuestas: respuestas
    };

    try {
        const response = await fetch('/api/session/manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showSuccess(result.message || 'Sesión registrada exitosamente');
            document.getElementById('manualEntryForm').reset();
            document.getElementById('puntajeValue').textContent = '4';
            
            // Resetear valores de tiempo
            document.getElementById('tiempo_minutos').value = 1;
            document.getElementById('tiempo_segundos').value = 0;
            actualizarDisplayTiempo();
            
            // Redirigir al dashboard después de 2 segundos
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            showError(result.message || 'Error al registrar la sesión');
        }
    } catch (error) {
        showError('Error de conexión. Intenta nuevamente.');
        console.error('Error:', error);
    }
});

// Cargar estudiantes al iniciar
loadStudents();
