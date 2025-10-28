// ============================================
// BOT DETECTION - Frontend Tracking
// ============================================

/**
 * Sistema de detección de comportamiento humano en el frontend.
 * Envía señales al backend para determinar si mostrar reCAPTCHA.
 */

class BehaviorTracker {
    constructor() {
        this.startTime = Date.now();
        this.mouseMovements = 0;
        this.keystrokes = 0;
        this.focusEvents = 0;
        this.scrollEvents = 0;
        
        this.init();
    }
    
    init() {
        // Marcar que JS está habilitado
        this.pingJavaScriptEnabled();
        
        // Registrar tiempo de inicio del formulario
        this.markFormStart();
        
        // Trackear eventos humanos
        this.trackMouseMovement();
        this.trackKeystrokes();
        this.trackFocus();
        this.trackScroll();
    }
    
    /**
     * Notifica al servidor que JavaScript está habilitado
     */
    async pingJavaScriptEnabled() {
        try {
            await fetch('/api/js-enabled', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
        } catch (error) {
            console.error('Error notificando JS habilitado:', error);
        }
    }
    
    /**
     * Marca el inicio del llenado del formulario
     */
    async markFormStart() {
        try {
            await fetch('/api/form-start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
        } catch (error) {
            console.error('Error marcando inicio de formulario:', error);
        }
    }
    
    /**
     * Trackea movimiento del mouse (humanos mueven el mouse)
     */
    trackMouseMovement() {
        let lastMove = 0;
        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (now - lastMove > 100) {  // Throttle
                this.mouseMovements++;
                lastMove = now;
            }
        });
    }
    
    /**
     * Trackea teclas presionadas
     */
    trackKeystrokes() {
        document.addEventListener('keydown', () => {
            this.keystrokes++;
        });
    }
    
    /**
     * Trackea eventos de focus en inputs
     */
    trackFocus() {
        document.querySelectorAll('input, textarea').forEach(input => {
            input.addEventListener('focus', () => {
                this.focusEvents++;
            });
        });
    }
    
    /**
     * Trackea scroll (bots generalmente no scrollean)
     */
    trackScroll() {
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const now = Date.now();
            if (now - lastScroll > 100) {  // Throttle
                this.scrollEvents++;
                lastScroll = now;
            }
        });
    }
    
    /**
     * Calcula un score de comportamiento humano (0-100)
     * Mientras más alto, más humano
     */
    getHumanScore() {
        let score = 0;
        
        // Tiempo en página (más de 5 segundos es bueno)
        const timeSpent = (Date.now() - this.startTime) / 1000;
        if (timeSpent > 5) score += 20;
        if (timeSpent > 10) score += 10;
        
        // Movimiento de mouse
        if (this.mouseMovements > 10) score += 20;
        if (this.mouseMovements > 50) score += 10;
        
        // Keystrokes (tipeo natural)
        if (this.keystrokes > 5) score += 15;
        if (this.keystrokes > 20) score += 10;
        
        // Focus events
        if (this.focusEvents > 1) score += 10;
        
        // Scroll
        if (this.scrollEvents > 0) score += 15;
        
        return Math.min(score, 100);
    }
    
    /**
     * Determina si debemos mostrar reCAPTCHA
     */
    shouldShowCaptcha() {
        const humanScore = this.getHumanScore();
        const timeSpent = (Date.now() - this.startTime) / 1000;
        
        // Si llenó muy rápido (< 3 seg) y score bajo = bot probable
        if (timeSpent < 3 && humanScore < 40) {
            return true;
        }
        
        // Si score muy bajo = sospechoso
        if (humanScore < 30) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Obtiene datos de comportamiento para enviar al backend
     */
    getBehaviorData() {
        return {
            human_score: this.getHumanScore(),
            time_spent: (Date.now() - this.startTime) / 1000,
            mouse_movements: this.mouseMovements,
            keystrokes: this.keystrokes,
            focus_events: this.focusEvents,
            scroll_events: this.scrollEvents
        };
    }
}

// Inicializar tracker global
const behaviorTracker = new BehaviorTracker();

/**
 * Helper: Decide si mostrar reCAPTCHA antes de submit
 */
async function shouldRequireCaptcha() {
    // Análisis local (frontend)
    const localCheck = behaviorTracker.shouldShowCaptcha();
    
    if (localCheck) {
        console.warn('⚠️ Comportamiento sospechoso detectado localmente');
        return true;
    }
    
    // Consultar al backend
    try {
        const response = await fetch('/api/captcha-check', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(behaviorTracker.getBehaviorData())
        });
        
        const data = await response.json();
        
        if (data.show_captcha) {
            console.warn('⚠️ Backend requiere reCAPTCHA:', data.reason);
            return true;
        }
        
        return false;
        
    } catch (error) {
        console.error('Error consultando captcha requirement:', error);
        // En caso de error, no bloquear al usuario
        return false;
    }
}

/**
 * Muestra el widget de reCAPTCHA dinámicamente
 */
function showCaptchaWidget() {
    const captchaContainer = document.getElementById('captcha-container');
    if (captchaContainer) {
        captchaContainer.style.display = 'block';
        captchaContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Oculta el widget de reCAPTCHA
 */
function hideCaptchaWidget() {
    const captchaContainer = document.getElementById('captcha-container');
    if (captchaContainer) {
        captchaContainer.style.display = 'none';
    }
}

// Exportar para uso global
window.behaviorTracker = behaviorTracker;
window.shouldRequireCaptcha = shouldRequireCaptcha;
window.showCaptchaWidget = showCaptchaWidget;
window.hideCaptchaWidget = hideCaptchaWidget;
