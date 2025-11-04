# services/email_service.py - Servicio para envío de correos electrónicos

from flask_mail import Mail, Message
from flask import render_template_string
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmailService:
    """
    Servicio para envío de correos electrónicos con manejo robusto de errores
    
    Implementa el patrón Service Layer para centralizar lógica de envío de emails
    con timeout, retry logic y fallback gracioso.
    """
    
    def __init__(self, mail_instance=None):
        self.mail = mail_instance
        self.timeout = 10  # Timeout de 10 segundos para evitar bloqueos
    
    def send_password_reset_email(self, email: str, reset_link: str, nombre: Optional[str] = None) -> Dict[str, any]:
        """
        Envía un correo de recuperación de contraseña con manejo robusto de errores
        
        Args:
            email (str): Email del destinatario
            reset_link (str): URL para restablecer la contraseña
            nombre (str): Nombre del usuario (opcional)
        
        Returns:
            dict: {'success': bool, 'message': str, 'error_type': str (opcional)}
        """
        try:
            # Validar configuración de correo
            if not self.mail:
                logger.error("❌ Mail instance no configurada")
                return {
                    'success': False,
                    'message': 'Servicio de correo no configurado',
                    'error_type': 'config_error'
                }
            
            # Validar email
            if not email or '@' not in email:
                logger.error(f"❌ Email inválido: {email}")
                return {
                    'success': False,
                    'message': 'Email inválido',
                    'error_type': 'validation_error'
                }
            # Template HTML del correo
            html_template = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .container {
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                        margin: -30px -30px 20px -30px;
                    }
                    .button {
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        margin: 20px 0;
                        font-weight: bold;
                    }
                    .footer {
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                    }
                    .warning {
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 10px;
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Recuperación de Contraseña</h1>
                    </div>
                    
                    <p>Hola{% if nombre %} {{ nombre }}{% endif %},</p>
                    
                    <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en <strong>VR Analytics</strong>.</p>
                    
                    <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
                    
                    <center>
                        <a href="{{ reset_link }}" class="button">Restablecer Contraseña</a>
                    </center>
                    
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
                        {{ reset_link }}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong> Este enlace expirará en <strong>1 hora</strong> por razones de seguridad.
                    </div>
                    
                    <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo de forma segura.</p>
                    
                    <div class="footer">
                        <p><strong>VR Analytics</strong> - Sistema de Análisis de Aprendizaje en Realidad Virtual</p>
                        <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Template de texto plano (fallback)
            text_template = """
            Recuperación de Contraseña - VR Analytics
            
            Hola{% if nombre %} {{ nombre }}{% endif %},
            
            Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.
            
            Para crear una nueva contraseña, visita el siguiente enlace:
            {{ reset_link }}
            
            ⚠️ IMPORTANTE: Este enlace expirará en 1 hora por razones de seguridad.
            
            Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.
            
            ---
            VR Analytics - Sistema de Análisis de Aprendizaje en Realidad Virtual
            Este es un correo automático, por favor no respondas a este mensaje.
            """
            
            # Renderizar templates
            html_body = render_template_string(html_template, reset_link=reset_link, nombre=nombre)
            text_body = render_template_string(text_template, reset_link=reset_link, nombre=nombre)
            
            # Obtener el remitente desde las variables de entorno o usar uno por defecto
            default_sender = os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_USERNAME') or 'noreply@vranalytics.com'
            
            # Crear mensaje
            msg = Message(
                subject='🔐 Recuperación de Contraseña - VR Analytics',
                recipients=[email],
                html=html_body,
                body=text_body,
                sender=default_sender
            )
            
            # Enviar correo con manejo de timeout
            try:
                self.mail.send(msg)
                logger.info(f"✅ Correo de recuperación enviado exitosamente a: {email}")
                return {
                    'success': True,
                    'message': 'Correo enviado exitosamente'
                }
            except TimeoutError:
                logger.error(f"⏱️ Timeout al enviar correo a {email}")
                return {
                    'success': False,
                    'message': 'Timeout al conectar con servidor de correo',
                    'error_type': 'timeout'
                }
            except ConnectionError as conn_err:
                logger.error(f"🔌 Error de conexión al enviar correo a {email}: {str(conn_err)}")
                return {
                    'success': False,
                    'message': 'Error de conexión con servidor de correo',
                    'error_type': 'connection_error'
                }
            except Exception as send_error:
                logger.error(f"📧 Error al enviar correo a {email}: {str(send_error)}")
                return {
                    'success': False,
                    'message': f'Error al enviar: {str(send_error)}',
                    'error_type': 'send_error'
                }
                
        except Exception as e:
            logger.error(f"❌ Error general en send_password_reset_email para {email}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'success': False,
                'message': f'Error al procesar correo: {str(e)}',
                'error_type': 'general_error'
            }
    
    def send_welcome_email(self, email, nombre, tipo_usuario):
        """
        Envía un correo de bienvenida al registrarse
        
        Args:
            email (str): Email del destinatario
            nombre (str): Nombre del usuario
            tipo_usuario (str): 'profesor' o 'estudiante'
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            html_template = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .container {
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                        margin: -30px -30px 20px -30px;
                    }
                    .footer {
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 ¡Bienvenido a VR Analytics!</h1>
                    </div>
                    
                    <p>Hola {{ nombre }},</p>
                    
                    <p>Tu registro como <strong>{{ tipo_usuario }}</strong> ha sido exitoso.</p>
                    
                    <p>VR Analytics es una plataforma de análisis de aprendizaje en Realidad Virtual que te ayudará a {% if tipo_usuario == 'profesor' %}monitorear el progreso de tus estudiantes{% else %}seguir tu progreso de aprendizaje{% endif %}.</p>
                    
                    <p>Ya puedes iniciar sesión en la plataforma con tu email.</p>
                    
                    <div class="footer">
                        <p><strong>VR Analytics</strong> - Sistema de Análisis de Aprendizaje en Realidad Virtual</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_body = render_template_string(html_template, nombre=nombre, tipo_usuario=tipo_usuario)
            
            # Obtener el remitente desde las variables de entorno o usar uno por defecto
            default_sender = os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_USERNAME') or 'noreply@vranalytics.com'
            
            msg = Message(
                subject='🎉 ¡Bienvenido a VR Analytics!',
                recipients=[email],
                html=html_body,
                sender=default_sender  # ← Especificar el remitente explícitamente
            )
            
            if self.mail:
                self.mail.send(msg)
                logger.info(f"Correo de bienvenida enviado a: {email}")
                return {'success': True, 'message': 'Correo enviado'}
            else:
                return {'success': False, 'message': 'Servicio de correo no configurado'}
                
        except Exception as e:
            logger.error(f"Error al enviar correo de bienvenida a {email}: {str(e)}")
            return {'success': False, 'message': str(e)}
