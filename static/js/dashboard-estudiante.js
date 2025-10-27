// dashboard-estudiante.js - Lógica del dashboard del estudiante

// ============================================
// UTILIDADES
// ============================================

/**
 * Formatea segundos a formato MM:SS
 * @param {number} segundos - Tiempo en segundos
 * @returns {string} Tiempo formateado como MM:SS
 */
function formatearTiempo(segundos) {
    if (segundos === null || segundos === undefined || isNaN(segundos)) {
        return '00:00';
    }
    const mins = Math.floor(segundos / 60);
    const secs = Math.floor(segundos % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ============================================
// FUNCIONES UX/UI PROFESIONALES
// ============================================

function showLoading(message = 'Cargando datos...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = overlay.querySelector('.spinner-text');
    text.textContent = message;
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
}

function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
            <div class="toast-progress">
                <div class="toast-progress-bar"></div>
            </div>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

let confirmCallback = null;

function showConfirm(message, title = 'Confirmación', icon = '⚠️', confirmText = 'Confirmar', confirmClass = 'primary') {
    return new Promise((resolve) => {
        const modal = document.getElementById('confirmModal');
        const titleEl = document.getElementById('confirmTitle');
        const iconEl = document.getElementById('confirmIcon');
        const messageEl = document.getElementById('confirmMessage');
        const confirmBtn = document.getElementById('confirmButton');

        titleEl.textContent = title;
        iconEl.textContent = icon;
        messageEl.textContent = message;
        confirmBtn.textContent = confirmText;
        confirmBtn.className = `btn-confirm ${confirmClass}`;

        confirmCallback = () => {
            resolve(true);
            hideConfirmModal();
        };

        confirmBtn.onclick = confirmCallback;
        modal.classList.add('active');

        modal.onclick = (e) => {
            if (e.target === modal) {
                resolve(false);
                hideConfirmModal();
            }
        };
    });
}

function hideConfirmModal() {
    const modal = document.getElementById('confirmModal');
    modal.classList.remove('active');
    confirmCallback = null;
}

async function confirmLogout() {
    const confirmed = await showConfirm(
        '¿Estás seguro de que deseas cerrar sesión?',
        'Cerrar Sesión',
        '🚪',
        'Cerrar Sesión',
        'danger'
    );

    if (confirmed) {
        logout();
    }
}

// ============================================
// FUNCIONES PRINCIPALES
// ============================================

let progresoChart = null;
let maquetasChart = null;

// Cargar datos del estudiante
async function refreshData() {
    showLoading('Cargando tus datos...');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';
    document.getElementById('noData').style.display = 'none';

    try {
        const response = await fetch('/api/estudiante/analytics');
        const data = await response.json();

        console.log('📊 Datos recibidos:', data);

        if (!data.success || data.total_sesiones === 0) {
            hideLoading();
            document.getElementById('loading').style.display = 'none';
            document.getElementById('noData').style.display = 'block';
            loadProfesores(); // Cargar profesores de todos modos
            showToast('No tienes sesiones registradas todavía', 'info');
            return;
        }

        // Actualizar estadísticas con validación defensiva
        document.getElementById('totalSesiones').textContent = data.total_sesiones || 0;
        
        const stats = data.estadisticas || {};
        document.getElementById('puntajePromedio').textContent = 
            (stats.puntaje_promedio || 0).toFixed(1) + ' / 7.0';
        document.getElementById('mejorPuntaje').textContent = 
            (stats.puntaje_maximo || 0).toFixed(1) + ' / 7.0';
        document.getElementById('tiempoPromedio').textContent = 
            formatearTiempo(stats.tiempo_promedio_segundos || 0);

        // Insights
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = '';
        const insights = data.insights || [];
        insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });

        // Gráfico de progreso
        updateProgresoChart(data.progreso_temporal || []);

        // Gráfico de maquetas
        updateMaquetasChart(data.por_maqueta || []);

        // Detalle por maqueta
        displayMaquetasDetalle(data.por_maqueta || []);

        // Cargar información de profesores
        loadProfesores();

        hideLoading();
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        showToast('Datos actualizados correctamente', 'success');
    } catch (error) {
        console.error('❌ Error al cargar datos:', error);
        hideLoading();
        document.getElementById('loading').innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h3 style="color: #dc3545;">⚠️ Error al cargar datos</h3>
                <p style="color: #666; margin: 15px 0;">${error.message}</p>
                <button onclick="refreshData()" class="btn btn-primary">🔄 Reintentar</button>
            </div>
        `;
        showToast('Error al cargar datos: ' + error.message, 'error');
    }
}

// Gráfico de progreso temporal por maqueta
function updateProgresoChart(progresoData) {
    const ctx = document.getElementById('progresoChart').getContext('2d');
    
    if (progresoChart) {
        progresoChart.destroy();
    }

    // Validar si hay datos
    if (!progresoData || typeof progresoData !== 'object' || Object.keys(progresoData).length === 0) {
        // Sin datos
        progresoChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Sin datos'],
                datasets: [{
                    label: 'Sin datos',
                    data: [0],
                    borderColor: '#ccc',
                    backgroundColor: 'rgba(200, 200, 200, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true } },
                scales: { y: { beginAtZero: true, max: 7 } }
            }
        });
        return;
    }

    // progresoData es un objeto: { 'Maqueta1': [{puntaje, fecha, fecha_completa}, ...], 'Maqueta2': [...] }
    const maquetas = Object.keys(progresoData);
    
    // Colores para cada maqueta
    const colores = [
        { border: 'rgba(102, 126, 234, 1)', bg: 'rgba(102, 126, 234, 0.1)' },    // Azul
        { border: 'rgba(244, 67, 54, 1)', bg: 'rgba(244, 67, 54, 0.1)' },        // Rojo
        { border: 'rgba(76, 175, 80, 1)', bg: 'rgba(76, 175, 80, 0.1)' },        // Verde
        { border: 'rgba(255, 152, 0, 1)', bg: 'rgba(255, 152, 0, 0.1)' },        // Naranja
        { border: 'rgba(156, 39, 176, 1)', bg: 'rgba(156, 39, 176, 0.1)' },      // Morado
        { border: 'rgba(0, 188, 212, 1)', bg: 'rgba(0, 188, 212, 0.1)' }         // Cyan
    ];

    // Recopilar todas las fechas únicas y ordenarlas
    const todasFechas = new Set();
    Object.values(progresoData).forEach(sesiones => {
        sesiones.forEach(s => todasFechas.add(s.fecha_completa));
    });
    const fechasOrdenadas = Array.from(todasFechas).sort();
    const labels = fechasOrdenadas.map(f => {
        const [y, m, d] = f.split('-');
        return `${d}/${m}`;
    });

    // Crear datasets (una línea por maqueta)
    const datasets = maquetas.map((maqueta, index) => {
        const sesiones = progresoData[maqueta];
        const colorIndex = index % colores.length;
        
        // Mapear puntajes a fechas correspondientes
        const data = fechasOrdenadas.map(fecha => {
            const sesion = sesiones.find(s => s.fecha_completa === fecha);
            return sesion ? sesion.puntaje : null;
        });

        return {
            label: maqueta,
            data: data,
            borderColor: colores[colorIndex].border,
            backgroundColor: colores[colorIndex].bg,
            tension: 0.4,
            fill: true,
            spanGaps: true  // Conectar puntos aunque haya nulls
        };
    });

    progresoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const maqueta = context.dataset.label;
                            const puntaje = context.parsed.y;
                            if (puntaje === null) return null;
                            return `${maqueta}: ${puntaje} / 7`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 7,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Gráfico de puntajes por maqueta
function updateMaquetasChart(porMaqueta) {
    const ctx = document.getElementById('maquetasChart').getContext('2d');
    
    if (maquetasChart) {
        maquetasChart.destroy();
    }

    // Validar y transformar datos
    let maquetas, puntajes;
    
    if (!porMaqueta || !Array.isArray(porMaqueta) || porMaqueta.length === 0) {
        // Sin datos
        maquetas = ['Sin datos'];
        puntajes = [0];
    } else {
        // porMaqueta es un array de {maqueta, sesiones, puntaje_promedio, mejor}
        maquetas = porMaqueta.map(m => m.maqueta || 'Sin nombre');
        puntajes = porMaqueta.map(m => m.puntaje_promedio || 0);
    }

    maquetasChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: maquetas,
            datasets: [{
                label: 'Puntaje Promedio',
                data: puntajes,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 7
                }
            }
        }
    });
}

// Detalle por maqueta
function displayMaquetasDetalle(porMaqueta) {
    const container = document.getElementById('maquetasDetalle');
    container.innerHTML = '';

    if (!porMaqueta || !Array.isArray(porMaqueta) || porMaqueta.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <p style="font-size: 18px;">📊 No hay datos de maquetas todavía</p>
                <p style="font-size: 14px;">Completa sesiones para ver tu progreso</p>
            </div>
        `;
        return;
    }

    // porMaqueta es un array de objetos
    for (const stats of porMaqueta) {
        const card = document.createElement('div');
        card.className = 'maqueta-card';
        card.innerHTML = `
            <div class="maqueta-header">🎮 ${stats.maqueta || 'Sin nombre'}</div>
            <div class="maqueta-stats">
                <div><strong>Sesiones:</strong> ${stats.sesiones || 0}</div>
                <div><strong>Promedio:</strong> ${(stats.puntaje_promedio || 0).toFixed(1)} / 7.0</div>
                <div><strong>Mejor:</strong> ${(stats.mejor || 0).toFixed(1)} / 7.0</div>
            </div>
        `;
        container.appendChild(card);
    }
}

