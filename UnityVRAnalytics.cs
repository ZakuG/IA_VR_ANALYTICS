// UnityVRAnalytics.cs
// Script de ejemplo para integrar con el sistema de analytics desde Unity
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Clase para enviar datos de sesiones VR al sistema de analytics
/// </summary>
public class UnityVRAnalytics : MonoBehaviour
{
    [Header("Configuración de API")]
    [Tooltip("URL del servidor Flask (cambiar si se despliega en producción)")]
    public string apiBaseUrl = "http://localhost:5000";
    
    [Header("Datos del Estudiante")]
    public string codigoEstudiante = "EST001"; // Este código debe ser registrado previamente
    
    [Header("Datos de la Sesión")]
    public string nombreMaqueta = "Aire acondicionado"; // o "Motor"
    
    private float tiempoInicio;
    private int puntajeActual = 0;
    private int interaccionesIA = 0;
    private List<RespuestaTest> respuestas = new List<RespuestaTest>();

    /// <summary>
    /// Clase para almacenar respuestas del test
    /// </summary>
    [System.Serializable]
    public class RespuestaTest
    {
        public int pregunta;
        public string respuesta;
        public bool correcta;
    }

    /// <summary>
    /// Clase para enviar datos al servidor
    /// </summary>
    [System.Serializable]
    private class SessionData
    {
        public string codigo_estudiante;
        public string maqueta;
        public int tiempo_segundos;
        public int puntaje;
        public int interacciones_ia;
        public List<RespuestaTest> respuestas;
    }

    void Start()
    {
        IniciarSesion();
    }

    /// <summary>
    /// Inicia el contador de tiempo para la sesión
    /// </summary>
    public void IniciarSesion()
    {
        tiempoInicio = Time.time;
        puntajeActual = 0;
        interaccionesIA = 0;
        respuestas.Clear();
        
        Debug.Log($"Sesión iniciada para {codigoEstudiante} en maqueta: {nombreMaqueta}");
    }

    /// <summary>
    /// Registra una interacción del estudiante con la IA
    /// </summary>
    public void RegistrarInteraccionIA()
    {
        interaccionesIA++;
        Debug.Log($"Interacciones IA: {interaccionesIA}");
    }

    /// <summary>
    /// Registra una respuesta del test
    /// </summary>
    /// <param name="numeroPregunta">Número de la pregunta (1-5)</param>
    /// <param name="respuesta">Opción seleccionada (A, B, C, D)</param>
    /// <param name="esCorrecta">Si la respuesta es correcta</param>
    public void RegistrarRespuesta(int numeroPregunta, string respuesta, bool esCorrecta)
    {
        RespuestaTest resp = new RespuestaTest
        {
            pregunta = numeroPregunta,
            respuesta = respuesta,
            correcta = esCorrecta
        };
        
        respuestas.Add(resp);
        
        if (esCorrecta)
        {
            puntajeActual++;
        }
        
        Debug.Log($"Respuesta registrada - Pregunta {numeroPregunta}: {respuesta} ({(esCorrecta ? "Correcta" : "Incorrecta")})");
        Debug.Log($"Puntaje actual: {puntajeActual}/5");
    }

    /// <summary>
    /// Finaliza la sesión y envía los datos al servidor
    /// </summary>
    public void FinalizarYEnviarSesion()
    {
        int tiempoTotal = Mathf.RoundToInt(Time.time - tiempoInicio);
        
        Debug.Log($"=== RESUMEN DE SESIÓN ===");
        Debug.Log($"Estudiante: {codigoEstudiante}");
        Debug.Log($"Maqueta: {nombreMaqueta}");
        Debug.Log($"Tiempo: {tiempoTotal} segundos ({tiempoTotal/60f:F2} minutos)");
        Debug.Log($"Puntaje: {puntajeActual}/5");
        Debug.Log($"Interacciones IA: {interaccionesIA}");
        Debug.Log($"========================");
        
        StartCoroutine(EnviarResultados(tiempoTotal));
    }

