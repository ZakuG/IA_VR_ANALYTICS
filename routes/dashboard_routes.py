"""
📊 Dashboard Routes - Blueprint de Dashboards
==============================================

Rutas para dashboards:
- Dashboard Profesor (con analytics)
- Dashboard Estudiante (vista personal)
- Manual Entry (ingreso manual de sesiones)

Patrón: MVC con decoradores de autenticación
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import Profesor, Estudiante

# Crear blueprint
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal - Redirige según tipo de usuario.
    
    - Profesor: Dashboard con analytics y gráficos
    - Estudiante: Dashboard personal con progreso
    
    Returns:
        Template HTML renderizado
    """
    if isinstance(current_user, Profesor):
        return render_template('dashboard.html', profesor=current_user)
    elif isinstance(current_user, Estudiante):
        return render_template('dashboard_estudiante.html', estudiante=current_user)
    else:
        return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard-estudiante')
@login_required
def dashboard_estudiante():
    """
    Dashboard del estudiante (ruta alternativa).
    
    Returns:
        Template HTML del dashboard estudiante
    """
    if not isinstance(current_user, Estudiante):
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('dashboard_estudiante.html', estudiante=current_user)


@dashboard_bp.route('/dashboard/manual-entry')
@login_required
def manual_entry():
    """
    Página para registro manual de sesiones.
    
    Solo accesible para profesores.
    
    Returns:
        Template HTML de ingreso manual
        Redirect: Si no es profesor
    """
    if not isinstance(current_user, Profesor):
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('manual_entry.html', profesor=current_user)
