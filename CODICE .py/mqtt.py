from umqttsimple import MQTTClient
import stato

# IP del broker Mosquitto (PC con Docker)
mqtt_server = '172.20.10.3'  
client_id = 'esp32_gruppo16'
topic_pub = b'esp32_gruppo16/th'

# Creazione del client MQTT
client = MQTTClient(client_id, mqtt_server)

# connessione MQTT
def mqtt_connect():
    try:
        client.connect()
        print("Connesso al broker MQTT")
        client.set_callback(mqtt_callback)
        
        #sottoscrizione del client ai topic
        client.subscribe(b'esp32_gruppo16/pagamento')
        client.subscribe(b'esp32_gruppo16/soglia_temp')
        client.subscribe(b'esp32_gruppo16/soglia_umid')
        client.subscribe(b'esp32_gruppo16/prenotazione')
        client.subscribe(b'esp32_gruppo16/sbarra')
    except Exception as e:
        print("Errore di connessione al broker MQTT:", e)

# reimpostazione della connessione MQTT se persa
def mqtt_reset():
    global client
    max_retry=10
    delay=2
    try:
        print("Disconnessione dal broker MQTT in corso...")
        client.disconnect()
    except Exception as e:
        print("Errore durante la disconnessione MQTT (ignorato):", e)

    for attempt in range(1, max_retry + 1):
        try:
            print(f"Tentativo di riconnessione MQTT ({attempt}/{max_retry})...")
            client = MQTTClient(client_id, mqtt_server)
            client.connect()
            print("Riconnesso al broker MQTT")
            client.set_callback(mqtt_callback)
            client.subscribe(b'esp32_gruppo16/pagamento')
            client.subscribe(b'esp32_gruppo16/soglia_temp')
            client.subscribe(b'esp32_gruppo16/soglia_umid')
            client.subscribe(b'esp32_gruppo16/prenotazione')
            client.subscribe(b'esp32_gruppo16/sbarra')
            return True
        except Exception as e:
            print("Errore durante la riconnessione MQTT:", e)
            time.sleep(delay)

    print("Impossibile riconnettersi al broker MQTT dopo vari tentativi.")
    return False

def check_msg():
    client.check_msg()
    
def publish(msg):
    client.publish(topic_pub, msg.encode('utf-8'))
    
def mqtt_callback(topic, msg):
    print("Messaggio ricevuto:", topic, msg)  # ricezione del msg
    
    '''Riconoscimento del Topic del messaggio'''
    
    # Topic: Pagamento
    if topic == b'esp32_gruppo16/pagamento':        
        payload_str = msg.decode().upper()
        if payload_str == "PAGATO":
            print("Pagamento ricevuto da MQTT!")
            stato.pagamento = True   # se da APP abbiamo ricevuto il pagamento
                                     # allora ne settiamo la variabile a true

    # Topic: Soglia temperatura        
    elif topic == b'esp32_gruppo16/soglia_temp':    
        try:
            stato.soglia_temp = int(msg.decode())
            print("Soglia temperatura aggiornata a: ", stato.soglia_temp)
        except ValueError:          # Aggiorniamo la soglia della temperatura alla nuova impostata
            print("Valore temperatura ricevuto non valido")
    
    # Topic: Soglia umidità
    elif topic == b'esp32_gruppo16/soglia_umid':    
        try:
            stato.soglia_umid = int(msg.decode())
            print("Soglia umidità aggiornata a: ", stato.soglia_umid)
        except ValueError:          # Aggiorniamo la soglia dell'umidità alla nuova impostata
            print("Valore umidità ricevuto non valido")
            
    # Topic: Prenotazione        
    elif topic == b'esp32_gruppo16/prenotazione':
        payload_str = msg.decode().upper()
        if payload_str == "PRENOTATO":
            stato.prenotato = True   # se da APP abbiamo ricevuto richiesta di prenotazione
                                     # allora ne settiamo la variabile a true
    
    # Topic: Sbarra
    elif topic == b'esp32_gruppo16/sbarra':
        payload_str = msg.decode().upper()
        if payload_str == "OPEN":
            stato.prenotato = False  # se da APP chi ha prenotato richiede l'apertura della sbarra
                                     # resettiamo lo stato del garage
