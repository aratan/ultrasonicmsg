# main.py
import ollama
from datetime import datetime
import time
import random
import argparse
import logging
from transmitir import generar_senal
from recibir import iniciar_recepcion

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes ---
PREAMBLE = "*"  # No se usa, ya que se implemento un preambulo en transmitir.
TOKEN = "$T"
RESCUE_MSG = "!RESCUE!"
TIMEOUT_SECS = 5
MAX_RETRIES = 3
INITIAL_WAIT = 0.1
BEACON_INTERVAL = 10

# --- Funciones Auxiliares ---

def get_current_time() -> str:
    return datetime.now().strftime("%H:%M")

def llm(mensaje, tools=True):
    try:
        if tools:
            tool_list = [{
                'type': 'function',
                'function': {
                    'name': 'get_current_time',
                    'description': 'Obtiene la hora actual en formato HH:MM.',
                    'parameters': {'type': 'object', 'properties': {}},
                },
            }]
        else:
            tool_list = []

        response = ollama.chat(
            model='mistral-small-3.1',
            messages=[{'role': 'user', 'content': f'{mensaje}.'}],
            tools=tool_list,
        )
        if response['message'].get('tool_calls'):
            hora_actual = get_current_time()
            respuesta = ollama.chat(
                model='mistral-small-3.1',
                messages=[
                    {'role': 'system', 'content': 'Responde siempre en español.'},
                    {'role': 'assistant', 'content': f'La hora actual es {hora_actual}'},
                    {'role': 'user', 'content': '¿Es la hora de cenar? Ceno de 22:00 a 23:00 '},
                ],
            )
            result = respuesta['message']['content']
        else:
            result = response['message']['content']

        logging.info('Respuesta del modelo: %s', result)
        return result

    except Exception as e:
        logging.error("Error al interactuar con Ollama: %s", e)
        return "Error en la comunicación con el LLM."


def enviar_mensaje(mensaje, es_maestro, requiere_ack=False):
    mensaje_con_token = mensaje + TOKEN if es_maestro else mensaje
    if requiere_ack:
        mensaje_con_token += "ACK_REQ"
    generar_senal(mensaje_con_token)

    if requiere_ack:
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_SECS:
            ack_recibido = iniciar_recepcion(timeout=TIMEOUT_SECS - (time.time() - start_time))
            if ack_recibido == "ACK":
                logging.info("ACK recibido.")
                return True
        logging.warning("No se recibió ACK.")
        return False
    return True

def esperar_turno(soy_maestro, timeout=TIMEOUT_SECS):
    start_time = time.time()
    while time.time() - start_time < timeout:
        mensaje_recibido = iniciar_recepcion(timeout=timeout - (time.time() - start_time))
        if mensaje_recibido:
            if mensaje_recibido.endswith("ACK_REQ"):
                generar_senal("ACK")
                mensaje_recibido = mensaje_recibido[:-len("ACK_REQ")]
            if mensaje_recibido.endswith(TOKEN):
                logging.info("Token recibido!")
                return mensaje_recibido[:-len(TOKEN)], True
            elif mensaje_recibido.startswith(RESCUE_MSG) and not soy_maestro:
                logging.info("Mensaje de rescate recibido. No me convierto en maestro.")
                return None, False
            else:
                logging.info("Mensaje recibido sin token. Ignorando.")
                return None, False
    logging.warning("Timeout esperando el token.")
    return None, False

def main(soy_maestro=False, device_id="A"):
    logging.info(f"Dispositivo {device_id}: Iniciando {'como maestro' if soy_maestro else 'como esclavo'}.")
    time.sleep(random.uniform(1, 2))

    retry_count = 0
    wait_time = INITIAL_WAIT
    last_beacon_time = time.time()

    while retry_count < MAX_RETRIES:
        if soy_maestro:
            if time.time() - last_beacon_time > BEACON_INTERVAL:
                 generar_senal("SOY_MAESTRO")
                 last_beacon_time = time.time()

            mensaje_inicial = " Continua una historia...  "
            respuesta_llm = llm(mensaje_inicial)

            if enviar_mensaje(respuesta_llm, soy_maestro, requiere_ack=True):
                mensaje_recibido, exito = esperar_turno(soy_maestro)
            else:
                exito = False

        else:
            mensaje_recibido, exito = esperar_turno(soy_maestro)
            if not exito:
                logging.info(f"Dispositivo {device_id}: Intentando rescate...")
                generar_senal(RESCUE_MSG)
                time.sleep(1)
                mensaje_recibido, exito = esperar_turno(soy_maestro, timeout=2)
                if not exito:
                    logging.info(f"Dispositivo {device_id}: Rescate exitoso. Ahora soy maestro.")
                    soy_maestro = True
                    continue
                else:
                    logging.info(f"Dispositivo {device_id}: Otro dispositivo ya rescató. Vuelvo a escuchar.")
                    continue

        if exito:
            retry_count = 0
            respuesta_llm = llm(mensaje_recibido, tools=False)

            if enviar_mensaje(respuesta_llm, soy_maestro, requiere_ack=True):
                soy_maestro = False
            else:
               exito = False

        else:
            retry_count += 1
            logging.warning(f"Dispositivo {device_id}: Intento fallido #{retry_count}. Esperando {wait_time:.2f}s")
            time.sleep(wait_time)
            wait_time *= 2

    logging.error(f"Dispositivo {device_id}: Demasiados intentos fallidos. Saliendo.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comunicación con LLMs.")
    parser.add_argument("--maestro", action="store_true", help="Iniciar como dispositivo maestro.")
    parser.add_argument("--id", type=str, default="A", help="Identificador del dispositivo.")
    args = parser.parse_args()

    main(soy_maestro=args.maestro, device_id=args.id)