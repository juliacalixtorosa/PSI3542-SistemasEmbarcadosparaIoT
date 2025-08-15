import network
import urequests
import time
import random

# --- Configurações da sua rede Wi-Fi (para o simulador) ---
SSID = 'Wokwi-GUEST'  # Rede Wi-Fi padrão do Wokwi para simulação
PASSWORD = ''         # Senha da rede Wi-Fi padrão do Wokwi (vazia para Wokwi-GUEST)

# --- Configurações do seu canal ThingSpeak ---
THINGSPEAK_API_KEY = "SUA_WRITE_API_KEY" # Substitua pela sua Write API Key
THINGSPEAK_URL = "http://api.thingspeak.com/update" # Use HTTP no Wokwi para simplificar

# --- Função para conectar ao Wi-Fi ---
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Conectando ao Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Conexão Wi-Fi estabelecida:', sta_if.ifconfig())

# --- Função para enviar dados ao ThingSpeak ---
def send_data_to_thingspeak():
    # Gerar dados simulados de temperatura e umidade
    temperature = round(random.uniform(20.0, 30.0), 2)  # Temperatura entre 20 e 30 °C
    humidity = round(random.uniform(50.0, 70.0), 2)     # Umidade entre 50 e 70 %

    # Construir os parâmetros da requisição
    # A biblioteca urequests no MicroPython pode não suportar 'params' diretamente para GET
    # Então, construímos a URL com os parâmetros
    url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1={temperature}&field2={humidity}"

    try:
        # Enviar a requisição GET
        print(f"Enviando dados: Temp={temperature}°C, Umi={humidity}%")
        response = urequests.get(url)

        # Verificar a resposta
        if response.status_code == 200:
            print(f"Dados enviados com sucesso! Entry ID: {response.text}")
        else:
            print(f"Erro ao enviar dados. Status code: {response.status_code}, Response: {response.text}")
        response.close() # Fechar a conexão
    except Exception as e:
        print(f"Erro de conexão/requisição: {e}")

# --- Loop principal ---
if __name__ == "__main__":
    connect_wifi() # Conecta ao Wi-Fi uma vez

    print("Iniciando simulador ThingSpeak com ESP32...")
    while True:
        send_data_to_thingspeak()
        # Enviar dados a cada 20 segundos (ThingSpeak free tem limite de 15s, 20s é mais seguro)
        time.sleep(20)