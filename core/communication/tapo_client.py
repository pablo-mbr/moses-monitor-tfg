import asyncio
from tapo import ApiClient 
from log_types import LogType
from gui.components.terminal import Terminal

async def measure_consumption(data_queue, credentials, stop_event):

    PLUG_IP = credentials['ip']
    EMAIL = credentials['email']
    PASS = credentials['pass']

    """
    IP_ENCHUFE = "10.171.247.148"
    EMAIL = "samuel.gonzalez.ramos.2004@gmail.com"
    PASS = "TPlink115"
    
    """
    client = ApiClient(EMAIL, PASS)
    
    try:
        device = await client.p110(PLUG_IP)
        Terminal().log(f"[MOTOR] Conectado a {PLUG_IP}.", LogType.SUCCESS)
        while not stop_event.is_set():
            try:
                
                usage = await device.get_current_power()
                power = usage.current_power
                data_queue.put(power)
                
            except Exception as e:
                data_queue.put(f"[MOTOR] Error de lectura: {e}.")

            await asyncio.sleep(1)

    except Exception as e:
        data_queue.put(f"[MOTOR] Error crítico de conexión: {e}.")