// Cargar profesores
async function loadProfesores() {
    try {
        const response = await fetch('/api/estudiante/profesores');
        const data = await response.json();

        // data es un array directo de profesores
        if (Array.isArray(data) && data.length > 0) {
            // Mostrar sección de profesores
            document.getElementById('profesorActual').style.display = 'block';
            
            let html = '';
            data.forEach(prof => {
                html += `
                    <div class="profesor-card" style="margin-bottom: 10px;">
                        <div class="profesor-info">
                            <div class="profesor-name">${prof.nombre}</div>
                            <div class="profesor-email">${prof.email}</div>
                            <div class="profesor-email">${prof.institucion || 'Sin institución'}</div>
                        </div>
                        <div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #667eea;">${prof.total_sesiones || 0}</div>
                                <div style="font-size: 12px; color: #666;">sesiones</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('profesorActualCard').innerHTML = html;
            
            // Llenar selector de filtro si hay más de un profesor
            if (data.length > 1) {
                document.getElementById('filtroProfesor').style.display = 'block';
                const select = document.getElementById('profesorFilter');
                select.innerHTML = '<option value="">Todos los profesores</option>';
                
                data.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = prof.id;
                    option.textContent = `${prof.nombre} (${prof.total_sesiones || 0} sesiones)`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error al cargar profesores:', error);
    }
}

// Filtrar analytics por profesor específico
async function filtrarPorProfesor() {
    const profesorId = document.getElementById('profesorFilter').value;
    
    if (!profesorId) {
        // Si no hay profesor seleccionado, recargar datos generales
        await refreshData();
        return;
    }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';
    
    try {
        const response = await fetch(`/api/estudiante/analytics-profesor/${profesorId}`);
        const data = await response.json();
        
        if (!data.success) {
            alert(data.message || 'Error al cargar datos del profesor');
            return;
        }
        
        // Actualizar estadísticas con datos filtrados
        document.getElementById('totalSesiones').textContent = data.total_sesiones;
        document.getElementById('puntajePromedio').textContent = data.estadisticas.puntaje_promedio ? data.estadisticas.puntaje_promedio.toFixed(1) + ' / 7.0' : '0';
        document.getElementById('mejorPuntaje').textContent = data.estadisticas.puntaje_maximo ? data.estadisticas.puntaje_maximo.toFixed(1) + ' / 7.0' : '0';
        document.getElementById('tiempoPromedio').textContent = data.estadisticas.tiempo_promedio_segundos ? formatearTiempo(data.estadisticas.tiempo_promedio_segundos) : '00:00';
        
        // Actualizar insights
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = '';
        data.insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });
        
        // Actualizar gráficos
        updateProgresoChart(data.progreso_temporal);
        updateMaquetasChart(data.por_maqueta);
        displayMaquetasDetalle(data.por_maqueta);
        
        // Guardar sesiones filtradas para el modal de maquetas
        misSesiones = data.sesiones;
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
    } catch (error) {
        console.error('Error al filtrar por profesor:', error);
        document.getElementById('loading').textContent = 'Error al filtrar datos. Intenta nuevamente.';
    }
}

// Limpiar filtro de profesor
function limpiarFiltroProfesor() {
    document.getElementById('profesorFilter').value = '';
    refreshData();
}

// Modal de profesores
async function openProfesorModal() {
    document.getElementById('profesorModal').style.display = 'block';
    
    try {
        // Cargar todos los profesores disponibles y los del estudiante
        const [profesoresResponse, misProfesoresResponse] = await Promise.all([
            fetch('/api/profesores'),
            fetch('/api/estudiante/profesores')
        ]);
        
        const todosLosProfesores = await profesoresResponse.json();
        const misProfesores = await misProfesoresResponse.json();
        
        // Crear Set con IDs de profesores inscritos para búsqueda rápida
        const profesoresInscritosIds = new Set(misProfesores.map(p => p.id));

        let html = '<h3 style="margin-bottom: 15px;">Profesores Disponibles</h3>';
        
        if (!todosLosProfesores || todosLosProfesores.length === 0) {
            html += '<p>No hay profesores disponibles.</p>';
        } else {
            todosLosProfesores.forEach(profesor => {
                const isInscrito = profesoresInscritosIds.has(profesor.id);
                html += `
                    <div class="profesor-list-item" onclick="${!isInscrito ? `inscribirseProfesor(${profesor.id}, '${profesor.nombre.replace(/'/g, "\\'")}')` : ''}" style="${isInscrito ? 'opacity: 0.7; cursor: default;' : 'cursor: pointer;'}">
                        <div class="profesor-name">
                            ${profesor.nombre}
                            ${isInscrito ? '<span class="badge badge-current">✓ Inscrito</span>' : ''}
                        </div>
                        <div class="profesor-email">${profesor.email}</div>
                        <div class="profesor-email">${profesor.institucion || 'Sin institución'}</div>
                    </div>
                `;
            });
        }

        document.getElementById('profesorModalContent').innerHTML = html;
    } catch (error) {
        console.error('Error al cargar profesores:', error);
        document.getElementById('profesorModalContent').innerHTML = '<p>Error al cargar profesores. Por favor, intenta de nuevo.</p>';
    }
}

