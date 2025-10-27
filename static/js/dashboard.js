// ============================================
// DASHBOARD VR ANALYTICS - JS OPTIMIZADO
// ============================================

// ============================================
// CONFIGURACIÓN Y VARIABLES GLOBALES
// ============================================
const CONFIG = {
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutos
    TOAST_DURATION: 4000,
    DEBOUNCE_DELAY: 300
};

let scoresChart, maquetasChart, scatterChart, trendChart;
let dataCache = {
    analytics: null,
    timestamp: null
};
let maquetasDisponibles = [];
let todasSesiones = [];
let confirmCallback = null;

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

/**
 * Debounce para optimizar eventos
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Verifica si el caché es válido
 */
function isCacheValid() {
    if (!dataCache.analytics || !dataCache.timestamp) return false;
    return (Date.now() - dataCache.timestamp) < CONFIG.CACHE_DURATION;
}

/**
 * Guarda datos en caché
 */
function cacheData(data) {
    dataCache.analytics = data;
    dataCache.timestamp = Date.now();
}

// ============================================
// FUNCIONES UX/UI PROFESIONALES
// ============================================

/**
 * Muestra overlay de carga
 */
function showLoading(message = 'Cargando datos...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = overlay.querySelector('.spinner-text');
    text.textContent = message;
    overlay.classList.add('active');
}

/**
 * Oculta overlay de carga
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
}

/**
 * Sistema de notificaciones Toast
 */
