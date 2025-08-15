# ESP32 -> ThingSpeak via MQTT (corrigido)
import network, time, dht, machine
from umqtt.simple import MQTTClient

# --- Wi-Fi ---
SSID = 'Wokwi-GUEST'
PASSWORD = ''

# --- Identificação do CANAL (numérico; só aparece nos tópicos) ---
CHANNEL_ID = "3033442"

# --- Credenciais MQTT (ThingSpeak > Devices > MQTT) ---
# Substitua pelos valores EXATOS exibidos na sua conta:
CLIENT_ID  = b"GR0IJjozHDcNATsRBS8ILCM"      # ex.: b"HwwiOjIeASM6CS48OS8ZIyQ"
MQTT_USER  = b"GR0IJjozHDcNATsRBS8ILCM"       # pode ser igual ao Client ID (depende da conta)
MQTT_PASS  = b"PnI7tBVSHtuarxdD6zV3ojwd"   # "Password (MQTT API Key)" de Devices->MQTT

# --- Broker ---
BROKER   = "mqtt3.thingspeak.com"  # use este host
PORT     = 1883                    # sem TLS (para TLS: 8883 + ssl=True, depois de validar)
KEEPALIVE = 60

# --- Write API Key do CANAL (para /publish) ---
WRITE_API_KEY = "XPBGLNFGL7IO8CG4"  # Channel Write API Key do canal 3033385

# --- Tópicos (bytes) ---
TOPIC_PUBLISH_ALL = f"channels/{CHANNEL_ID}/publish".encode()
TOPIC_CMD         = f"channels/{CHANNEL_ID}/subscribe/fields/field3".encode()
TOPIC_STATUS      = f"channels/{CHANNEL_ID}/publish/fields/field8".encode()  # opcional (status)

# --- Hardware ---
dht_sensor = dht.DHT22(machine.Pin(15))
led = machine.Pin(18, machine.Pin.OUT)

def connect_wifi():
    sta = network.WLAN(network.STA_IF)
    if not sta.isconnected():
        print("Conectando ao Wi-Fi...")
        sta.active(True)
        sta.connect(SSID, PASSWORD)
        for _ in range(40):
            if sta.isconnected(): break
            time.sleep(0.25)
        if not sta.isconnected():
            print("Falha no Wi-Fi.")
            return False
    print("Wi-Fi OK:", sta.ifconfig())
    return True

def on_msg(topic, msg):
    print("[MQTT RX]", topic, msg)
    if msg == b"1":
        led.on();  print("LED ON")
    elif msg == b"0":
        led.off(); print("LED OFF")

def new_client():
    c = MQTTClient(client_id=CLIENT_ID, server=BROKER, port=PORT,
                   user=MQTT_USER, password=MQTT_PASS,
                   keepalive=KEEPALIVE, ssl=False)
    c.set_callback(on_msg)
    # LWT opcional (se cair, publica 0 em field8)
    try:
        c.set_last_will(TOPIC_STATUS, b"0", retain=False)
    except:
        pass
    return c

def main():
    if not connect_wifi():
        return

    client = new_client()
    try:
        client.connect()
        print("Conectado ao ThingSpeak MQTT.")
        # Sinaliza "online" no field8 (opcional)
        try:
            client.publish(TOPIC_STATUS, b"1")
        except:
            pass
        # IMPORTANTE: ThingSpeak aceita APENAS QoS 0
        client.subscribe(TOPIC_CMD, qos=0)
        print("Inscrito em comandos (field3).")
    except Exception as e:
        print("Falha CONNECT/SUBSCRIBE:", repr(e))
        return

    while True:
        try:
            # Processa comandos recebidos
            client.check_msg()

            # Leitura do sensor
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()

            # /publish exige api_key do CANAL no payload
            payload = f"api_key={WRITE_API_KEY}&field1={t}&field2={h}".encode()
            client.publish(TOPIC_PUBLISH_ALL, payload)  # QoS 0
            print("PUB:", payload)

            time.sleep(15)  # respeite o rate mínimo do ThingSpeak
        except Exception as e:
            print("Erro loop:", repr(e))
            time.sleep(3)
            try:
                client.disconnect()
            except:
                pass
            time.sleep(2)
            client = new_client()
            client.connect()
            client.subscribe(TOPIC_CMD, qos=0)
            print("Reconectado e reinscrito.")

main()