function closeProfesorModal() {
    document.getElementById('profesorModal').style.display = 'none';
}

// Inscribirse con profesor
async function inscribirseProfesor(profesorId, profesorNombre) {
    const confirmed = await showConfirm(
        `¿Deseas inscribirte con el profesor ${profesorNombre}?`,
        'Inscripción a Profesor',
        '👨‍🏫',
        'Inscribirme',
        'primary'
    );

    if (!confirmed) return;

    showLoading('Procesando inscripción...');

    try {
        const response = await fetch('/api/estudiante/inscribirse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ profesor_id: profesorId })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            if (data.ya_inscrito) {
                showToast('Ya estás inscrito con este profesor', 'info');
            } else {
                showToast(`¡Te has inscrito exitosamente con ${profesorNombre}!`, 'success');
            }
            closeProfesorModal();
            refreshData();  // Recargar datos para mostrar el nuevo profesor
        } else {
            showToast('Error: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error al inscribirse:', error);
        hideLoading();
        showToast('Error al procesar la solicitud', 'error');
    }
}

// Cerrar sesión
function logout() {
    window.location.href = '/logout';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('profesorModal');
    if (event.target === modal) {
        closeProfesorModal();
    }
    const modalMaqueta = document.getElementById('maquetaModalEstudiante');
    if (event.target === modalMaqueta) {
        cerrarModalMaquetaEstudiante();
    }
}

