import json

import paho.mqtt.client as mqtt
from log_types import LogType
from core.communication.dto.metrics_dto import MetricsDto
from gui.components.terminal import Terminal


def on_connect(client, window, flags, rc):
    if rc == 0:
        Terminal().log("[RECEPTOR] Conectado al broker local.", LogType.SUCCESS)
        client.subscribe("training/metrics")
        Terminal().log("[RECEPTOR] Suscrito al topic.", LogType.SUCCESS)
    else:
        Terminal().log(f"[RECEPTOR] Error en la conexión. Código {rc}.", LogType.ERROR)


def on_message(client, window, msg):
    try:
        payload = msg.payload.decode()
        dto = MetricsDto(**json.loads(payload))

        window.new_training_metrics.emit(dto)

    except Exception as e:
        Terminal().log(f"[RECEPTOR] Error al procesar mensaje: {e}.", LogType.ERROR)


def init_mqtt_listener(window):
    client = mqtt.Client(userdata=window)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        Terminal().log("[RECEPTOR] Conectando al broker local.", LogType.INFO)
        client.connect("localhost", 1883, 60)

        client.loop_forever()
    except Exception as e:
        Terminal().log(f"[RECEPTOR] No se pudo conectar al broker: {e}.", LogType.ERROR)
