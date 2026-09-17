import network
import time
from umqttsimple import MQTTClient
import mqtt

# Configura le credenziali WiFi (hotspot del cellulare)
ssid = "Cory"
password = "corycorycory"

wlan = network.WLAN(network.STA_IF)

# Funzione per connettersi a WiFi
def connect_wifi():
    print("Sto tentando di connettermi al Wi-Fi...")
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print('WiFi connesso:', wlan.ifconfig())
    

# funzione che controlla la connessione e la ristabilisce se manca
def check_connection():
    if not wlan.isconnected(): # se la connessione manca
        print("Connessione Wifi persa, riconnessione in corso...")
        wlan.disconnect()
        wlan.connect(ssid, password)    # proviamo a ristabilirla
        retry = 0
        while not wlan.isconnected() and retry < 10:  
            time.sleep(1)
            retry += 1
        if wlan.isconnected():          # se la riconnessione è avvenuta con successo
            print("Riconnesso con successo: ", wlan.ifconfig())
            time.sleep(1)
            mqtt.mqtt_reset()           # resettiamo anche l'MQTT
            return True                 # restituiamo TRUE (connessione presente)
        else:
            print("Errore: impossibile riconnettersi al WiFi")
            return False                # restituiamo FALSE (connessione assente, non siamo riusciti a ripristinarla)
        
    else:
        print("Wifi ancora connesso.")
        return True                     # restituiamo TRUE (connessione non persa)
