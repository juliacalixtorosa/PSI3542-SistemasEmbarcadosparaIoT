import network
import urequests
import time
import dht
import machine
import json
# --- Configurações da sua rede Wi-Fi ---
SSID = 'Wokwi-GUEST'
PASSWORD = ''
# --- Configurações do seu canal ThingSpeak ---
THINGSPEAK_WRITE_API_KEY = "IN91SKW1JA4CZWQL" # Substitua aqui
THINGSPEAK_READ_API_KEY = "61PVPIZYS08IJUNC" # Substitua aqui
THINGSPEAK_CHANNEL_ID = "3035690" # Substitua aqui
THINGSPEAK_URL_UPDATE = "https://api.thingspeak.com/update"
THINGSPEAK_URL_READ_FIELD3 = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/3/last.json"
# --- Configurações do hardware ---
dht_sensor = dht.DHT22(machine.Pin(15))
led = machine.Pin(18, machine.Pin.OUT)
# --- Função para conectar ao Wi-Fi ---
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Conectando ao Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        time.sleep(5)
        if not sta_if.isconnected():
            print("Erro de conexão Wi-Fi.")
            return False
    print('Conexão Wi-Fi estabelecida:', sta_if.ifconfig())
    return True
# --- Função para ENVIAR dados usando POST ---
def send_data_to_thingspeak_post(temp, hum):
    # Dicionário com os dados a serem enviados
    data = {
        'api_key': THINGSPEAK_WRITE_API_KEY,
        'field1': temp,
        'field2': hum
    }
    # Headers para indicar o tipo de conteúdo
    headers = {'Content-Type': 'application/json'}
    try:
        print(f"Enviando dados (POST): Temp={temp}°C, Umi={hum}%")
        # Envia a requisição POST com os dados no corpo
        response = urequests.post(THINGSPEAK_URL_UPDATE, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Dados enviados com sucesso! Entry ID: {response.text}")
        else:
            print(f"Erro ao enviar dados. Status code: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Erro ao enviar: {e}")
# --- Função para RECEBER o comando usando GET ---
def read_control_command():
    # A API de leitura usa GET e requer a API Key
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/3/last.json?api_key={THINGSPEAK_READ_API_KEY}"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'field3' in data and data['field3'] is not None:
                command = data['field3']
                print(f"Comando recebido do ThingSpeak: {command}")
                return command
            else:
                print("Comando de controle não encontrado no canal.")
                return None
        else:
            print(f"Erro ao ler comando. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao ler comando: {e}")
        return None
# --- Loop principal ---
if __name__ == "__main__":
    if not connect_wifi():
        print("Impossível continuar sem conexão Wi-Fi.")
    else:
        print("Pronto para iniciar o termostato.")
        while True:
            try:
                dht_sensor.measure()
                temp = dht_sensor.temperature()
                hum = dht_sensor.humidity()
                send_data_to_thingspeak_post(temp, hum)
                time.sleep(5)
                control_command = read_control_command()
                if control_command == 1:
                    print("Comando '1' recebido. Ligando LED.")
                    led.on()
                elif control_command == 0:
                    print("Comando '0' recebido. Desligando LED.")
                    led.off()
                else:
                    print(f"Comando '{control_command}' inválido ou ausente.")
                time.sleep(15)
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                time.sleep(10)