function showToast(message, type = 'info', duration = CONFIG.TOAST_DURATION) {
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

/**
 * Modal de confirmación
 */
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

function logout() {
    window.location.href = '/logout';
}

// ============================================
// FUNCIONES PRINCIPALES
// ============================================

/**
 * Refresca los datos del dashboard (con caché)
 */
async function refreshData(forceRefresh = false) {
    // Verificar caché
    if (!forceRefresh && isCacheValid()) {
        console.log('📦 Usando datos del caché');
        updateDashboard(dataCache.analytics);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        showToast('Datos actualizados correctamente', 'success');
        return;
    }

    showLoading('Actualizando datos...');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';

    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        if (response.ok) {
            if (data.message && data.message.includes('No hay datos')) {
                hideLoading();
                showEmptyState();
            } else {
                cacheData(data); // Guardar en caché
                updateDashboard(data);
                hideLoading();
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
                showToast('Datos actualizados correctamente', 'success');
            }
        } else {
            hideLoading();
            showErrorState(data.message || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showConnectionError(error.message);
    }
}

/**
 * Muestra estado vacío
 */
function showEmptyState() {
    document.getElementById('loading').innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center; color: #333;">
            <h2 style="color: #667eea;">📊 Bienvenido al Dashboard</h2>
            <p style="margin: 20px 0;">Aún no hay datos para analizar.</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 20px;">
                <h3 style="color: #667eea; margin-bottom: 15px;">Para comenzar:</h3>
                <ol style="text-align: left; display: inline-block;">
                    <li style="margin: 10px 0;">Ingresa manualmente los datos</li>
                    <li style="margin: 10px 0;">Luego recarga esta página</li>
                </ol>
            </div>
            <button onclick="refreshData(true)" class="btn btn-primary" style="margin-top: 20px;">Recargar Datos</button>
        </div>
    `;
}

/**
 * Muestra error de servidor
 */
function showErrorState(message) {
    document.getElementById('loading').innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center; color: #333;">
            <h2 style="color: #dc3545;">⚠️ Error</h2>
            <p>No se pudieron cargar los datos. ${message}</p>
            <button onclick="refreshData(true)" class="btn btn-primary" style="margin-top: 20px;">Reintentar</button>
        </div>
    `;
}

/**
 * Muestra error de conexión
 */
function showConnectionError(message) {
    document.getElementById('loading').innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center; color: #333;">
            <h2 style="color: #dc3545;">⚠️ Error de Conexión</h2>
            <p>No se pudo conectar con el servidor.</p>
            <p style="color: #666; font-size: 14px;">${message}</p>
            <button onclick="refreshData(true)" class="btn btn-primary" style="margin-top: 20px;">Reintentar</button>
        </div>
    `;
}

/**
 * Actualiza el dashboard con datos
 */
function updateDashboard(data) {
    if (!data.estadisticas || !data.estadisticas.general) {
        console.error('Datos incompletos recibidos');
        return;
    }
    
    // Actualizar estadísticas (optimizado con requestAnimationFrame)
    requestAnimationFrame(() => {
        updateStats(data.estadisticas.general);
        displayInsights(data.insights);
        displayCorrelations(data.correlaciones);
        displayPrediction(data.prediccion);
    });

    // ML Modules (lazy loading)
    setTimeout(() => {
        displayMLClasificacion(data.ml_clasificacion);
        displayMLClustering(data.ml_clustering);
        displayMLCorrelaciones(data.ml_correlaciones);
    }, 100);

    // Gráficos (lazy loading)
    setTimeout(() => updateCharts(data), 200);

    // Tablas (lazy loading)
    setTimeout(() => {
        updateRiskTable(data.estudiantes_riesgo);
        updateRankingTable(data.ranking);
    }, 300);
}

/**
 * Actualiza estadísticas generales
 */
function updateStats(stats) {
    document.getElementById('total-sesiones').textContent = stats.total_sesiones || 0;
    document.getElementById('total-estudiantes').textContent = stats.total_estudiantes || 0;
    document.getElementById('promedio-puntaje').textContent = stats.promedio_puntaje || 0;
    document.getElementById('tasa-aprobacion').textContent = (stats.tasa_aprobacion || 0) + '%';
    document.getElementById('tiempo-promedio').textContent = stats.promedio_tiempo_segundos ? formatearTiempo(stats.promedio_tiempo_segundos) : '00:00';
    document.getElementById('desviacion-puntaje').textContent = stats.desviacion_puntaje || 0;
}

// ============================================
// FUNCIONES DE VISUALIZACIÓN (importadas del HTML original)
// ============================================

function displayInsights(insights) {
    const container = document.getElementById('insights-container');
    container.innerHTML = '';

    if (!insights || insights.length === 0) return;

    insights.forEach(insight => {
        const alertClass = insight.tipo === 'critico' ? 'background: #f8d7da; border-color: #dc3545;' :
                         insight.tipo === 'atencion' ? 'background: #fff3cd; border-color: #ffc107;' :
                         insight.tipo === 'positivo' ? 'background: #d4edda; border-color: #28a745;' :
                         'background: #d1ecf1; border-color: #17a2b8;';
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert';
        alertDiv.style = alertClass;
        alertDiv.innerHTML = insight.mensaje;
        container.appendChild(alertDiv);
    });
}

function displayCorrelations(corr) {
    const content = document.getElementById('correlation-content');
    
    if (!corr) {
        content.innerHTML = '<p>No hay suficientes datos</p>';
        return;
    }

    const tiempoStatus = corr.tiempo_puntaje.significativo ? '✅ Significativa' : '⚠️ No significativa';
    const iaStatus = corr.ia_puntaje.significativo ? '✅ Significativa' : '⚠️ No significativa';

    content.innerHTML = `

        <div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px;">
            <strong style=" color: #856404;">Recomendaciones:</strong>
            <ul style="margin: 5px 0; padding-left: 20px; font-size: 13px; color: #856404;">
                ${corr.recomendaciones.map(r => `<li>${r}</li>`).join('')}
            </ul>
        </div>

        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <ul style="margin: 5px 0; padding-left: 20px;">
            </ul>
        </div>
    `;
}

function displayPrediction(pred) {
    const content = document.getElementById('prediction-content');
    
    // Verificar si el elemento existe en el DOM
    if (!content) {
        console.warn('Elemento prediction-content no encontrado en el DOM');
        return;
    }
    
    if (!pred || !pred.r2_score) {
        content.innerHTML = '<p>No hay suficientes datos para predicción</p>';
        return;
    }

    content.innerHTML = `
        <div style="margin-bottom: 15px;">
            <strong>Precisión del Modelo:</strong><br>
            <span style="font-size: 24px; font-weight: bold; color: ${pred.r2_score > 0.7 ? '#28a745' : pred.r2_score > 0.4 ? '#ffc107' : '#dc3545'};">
                ${(pred.r2_score * 100).toFixed(1)}%
            </span> (${pred.precision})
        </div>
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;">
            ${pred.formula}
        </div>
        <div style="margin-top: 10px;">
            <em>${pred.interpretacion}</em>
        </div>
    `;
}

// Continuará en el siguiente mensaje debido al límite de caracteres...