// Funciones para modal de maquetas del estudiante
let misSesiones = [];
let misProfesores = [];

async function verMisMaquetas() {
    showLoading('Cargando maquetas...');
    try {
        const response = await fetch('/api/estudiante/analytics');
        const data = await response.json();

        if (!data.sesiones || data.sesiones.length === 0) {
            hideLoading();
            showToast('No tienes sesiones registradas aún', 'info');
            return;
        }

        misSesiones = data.sesiones;

        // Obtener profesores únicos de las sesiones
        const profesoresMap = new Map();
        misSesiones.forEach(s => {
            if (s.profesor) {
                profesoresMap.set(s.profesor.id, s.profesor.nombre);
            }
        });
        misProfesores = Array.from(profesoresMap, ([id, nombre]) => ({ id, nombre }));

        // Obtener maquetas únicas
        const maquetasUnicas = [...new Set(misSesiones.map(s => s.maqueta))];

        // Mostrar modal
        document.getElementById('maquetaModalEstudiante').style.display = 'block';

        // Llenar selector de maquetas
        const select = document.getElementById('maquetaSelectEst');
        select.innerHTML = '<option value="">Selecciona una maqueta...</option>';
        maquetasUnicas.forEach(maqueta => {
            const option = document.createElement('option');
            option.value = maqueta;
            option.textContent = maqueta;
            select.appendChild(option);
        });

        // Llenar selector de profesores
        const profesorSelect = document.getElementById('profesorSelectModal');
        profesorSelect.innerHTML = '<option value="">Todos los profesores</option>';
        misProfesores.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = prof.nombre;
            profesorSelect.appendChild(option);
        });

        hideLoading();

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showToast('Error al cargar tus sesiones', 'error');
    }
}

