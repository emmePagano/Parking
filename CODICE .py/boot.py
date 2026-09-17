# Nel boot, ci connettiamo al wifi e settiamo l'MQTT
import wifi
import mqtt

wifi.connect_wifi()
mqtt.mqtt_connect()

#dopo la connessione, mandiamo in esecuzione il main
import main
