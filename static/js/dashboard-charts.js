// ============================================
// DASHBOARD VR ANALYTICS - JS PARTE 2 (ML & CHARTS)
// ============================================

// Este archivo contiene las funciones ML y de gráficos
// Debe ser cargado después de dashboard.js

// ============================================
// FUNCIONES ML PROFESIONALES
// ============================================

function displayMLClasificacion(ml_data) {
    const container = document.getElementById('ml-clasificacion');
    
    if (!ml_data || !ml_data.modelo_disponible) {
        container.innerHTML = `
            <div style="padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                <p style="color: #666;">${ml_data?.mensaje || 'Modelo de clasificación no disponible'}</p>
            </div>
        `;
        return;
    }
    
    const mejor_accuracy = (ml_data.mejor_accuracy * 100).toFixed(1);
    
    let html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9;">Precisión del Modelo</div>
                <div style="font-size: 36px; font-weight: bold; margin: 10px 0;">${mejor_accuracy}%</div>
                <div style="font-size: 12px;">${ml_data.mejor_modelo}</div>
            </div>
            
            <div style="background: #28a745; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9;">Tasa de Aprobación</div>
                <div style="font-size: 36px; font-weight: bold; margin: 10px 0;">${ml_data.tasa_aprobacion_real.toFixed(1)}%</div>
                <div style="font-size: 12px;">${ml_data.aprobados} de ${ml_data.total_sesiones} sesiones</div>
            </div>
            
            <div style="background: #17a2b8; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9;">Aprobados</div>
                <div style="font-size: 36px; font-weight: bold; margin: 10px 0;">${ml_data.aprobados}</div>
                <div style="font-size: 12px;">✅ Puntaje ≥ 4.0</div>
            </div>
            
            <div style="background: #dc3545; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9;">Reprobados</div>
                <div style="font-size: 36px; font-weight: bold; margin: 10px 0;">${ml_data.reprobados}</div>
                <div style="font-size: 12px;">❌ Puntaje < 4.0</div>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="color: #667eea; margin-bottom: 15px;">📈 Importancia de Características</h4>
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>⏱️ Tiempo (segundos)</span>
                    <span><strong>${(ml_data.random_forest.feature_importance.tiempo_segundos * 100).toFixed(1)}%</strong></span>
                </div>
                <div style="background: #e9ecef; border-radius: 5px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 25px; width: ${ml_data.random_forest.feature_importance.tiempo_segundos * 100}%;"></div>
                </div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>🤖 Interacciones con IA</span>
                    <span><strong>${(ml_data.random_forest.feature_importance.interacciones_ia * 100).toFixed(1)}%</strong></span>
                </div>
                <div style="background: #e9ecef; border-radius: 5px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #f093fb, #f5576c); height: 25px; width: ${ml_data.random_forest.feature_importance.interacciones_ia * 100}%;"></div>
                </div>
            </div>
        </div>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px;">
            <h4 style="color: #856404; margin-bottom: 10px;">💡 Interpretación del Modelo</h4>
            <ul style="margin: 0; padding-left: 20px; color: #856404;">
                ${ml_data.interpretacion.map(item => `<li style="margin-bottom: 8px;">${item}</li>`).join('')}
            </ul>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayMLClustering(ml_clustering) {
    const container = document.getElementById('ml-clustering');
    
    if (!ml_clustering || !ml_clustering.clusters || Object.keys(ml_clustering.clusters).length === 0) {
        container.innerHTML = `
            <div style="padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                <p style="color: #666;">No hay suficientes datos para clustering profesional</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #666;">Total de Estudiantes:</span>
                    <strong style="font-size: 20px; color: #667eea; margin-left: 10px;">${ml_clustering.total_estudiantes}</strong>
                </div>
                <div>
                    <span style="color: #666;">Clusters Identificados:</span>
                    <strong style="font-size: 20px; color: #667eea; margin-left: 10px;">${ml_clustering.n_clusters}</strong>
                </div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 20px;">
    `;
    
    for (const [nombre, cluster] of Object.entries(ml_clustering.clusters)) {
        // Obtener lista de estudiantes (puede no estar disponible en clustering profesional)
        const tieneEstudiantes = cluster.estudiantes && cluster.estudiantes.length > 0;
        
        html += `
            <div style="background: ${cluster.color}15; border: 2px solid ${cluster.color}; border-radius: 10px; padding: 20px; transition: transform 0.2s;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 32px; margin-right: 10px;">${cluster.icono}</span>
                    <div>
                        <h4 style="margin: 0; color: ${cluster.color};">${nombre}</h4>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">${cluster.nivel}</p>
                    </div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                        <div>
                            <div style="color: #666;">Estudiantes:</div>
                            <div style="font-weight: bold; font-size: 18px; color: ${cluster.color};">${cluster.total_estudiantes}</div>
                        </div>
                        <div>
                            <div style="color: #666;">Promedio:</div>
                            <div style="font-weight: bold; font-size: 18px; color: ${cluster.color};">${cluster.promedio_puntaje} / 7.0</div>
                        </div>
                        <div>
                            <div style="color: #666;">Tiempo:</div>
                            <div style="font-weight: bold; color: #333;">${formatearTiempo(cluster.promedio_tiempo_segundos)}</div>
                        </div>
                        <div>
                            <div style="color: #666;">Uso IA:</div>
                            <div style="font-weight: bold; color: #333;">${cluster.promedio_uso_ia.toFixed(1)}</div>
                        </div>
                    </div>
                </div>
                
                <div style="background: ${cluster.color}10; padding: 10px; border-radius: 5px; margin-bottom: ${tieneEstudiantes ? '10px' : '0'};">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Características:</div>
                    ${cluster.caracteristicas.map(c => `
                        <span style="display: inline-block; background: white; padding: 4px 8px; border-radius: 3px; margin: 2px; font-size: 11px; color: ${cluster.color}; border: 1px solid ${cluster.color};">
                            ${c}
                        </span>
                    `).join('')}
                </div>
                
                ${tieneEstudiantes ? `
                    <details style="margin-top: 10px;">
                        <summary style="cursor: pointer; color: ${cluster.color}; font-weight: bold; padding: 8px; background: white; border-radius: 5px; border: 1px solid ${cluster.color}30;">
                            👥 Ver estudiantes (${cluster.estudiantes.length})
                        </summary>
                        <ul style="margin-top: 10px; padding-left: 20px; background: white; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">
                            ${cluster.estudiantes.map(e => `<li style="margin-bottom: 5px; color: #333;">${e}</li>`).join('')}
                        </ul>
                    </details>
                ` : ''}
            </div>
        `;
    }
    
    html += `
        </div>
        
        <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; border-radius: 5px;">
            <h4 style="color: #1976D2; margin-bottom: 10px;">🎯 Insights del Clustering</h4>
            <ul style="margin: 0; padding-left: 20px; color: #1976D2;">
                ${ml_clustering.interpretacion.map(item => `<li style="margin-bottom: 8px;">${item}</li>`).join('')}
            </ul>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayMLCorrelaciones(ml_corr) {
    const container = document.getElementById('ml-correlaciones');
    
    if (!ml_corr || !ml_corr.disponible) {
        container.innerHTML = `
            <div style="padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                <p style="color: #666;">${ml_corr?.mensaje || 'Análisis de correlaciones no disponible'}</p>
            </div>
        `;
        return;
    }
    
    const corrs = ml_corr.correlaciones;
    
    let html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px;">
    `;
    
    for (const [nombre, datos] of Object.entries(corrs)) {
        const color = datos.significativo ? (datos.correlacion > 0 ? '#28a745' : '#dc3545') : '#6c757d';
        const fuerza_color = datos.fuerza === 'Fuerte' ? '#dc3545' : datos.fuerza === 'Moderada' ? '#ffc107' : '#17a2b8';
        
        html += `
            <div style="background: ${color}10; border: 2px solid ${color}; border-radius: 10px; padding: 20px;">
                <h4 style="color: ${color}; margin-bottom: 15px; text-transform: capitalize;">
                    ${nombre.replace('_', ' → ')}
                </h4>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="text-align: center; margin-bottom: 10px;">
                        <div style="font-size: 12px; color: #666;">Coeficiente de Correlación</div>
                        <div style="font-size: 36px; font-weight: bold; color: ${color};">
                            ${datos.correlacion.toFixed(3)}
                        </div>
                    </div>
                    
                    <div style=" gap: 10px; font-size: 13px; border-top: 1px solid #eee; padding-top: 10px; text-align: center;">
                        <div style="color: #666;">
                            Fuerza: <a style="font-weight: bold; color: ${fuerza_color};">${datos.fuerza}</a>
                        </div> 
                    </div>
                </div>
                <div style="padding: 10px; background: ${datos.significativo ? '#d4edda' : '#f8d7da'}; border-radius: 5px; text-align: center;">
                    <span style="font-size: 12px; color: ${datos.significativo ? '#155724' : '#721c24'};">
                        ${datos.significativo ? '✅ Significativo (p < 0.05)' : '❌ No significativo (p ≥ 0.05)'}
                    </span>
                </div>
                <div style="margin-top: 15px; padding: 10px; background: #ffffffff; border-left: 4px solid #b8b8b8ff; border-radius: 5px;">
                    <ul style="margin: 0; font-size: 13px; color: #000000ff;">
                        ${datos.interpretacion}
                    </ul>
                </div>

            </div>

        `;
    }
    
    html += `
        </div>
        

    `;
    
    container.innerHTML = html;
}

// ============================================
// FUNCIONES DE GRÁFICOS (Chart.js)
// ============================================

function updateCharts(data) {
    const viz = data.visualizacion;
    
    // Destruir gráficos existentes para evitar memory leaks
    if (scoresChart) scoresChart.destroy();
    if (maquetasChart) maquetasChart.destroy();
    if (scatterChart) scatterChart.destroy();
    if (trendChart) trendChart.destroy();
    
    // Gráfico de distribución de puntajes
    const ctx1 = document.getElementById('scoresChart').getContext('2d');
    const labels = Object.keys(viz.distribucion_puntajes).map(k => `Puntaje ${k}`);
    const values = Object.values(viz.distribucion_puntajes);

    scoresChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad de Estudiantes',
                data: values,
                backgroundColor: [
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(23, 162, 184, 0.7)',
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(40, 167, 69, 0.9)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    // Gráfico por maqueta
    const ctx2 = document.getElementById('maquetasChart').getContext('2d');
    const maquetas = Object.keys(viz.puntajes_por_maqueta);
    const puntajes_maqueta = Object.values(viz.puntajes_por_maqueta);

    const coloresMaquetas = puntajes_maqueta.map(puntaje => {
        if (puntaje >= 5.5) return 'rgba(40, 167, 69, 0.8)';
        else if (puntaje >= 4) return 'rgba(23, 162, 184, 0.8)';
        else return 'rgba(220, 53, 69, 0.8)';
    });

    maquetasChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: maquetas,
            datasets: [{
                label: 'Promedio de Puntaje',
                data: puntajes_maqueta,
                backgroundColor: coloresMaquetas,
                borderColor: coloresMaquetas.map(c => c.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 8,
                barPercentage: 0.7
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `Puntaje: ${context.parsed.x.toFixed(2)} / 7`
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 7,
                    ticks: { stepSize: 1 },
                    title: {
                        display: true,
                        text: 'Puntaje Promedio (0-7)',
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });

    // Scatter plot Tiempo vs Puntaje
    const ctx3 = document.getElementById('scatterChart').getContext('2d');
    const scatterData = viz.scatter_tiempo_puntaje;
    const datasets = {};
    
    scatterData.tiempo.forEach((t, i) => {
        const maqueta = scatterData.maqueta[i];
        const estudianteNombre = scatterData.estudiante ? scatterData.estudiante[i] : 'Estudiante';
        
        if (!datasets[maqueta]) {
            datasets[maqueta] = {
                label: maqueta,
                data: [],
                backgroundColor: maqueta.includes('Motor') ? 'rgba(255, 99, 132, 0.6)' : 'rgba(54, 162, 235, 0.6)'
            };
        }
        datasets[maqueta].data.push({ 
            x: t, 
            y: scatterData.puntaje[i],
            estudiante: estudianteNombre
        });
    });

    // Calcular regresión lineal
    const allX = scatterData.tiempo;
    const allY = scatterData.puntaje;
    const n = allX.length;
    const sumX = allX.reduce((a, b) => a + b, 0);
    const sumY = allY.reduce((a, b) => a + b, 0);
    const sumXY = allX.reduce((sum, x, i) => sum + x * allY[i], 0);
    const sumX2 = allX.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Crear línea de regresión (inicialmente oculta)
    const minX = Math.min(...allX);
    const maxX = Math.max(...allX);
    const regressionLine = {
        label: 'Regresión Lineal',
        data: [
            { x: minX, y: slope * minX + intercept },
            { x: maxX, y: slope * maxX + intercept }
        ],
        type: 'line',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 3,
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        hidden: true // Inicialmente oculta
    };

    const allDatasets = [...Object.values(datasets), regressionLine];

    scatterChart = new Chart(ctx3, {
        type: 'scatter',
        data: { datasets: allDatasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const tiempo = context.parsed.x;
                            const puntaje = context.parsed.y;
                            const minutes = Math.floor(tiempo / 60);
                            const seconds = Math.floor(tiempo % 60);
                            const tiempoFormateado = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                            
                            // Obtener nombre del estudiante del punto de datos
                            let estudianteNombre = 'Estudiante';
                            if (context.raw && context.raw.estudiante) {
                                estudianteNombre = context.raw.estudiante;
                            }
                            
                            // Formatear nombre: "Nombre Apellido" -> "Nombre A."
                            const formatearNombre = (nombreCompleto) => {
                                const partes = nombreCompleto.trim().split(' ');
                                if (partes.length === 1) {
                                    return partes[0];
                                }
                                const nombre = partes[0];
                                const inicialApellido = partes[partes.length - 1].charAt(0).toUpperCase();
                                return `${nombre} ${inicialApellido}.`;
                            };
                            
                            const nombreFormateado = formatearNombre(estudianteNombre);
                            
                            return [
                                `${nombreFormateado}`,
                                `Tiempo: ${tiempoFormateado}`,
                                `Puntaje: ${puntaje.toFixed(2)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'Tiempo (mm:ss)' }, 
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            const minutes = Math.floor(value / 60);
                            const seconds = Math.floor(value % 60);
                            return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                        },
                        stepSize: 20 // Incrementos de 20 segundos
                    }
                },
                y: { 
                    title: { display: true, text: 'Puntaje' }, 
                    beginAtZero: true,
                    min: 0, 
                    max: 7, 
                    ticks: { stepSize: 1 } 
                }
            }
        }
    });

    // Tendencia temporal
    const ctx4 = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctx4, {
        type: 'line',
        data: {
            labels: viz.tendencia_temporal.fechas,
            datasets: [{
                label: 'Puntaje Promedio',
                data: viz.tendencia_temporal.puntajes,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 7, ticks: { stepSize: 1 } }
            }
        }
    });
}

// ============================================
// FUNCIONES DE TABLAS
// ============================================

function updateRiskTable(students) {
    const tbody = document.getElementById('risk-tbody');
    tbody.innerHTML = '';

    if (!students || students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #28a745;">✅ No hay estudiantes en riesgo</td></tr>';
        return;
    }

    students.forEach(student => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${student.estudiante_nombre}</td>
            <td class="risk">${student.puntaje_mean ? student.puntaje_mean.toFixed(2) : 'N/A'}</td>
            <td>${student.tiempo_mean ? formatearTiempo(student.tiempo_mean) : 'N/A'}</td>
            <td class="risk">⚠️ ${student.motivo_riesgo || 'Requiere atención'}</td>
        `;
    });
}

function updateRankingTable(ranking) {
    const tbody = document.getElementById('ranking-tbody');
    tbody.innerHTML = '';

    if (!ranking || ranking.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No hay datos de ranking</td></tr>';
        return;
    }

    ranking.forEach((student, index) => {
        const row = tbody.insertRow();
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
        
        row.innerHTML = `
            <td>${medal} ${index + 1}</td>
            <td>${student.estudiante_nombre}</td>
            <td class="good">${student.puntaje.toFixed(2)}</td>
            <td>${formatearTiempo(student.tiempo_segundos)}</td>
            <td class="good">${student.puntuacion_final.toFixed(2)}</td>
        `;
    });
}

// ============================================
// FUNCIONES DE MODAL MAQUETAS
// ============================================

const verResultadosPorMaqueta = debounce(async function() {
    showLoading('Cargando maquetas...');
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        if (!data.estadisticas || !data.estadisticas.general || data.estadisticas.general.total_sesiones === 0) {
            hideLoading();
            showToast('No hay datos disponibles para mostrar', 'warning');
            return;
        }

        const sesionesResponse = await fetch('/api/sesiones-todas');
        const sesionesData = await sesionesResponse.json();
        todasSesiones = sesionesData.sesiones || [];

        maquetasDisponibles = [...new Set(todasSesiones.map(s => s.maqueta))];

        document.getElementById('maquetaModal').style.display = 'block';
        
        const select = document.getElementById('maquetaSelect');
        select.innerHTML = '<option value="">Selecciona una maqueta...</option>';
        maquetasDisponibles.forEach(maqueta => {
            const option = document.createElement('option');
            option.value = maqueta;
            option.textContent = maqueta;
            select.appendChild(option);
        });

        hideLoading();

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showToast('Error al cargar datos de maquetas', 'error');
    }
}, CONFIG.DEBOUNCE_DELAY);

function cerrarModalMaqueta() {
    document.getElementById('maquetaModal').style.display = 'none';
}

function filtrarPorMaqueta() {
    showLoading('Filtrando datos...');
    const maquetaSeleccionada = document.getElementById('maquetaSelect').value;
    const estudianteFilter = document.getElementById('estudianteFilterInput').value.toLowerCase().trim();
    
    if (!maquetaSeleccionada) {
        hideLoading();
        document.getElementById('maquetaResultados').innerHTML = '<div class="no-data">Por favor selecciona una maqueta</div>';
        return;
    }

    // Filtrar por maqueta
    let sesionesFiltradas = todasSesiones.filter(s => s.maqueta === maquetaSeleccionada);
    
    // Filtrar por estudiante (opcional)
    if (estudianteFilter) {
        sesionesFiltradas = sesionesFiltradas.filter(s => 
            s.estudiante_nombre.toLowerCase().includes(estudianteFilter)
        );
    }
    
    // Filtrar por aprobación/reprobación
    if (filtroAprobacion === 'aprobados') {
        sesionesFiltradas = sesionesFiltradas.filter(s => s.puntaje >= 4.0);
    } else if (filtroAprobacion === 'reprobados') {
        sesionesFiltradas = sesionesFiltradas.filter(s => s.puntaje < 4.0);
    }

    if (sesionesFiltradas.length === 0) {
        hideLoading();
        let mensaje = 'No hay sesiones';
        if (filtroAprobacion === 'aprobados') mensaje += ' de estudiantes aprobados';
        if (filtroAprobacion === 'reprobados') mensaje += ' de estudiantes reprobados';
        if (estudianteFilter) mensaje += ` del estudiante "${estudianteFilter}"`;
        mensaje += ' para esta maqueta';
        document.getElementById('maquetaResultados').innerHTML = `<div class="no-data">${mensaje}</div>`;
        return;
    }

    const totalSesiones = sesionesFiltradas.length;
    const puntajes = sesionesFiltradas.map(s => s.puntaje);
    const tiempos = sesionesFiltradas.map(s => s.tiempo_segundos);
    
    const promedioPuntaje = (puntajes.reduce((a, b) => a + b, 0) / totalSesiones).toFixed(2);
    const promedioTiempoSegundos = tiempos.reduce((a, b) => a + b, 0) / totalSesiones;
    const promedioTiempo = formatearTiempo(promedioTiempoSegundos);
    const mejorPuntaje = Math.max(...puntajes).toFixed(2);
    const peorPuntaje = Math.min(...puntajes).toFixed(2);
    const estudiantesUnicos = [...new Set(sesionesFiltradas.map(s => s.estudiante_nombre))].length;
    
    // Calcular estadísticas de clasificación binaria
    const aprobados = sesionesFiltradas.filter(s => s.puntaje >= 4.0).length;
    const reprobados = sesionesFiltradas.filter(s => s.puntaje < 4.0).length;
    const tasaAprobacion = ((aprobados / totalSesiones) * 100).toFixed(1);

    let html = `
        ${estudianteFilter || filtroAprobacion !== 'todos' ? `
        <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">🔍</span>
                <div>
                    <strong style="color: #1976D2;">Filtros activos:</strong>
                    <span style="color: #333;">
                        ${estudianteFilter ? ` Estudiante "${estudianteFilter}"` : ''}
                        ${filtroAprobacion === 'aprobados' ? ' | ✅ Solo Aprobados (≥4.0)' : ''}
                        ${filtroAprobacion === 'reprobados' ? ' | ❌ Solo Reprobados (<4.0)' : ''}
                    </span>
                </div>
            </div>
        </div>
        ` : ''}
        
        <!-- Estadísticas de Clasificación Binaria -->
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="color: #667eea; margin-bottom: 12px;">🤖 Clasificación Binaria (Aprobación)</h4>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: white; padding: 12px; border-radius: 8px; text-align: center; border-left: 4px solid #28a745;">
                    <div style="color: #666; font-size: 11px;">APROBADOS</div>
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">${aprobados}</div>
                    <div style="font-size: 10px; color: #999;">≥ 4.0 puntos</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 8px; text-align: center; border-left: 4px solid #dc3545;">
                    <div style="color: #666; font-size: 11px;">REPROBADOS</div>
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545;">${reprobados}</div>
                    <div style="font-size: 10px; color: #999;">< 4.0 puntos</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 8px; text-align: center; border-left: 4px solid #667eea;">
                    <div style="color: #666; font-size: 11px;">TASA APROBACIÓN</div>
                    <div style="font-size: 24px; font-weight: bold; color: #667eea;">${tasaAprobacion}%</div>
                    <div style="font-size: 10px; color: #999;">del total</div>
                </div>
            </div>
        </div>
        
        <div class="maqueta-stats">
            <div class="maqueta-stat-card">
                <h4>TOTAL SESIONES</h4>
                <div class="value">${totalSesiones}</div>
            </div>
            <div class="maqueta-stat-card">
                <h4>ESTUDIANTES</h4>
                <div class="value">${estudiantesUnicos}</div>
            </div>
            <div class="maqueta-stat-card">
                <h4>PROMEDIO PUNTAJE</h4>
                <div class="value">${promedioPuntaje}</div>
            </div>

        </div>
        <div class="maqueta-stats">
            <div class="maqueta-stat-card">
                <h4>MEJOR PUNTAJE</h4>
            <div class="value">${mejorPuntaje}</div>
            </div>
            <div class="maqueta-stat-card">
                <h4>PEOR PUNTAJE</h4>
                <div class="value">${peorPuntaje}</div>
            </div>
            <div class="maqueta-stat-card">
                <h4>TIEMPO PROMEDIO</h4>
                <div class="value">${promedioTiempo}</div>
            </div>
        </div>
        <div class="sessions-table">
            <h3>Detalle de Sesiones</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Estudiante</th>
                        <th>Puntaje</th>
                        <th>Tiempo</th>
                        <th>IA Usada</th>
                    </tr>
                </thead>
                <tbody>
                    ${sesionesFiltradas.map(sesion => `
                        <tr>
                            <td>${new Date(sesion.fecha).toLocaleDateString('es-ES')}</td>
                            <td>${sesion.estudiante_nombre}</td>
                            <td class="${sesion.puntaje >= 4 ? 'good' : 'risk'}">${sesion.puntaje.toFixed(2)}</td>
                            <td>${formatearTiempo(sesion.tiempo_segundos)}</td>
                            <td>${sesion.interacciones_ia} veces</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    document.getElementById('maquetaResultados').innerHTML = html;
    hideLoading();
}

// ============================================
// FUNCIONES DE REGRESIÓN
// ============================================

let filtroAprobacion = 'todos'; // Variable global para el filtro de aprobación

/**
 * Muestra análisis de regresión simple (Puntaje vs Tiempo)
 */
async function mostrarRegresionSimple() {
    showLoading('Calculando regresión simple...');
    
    try {
        const response = await fetch('/api/regresion-simple');
        const data = await response.json();
        
        if (!data.success) {
            hideLoading();
            showToast('No hay suficientes datos para regresión simple', 'warning');
            return;
        }
        
        const container = document.getElementById('prediction-content');
        const r2_pct = (data.r2_score * 100).toFixed(1);
        const r2_color = data.r2_score > 0.7 ? '#28a745' : data.r2_score > 0.4 ? '#ffc107' : '#dc3545';
        
        container.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #667eea; margin-bottom: 15px;">📈 Regresión Lineal Simple</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #666; font-size: 12px;">Precisión del Modelo (R²)</div>
                        <div style="font-size: 32px; font-weight: bold; color: ${r2_color};">${r2_pct}%</div>
                        <div style="font-size: 11px; color: #999;">${data.precision}</div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #666; font-size: 12px;">Error Medio (MAE)</div>
                        <div style="font-size: 32px; font-weight: bold; color: #667eea;">${data.mae.toFixed(2)}</div>
                        <div style="font-size: 11px; color: #999;">puntos de diferencia</div>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h5 style="color: #333; margin-bottom: 10px;">🔢 Ecuación del Modelo:</h5>
                    <div style="font-family: 'Courier New', monospace; font-size: 14px; background: white; padding: 12px; border-radius: 5px; border-left: 4px solid #667eea;">
                        ${data.formula}
                    </div>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 5px;">
                    <strong style="color: #856404;">💡 Interpretación:</strong>
                    <p style="margin: 8px 0 0 0; color: #856404; font-size: 13px;">${data.interpretacion}</p>
                </div>
                
                <div style="margin-top: 15px; padding: 12px; background: white; border-radius: 8px; border: 2px solid #e0e0e0;">
                    <strong style="color: #333;">📊 Variables del Modelo:</strong>
                    <ul style="margin: 8px 0 0 20px; color: #666; font-size: 13px;">
                        <li><strong>Variable independiente (X):</strong> Tiempo en VR (segundos)</li>
                        <li><strong>Variable dependiente (Y):</strong> Puntaje en laboratorio (0-7)</li>
                        <li><strong>Muestras analizadas:</strong> ${data.n_samples} sesiones</li>
                    </ul>
                </div>
            </div>
        `;
        
        hideLoading();
        showToast('Regresión simple calculada exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al calcular regresión simple:', error);
        hideLoading();
        showToast('Error al calcular regresión simple', 'error');
    }
}

/**
 * Muestra análisis de regresión múltiple (Tiempo + Intentos + Complejidad)
 */
async function mostrarRegresionMultiple() {
    showLoading('Calculando regresión múltiple...');
    
    try {
        const response = await fetch('/api/regresion-multiple');
        const data = await response.json();
        
        if (!data.success) {
            hideLoading();
            showToast('No hay suficientes datos para regresión múltiple', 'warning');
            return;
        }
        
        const container = document.getElementById('prediction-content');
        const r2_pct = (data.r2_score * 100).toFixed(1);
        const r2_color = data.r2_score > 0.7 ? '#28a745' : data.r2_score > 0.4 ? '#ffc107' : '#dc3545';
        
        container.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #667eea; margin-bottom: 15px;">📊 Regresión Lineal Múltiple</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #666; font-size: 12px;">Precisión (R²)</div>
                        <div style="font-size: 28px; font-weight: bold; color: ${r2_color};">${r2_pct}%</div>
                        <div style="font-size: 11px; color: #999;">${data.precision}</div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #666; font-size: 12px;">Error Medio</div>
                        <div style="font-size: 28px; font-weight: bold; color: #667eea;">${data.mae.toFixed(2)}</div>
                        <div style="font-size: 11px; color: #999;">MAE</div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #666; font-size: 12px;">Variables</div>
                        <div style="font-size: 28px; font-weight: bold; color: #764ba2;">${data.n_features}</div>
                        <div style="font-size: 11px; color: #999;">predictoras</div>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h5 style="color: #333; margin-bottom: 10px;">🔢 Ecuación del Modelo:</h5>
                    <div style="font-family: 'Courier New', monospace; font-size: 13px; background: white; padding: 12px; border-radius: 5px; border-left: 4px solid #667eea;">
                        ${data.formula}
                    </div>
                </div>
                
                <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 12px; border-radius: 5px; margin-bottom: 15px;">
                    <strong style="color: #1976D2;">📈 Coeficientes del Modelo:</strong>
                    <div style="margin-top: 10px; display: grid; gap: 8px;">
                        ${data.coeficientes.map(coef => `
                            <div style="background: white; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #333; font-weight: 500;">${coef.variable}</span>
                                <span style="color: #667eea; font-weight: bold; font-family: monospace;">${coef.valor > 0 ? '+' : ''}${coef.valor}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 5px; margin-bottom: 15px;">
                    <strong style="color: #856404;">💡 Interpretación:</strong>
                    <p style="margin: 8px 0 0 0; color: #856404; font-size: 13px;">${data.interpretacion}</p>
                </div>
                
                <div style="padding: 12px; background: white; border-radius: 8px; border: 2px solid #e0e0e0;">
                    <strong style="color: #333;">📊 Variables del Modelo:</strong>
                    <ul style="margin: 8px 0 0 20px; color: #666; font-size: 13px;">
                        <li><strong>Tiempo en VR:</strong> Duración de la sesión en segundos</li>
                        <li><strong>Número de intentos:</strong> Cantidad de interacciones con IA</li>
                        <li><strong>Nivel de complejidad:</strong> Basado en la maqueta utilizada</li>
                        <li><strong>Variable dependiente:</strong> Puntaje en laboratorio (0-7)</li>
                        <li><strong>Muestras analizadas:</strong> ${data.n_samples} sesiones</li>
                    </ul>
                </div>
            </div>
        `;
        
        hideLoading();
        showToast('Regresión múltiple calculada exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al calcular regresión múltiple:', error);
        hideLoading();
        showToast('Error al calcular regresión múltiple', 'error');
    }
}

/**
 * Filtra sesiones por estado de aprobación
 */
function filtrarPorAprobacion(tipo) {
    filtroAprobacion = tipo;
    
    // Actualizar estilos de botones
    document.getElementById('btnTodos').style.background = tipo === 'todos' ? '#667eea' : '#6c757d';
    document.getElementById('btnAprobados').style.background = tipo === 'aprobados' ? '#28a745' : '#6c757d';
    document.getElementById('btnReprobados').style.background = tipo === 'reprobados' ? '#dc3545' : '#6c757d';
    
    // Re-filtrar con el filtro de aprobación activo
    filtrarPorMaqueta();
}

/**
 * Muestra/oculta la línea de regresión lineal en el gráfico scatter
 */
function toggleRegresionLineal() {
    if (!scatterChart) return;
    
    const btn = document.getElementById('toggleRegresion');
    const regressionDataset = scatterChart.data.datasets.find(ds => ds.label === 'Regresión Lineal');
    
    if (regressionDataset) {
        regressionDataset.hidden = !regressionDataset.hidden;
        scatterChart.update();
        
        // Actualizar texto del botón
        if (regressionDataset.hidden) {
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-outline-primary');
        } else {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-warning');
        }
    }
}

// ============================================
// INICIALIZACIÓN
// ============================================

window.onload = function() {
    console.log('🚀 Dashboard VR Analytics iniciado');
    refreshData();
};
