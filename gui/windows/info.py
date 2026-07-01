#info.py


INFO_CONTENTS = """
            <h2>Funcionalidades de la aplicación</h2>
            <p><b>1. Monitorización:</b> Pulsar los botones de "Vista" permite alternar entre la evolución de la potencia en tiempo real, la evolución del consumo energético y las métricas del entrenamiento de ML. La opción "Resetear" permite reiniciar visualmente las gráficas de potencia y consumo energético.</p>
            <p><b>2. Registros:</b> El sistema almacena automáticamente en ficheros CSV automáticamente los datos de consumo y los resultados del entrenamiento en la carpeta <i>/Training Metrics</i>. Pulsando el boton "Visualizar Históricos" y seleccionando los CSV de consumo y métricas registrados previamente, se pueden correlacionar ambos sobre una gráfica para análisis de resultados y toma de decisiones.</p>
            <p>El sistema muestra en la pantalla de la terminal la información relevante de la ejecución, como la gestión de hilos y conexión con los otros nodos del sistema. Es posible almacenar esta información usando la opcion de "Exportar Logs".</p>
            <p><b>3. Config y ayuda:</b> "Reconfigurar" permite acceder de nuevo a la ventana de configuración inicial para reintroducir las credenciales en caso de haber ocurrido algún fallo que lo requiera.</p>
            <p><b>4. Umbrales y alertas:</b> En esta sección se permite la configuración dinámita de umbrales de potencia, consumo energético y baseline de potencia. El sistema alertará sobre excesos producidos sobre los dos primeros.</b> </p>
            <p>Adicionalmente, "Configurar Early Stopping" permite la creación de reglas dinámicas para la aplicación de la parada temprana del entrenamiento a través de alertas. En caso de producirse una alerta se dará al usuario la posibilidad de decidir si parar o no el entrenamiento.</b> </p>

            <hr>
            <p><small>Desarrollado para la monitorización energética de modelos de Machine Learning.</small></p>
        """