    /// <summary>
    /// Envía los resultados al servidor mediante POST request
    /// </summary>
    private IEnumerator EnviarResultados(int tiempoSegundos)
    {
        SessionData data = new SessionData
        {
            codigo_estudiante = codigoEstudiante,
            maqueta = nombreMaqueta,
            tiempo_segundos = tiempoSegundos,
            puntaje = puntajeActual,
            interacciones_ia = interaccionesIA,
            respuestas = respuestas
        };

        string jsonData = JsonUtility.ToJson(data);
        string url = apiBaseUrl + "/api/unity/session";
        
        Debug.Log($"Enviando datos a: {url}");
        Debug.Log($"JSON: {jsonData}");

        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("✅ Resultados enviados correctamente al servidor");
            Debug.Log($"Respuesta: {request.downloadHandler.text}");
            
            // Aquí puedes mostrar un mensaje al usuario
            MostrarMensajeExito();
        }
        else
        {
            Debug.LogError($"❌ Error al enviar resultados: {request.error}");
            Debug.LogError($"Código de respuesta: {request.responseCode}");
            
            // Aquí puedes intentar reenviar o guardar localmente
            MostrarMensajeError();
        }
    }

    /// <summary>
    /// Muestra mensaje de éxito al usuario (implementar UI)
    /// </summary>
    private void MostrarMensajeExito()
    {
        // TODO: Implementar UI para mostrar mensaje
        Debug.Log("Datos enviados exitosamente. El profesor podrá ver tu progreso.");
    }

    /// <summary>
    /// Muestra mensaje de error al usuario (implementar UI)
    /// </summary>
    private void MostrarMensajeError()
    {
        // TODO: Implementar UI para mostrar mensaje
        Debug.LogWarning("No se pudieron enviar los datos. Verifica tu conexión.");
    }

    // ===== MÉTODOS DE EJEMPLO PARA USAR EN TU JUEGO =====

    /// <summary>
    /// Ejemplo de uso cuando el estudiante pregunta a la IA
    /// </summary>
    public void OnPreguntaAIA()
    {
        // Llamar cuando el estudiante interactúa con el chatbot IA
        RegistrarInteraccionIA();
    }

    /// <summary>
    /// Ejemplo de uso cuando el estudiante responde una pregunta del test
    /// </summary>
    public void OnRespuestaTest(int numeroPregunta, string opcionSeleccionada, string respuestaCorrecta)
    {
        bool esCorrecta = opcionSeleccionada == respuestaCorrecta;
        RegistrarRespuesta(numeroPregunta, opcionSeleccionada, esCorrecta);
        
        // Si es la última pregunta, finalizar
        if (numeroPregunta == 5)
        {
            FinalizarYEnviarSesion();
        }
    }
}

// ===== EJEMPLO DE USO =====
/*
 * En tu script de control del juego VR:
 * 
 * 1. Agregar este script a un GameObject (por ejemplo, GameManager)
 * 
 * 2. Al iniciar la maqueta:
 *    vrAnalytics = GetComponent<UnityVRAnalytics>();
 *    vrAnalytics.codigoEstudiante = "EST001"; // Obtener del login
 *    vrAnalytics.nombreMaqueta = "Motor";
 *    vrAnalytics.IniciarSesion();
 * 
 * 3. Cuando el estudiante usa la IA:
 *    vrAnalytics.RegistrarInteraccionIA();
 * 
 * 4. Cuando responde una pregunta del test:
 *    vrAnalytics.OnRespuestaTest(1, "A", "A"); // Pregunta 1, seleccionó A, correcta es A
 *    vrAnalytics.OnRespuestaTest(2, "B", "C"); // Pregunta 2, seleccionó B, correcta es C
 *    // ... etc
 * 
 * 5. Al terminar (automático en pregunta 5) o manualmente:
 *    vrAnalytics.FinalizarYEnviarSesion();
 */