function cerrarModalMaquetaEstudiante() {
    document.getElementById('maquetaModalEstudiante').style.display = 'none';
}

function filtrarMisMaquetas() {
    showLoading('Filtrando sesiones...');
    const maquetaSeleccionada = document.getElementById('maquetaSelectEst').value;
    const profesorSeleccionado = document.getElementById('profesorSelectModal').value;

    if (!maquetaSeleccionada) {
        document.getElementById('maquetaResultadosEst').innerHTML = '<div class="no-data">Por favor selecciona una maqueta</div>';
        hideLoading();
        return;
    }

    // Filtrar por maqueta
    let sesionesFiltradas = misSesiones.filter(s => s.maqueta === maquetaSeleccionada);

    // Filtrar por profesor si está seleccionado
    if (profesorSeleccionado) {
        sesionesFiltradas = sesionesFiltradas.filter(s => 
            s.profesor && s.profesor.id == profesorSeleccionado
        );
    }

    if (sesionesFiltradas.length === 0) {
        document.getElementById('maquetaResultadosEst').innerHTML = '<div class="no-data">No tienes sesiones para esta combinación de filtros</div>';
        hideLoading();
        return;
    }

    // Calcular estadísticas
    const totalSesiones = sesionesFiltradas.length;
    const puntajes = sesionesFiltradas.map(s => s.puntaje);
    const tiempos = sesionesFiltradas.map(s => s.tiempo_segundos);

    const promedioPuntaje = (puntajes.reduce((a, b) => a + b, 0) / totalSesiones).toFixed(2);
    const promedioTiempoSegundos = tiempos.reduce((a, b) => a + b, 0) / totalSesiones;
    const promedioTiempo = formatearTiempo(promedioTiempoSegundos);
    const mejorPuntaje = Math.max(...puntajes).toFixed(2);
    const peorPuntaje = Math.min(...puntajes).toFixed(2);
    
    const filtroProfesor = profesorSeleccionado ? misProfesores.find(p => p.id == profesorSeleccionado)?.nombre : 'Todos';

    // Generar HTML
    let html = `
        <div class="maqueta-stats-est">
            <div class="maqueta-stat-card-est">
                <h4>MIS SESIONES</h4>
                <div class="value">${totalSesiones}</div>
            </div>
            <div class="maqueta-stat-card-est">
                <h4>PROMEDIO</h4>
                <div class="value">${promedioPuntaje} / 7.0</div>
            </div>
            <div class="maqueta-stat-card-est">
                <h4>MEJOR PUNTAJE</h4>
                <div class="value">${mejorPuntaje} / 7.0</div>
            </div>
            <div class="maqueta-stat-card-est">
                <h4>PEOR PUNTAJE</h4>
                <div class="value">${peorPuntaje} / 7.0</div>
            </div>
            <div class="maqueta-stat-card-est">
                <h4>TIEMPO PROMEDIO</h4>
                <div class="value">${promedioTiempo}</div>
            </div>
        </div>

        <div class="sessions-table-est">
            <h3>📋 Mis Sesiones en ${maquetaSeleccionada} ${profesorSeleccionado ? '- Profesor: ' + filtroProfesor : ''}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Puntaje</th>
                        <th>Tiempo</th>
                        <th>IA Usada</th>
                        <th>Evaluado por</th>
                    </tr>
                </thead>
                <tbody>
    `;

    sesionesFiltradas.forEach(sesion => {
        const fecha = new Date(sesion.fecha).toLocaleDateString('es-ES');
        const tiempo = formatearTiempo(sesion.tiempo_segundos);
        const puntajeClass = sesion.puntaje >= 4 ? 'good' : 'risk';
        const profesorNombre = sesion.profesor ? sesion.profesor.nombre : 'Sin registro';

        html += `
            <tr>
                <td>${fecha}</td>
                <td class="${puntajeClass}">${sesion.puntaje.toFixed(1)} / 7.0</td>
                <td>${tiempo}</td>
                <td>${sesion.interacciones_ia} veces</td>
                <td><strong>${profesorNombre}</strong></td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    document.getElementById('maquetaResultadosEst').innerHTML = html;
    hideLoading();
}

// Cargar datos al iniciar
window.onload = refreshData;
