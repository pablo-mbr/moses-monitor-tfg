# MOSES

Aplicación de escritorio para la aplicación de Early Stopping y optimización de precisión y consumo energético de entrenamientos de Machine y Deep learning.

## Requisitos de hardware

- Enchufe inteligente **TP-Link Tapo P110/115** conectado a la red 
- Cuenta Tapo vinculada al dispositivo

## Requisitos de software

- Python 3.11+
- [Mosquitto MQTT Broker](https://mosquitto.org/download/) (Windows)

## Instalación

1. Clona el repositorio e instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Descarga e instala **Mosquitto** desde [mosquitto.org/download](https://mosquitto.org/download/). Copia el contenido de la instalación en `moses-tfg/Mosquitto/`.

3. Asegúrate de que `moses-tfg/Mosquitto/mosquitto.conf` existe con:

```
listener 1883 0.0.0.0
allow_anonymous true
persistence false
```

## Ejecución

```bash
python main.py
```

## Integración con el script de entrenamiento

La aplicación escucha mensajes MQTT en el topic `training/metrics` en `localhost:1883`.

El payload debe ser un JSON con la siguiente estructura:

```json
{
  "name": "",
  "timestamp": "2025-01-01T12:00:00",
  "step": 3,
  "step_type": "",
  "phase": "",
  "values": [
    {"value_name": "Loss", "value": 0.42},
    {"value_name": "Accuracy", "value": 0.87}
  ]
}
```

| Campo | Tipo                | Descripción                                                     |
|---|---------------------|-----------------------------------------------------------------|
| `name` | string              | Nombre identificativo del entrenamiento                         |
| `timestamp` | datetime ISO        | Marca temporal asociada a la producción de los valores enviados |
| `step` | int                 | Número de paso actual del entrenamiento                         |
| `step_type` | string              | Tipo de paso (`epoch`, `iteración`, etc.)                       |
| `phase` | `"train"` / `"val"` | Fase del entrenamiento a la que corresponde el envío            |
| `values` | List [MetricsValue] | Lista de métricas enviadas                                      |

| Campo        | Tipo  | Descripción                                                     |
|--------------|-------|-----------------------------------------------------------------|
| `value_name` | string | Nombre identificativo de la métrica |
| `value`      | float | Valor de la métrica

Early stopping solo actúa sobre mensajes con `phase: "val"`.

Si el early stopping detecta estancamiento, la aplicación publica una señal de parada en el topic `training/stopping`. El script de entrenamiento debe suscribirse a ese topic para detener el entrenamiento.

## Dependencias

| Paquete | Versión |
|---|---|
| PyQt6 | 6.7.1 |
| pyqtgraph | 0.13.7 |
| numpy | 1.26.4 |
| paho-mqtt | 2.1.0 |
| tapo | 0.8.5 |
