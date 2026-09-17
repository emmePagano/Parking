# ------------------------------------------------ IMPORT ----------------------------------------
import machine, time
from machine import Pin
from time import sleep
import dht

import stato
import hcsr04
import servo
from servo import set_angle
import buzzer
import button
import oled

import mqtt
import wifi
 
# ---------------------------------------------------- DICHIARAZIONI -----------------------------------------------------------------

# ULTRASONIC
sensor_outside = hcsr04.HCSR04(trigger_pin=22, echo_pin=23)
sensor_inside = hcsr04.HCSR04(trigger_pin=26, echo_pin=27)

# SEMAFORO
red = Pin(15, Pin.OUT)
yellow = Pin(2, Pin.OUT)
green = Pin(4, Pin.OUT)

# BUZZER
buzzer = buzzer.BUZZER(32)

# HUMIDITY TEMPERATURE
ht = dht.DHT22(Pin(5))

# PULSANTE
pulsante = button.BUTTON(13)

# DISPLAY
display = oled.OLED(18, 19)

# ----------------- INIZIALIZZAZIONI ----------------------

# inizializzazione del semaforo
red.off()
yellow.off()
green.on()

# inizializzazione della sbarra, la chiudiamo
set_angle(0)
sleep(2)

# Mostra il logo all'avvio
display.show_logo()

# --------------- MESSA IN FUNZIONE DEL SISTEMA -------------------
while True:
    
    foundMatch = False    # variabile che rende unica la condizione da eseguire nel ciclo
    
    try:
        if not wifi.check_connection(): # controlliamo che il dispositivo sia ancora connesso
            display.clear()             # in caso contrario, lo riconnettiamo
            display.oled.text('Riconnessione...', 0, 30)  # mostriamo 'Riconnessione' a schermo
            display.oled.show()
        
        mqtt.check_msg()   # attraverso MQTT, controlliamo la presenza di messaggi
        
        ''' Prendiamo i dati dai sensori per elaborare lo stato in cui si trova il garage.
            Dai due sensori ad ultrasuoni leggiamo la distanza misurata,
            da cui elaboriamo la presenza di eventuali veicoli all'ingresso o all'interno della struttura.'''
        
        distance_outside = sensor_outside.distance_cm()  # lettura della distanza misurata dal sensore esterno
        distance_inside = sensor_inside.distance_cm()    # lettura della distanza misurata dal sensore interno
        ht.measure()    # lettura dei valori di temperatura e umidità della struttura
        
        print('Distanza fuori:', distance_outside, 'cm')
        print('Distanza dentro:', distance_inside, 'cm')
        print('Temperatura: ', ht.temperature(), 'C, Umidità: ', ht.humidity(), '%\n')
        temperatura = ht.temperature()
        umidita = ht.humidity()


        # utilizzando MQTT, pubblichiamo i dati riguardanti i valori di temperatura ed umidità registrati
        
        msg = "Temperatura: {} C, Umidità: {} %".format(ht.temperature(), ht.humidity())
        mqtt.publish(msg)
        
        ''' Valutiamo lo stato del garage attraverso due variabili booleane.
            Se la distanza misurata dal sensore interno è maggiore di 18 cm, il garage è LIBERO
            Se il sensore esterno misura un valore minore di 10 cm, è stato rilevato un veicolo all'esterno in WAITING'''

        stato.libero = distance_inside > 18  # valutiamo la condizione di LIBERO
        waiting = distance_outside < 10      # valutiamo la condizione di WAITING
        
        '''Condizioni di emergenza:
           se la temperatura o l'umidità rilevate superano una certa soglia (modificabile in app)
           il sistema va in allarme'''
        
        allarmeTemperatura = ht.temperature() > stato.soglia_temp # default: 50
        allarmeUmidità = ht.humidity() > stato.soglia_umid # default: 90
        
# ---------------------------------------------VALUTAZIONE STATI ----------------------------------------

        '''La prima condizione che valutiamo è quella d'emergenza:
           se una delle variabili allarmeTemperatura o allarmeUmidità è vera, bisogna evacuare la struttura.
           Eseguiremo questo codice in maniera ciclica fino a fine emergenza'''
        
        if (allarmeTemperatura or allarmeUmidità) and not foundMatch:
            foundMatch = True
            display.clear()
            display.oled.text('ALERT!', 40, 30)   # mostriamo ALERT sull'OLED
            display.oled.show()
            
            print('ALLARME. EVACUARE')
            set_angle(90)       # alziamo la sbarra per permettere l'evacuazione 
            red.on()            # facciamo lampeggiare il semaforo
            yellow.on()
            green.on()
            buzzer.play_alarm() # suoniamo l'allarme
            red.off()
            yellow.off()
            green.off()
            
            
        '''Seconda condizione: il garage è libero ed è stato prenotato'''
        
        if (stato.prenotato and stato.libero) and not foundMatch:
            foundMatch = True
            print("IF DEL PRENOTATO")
            display.clear()
            display.oled.text(str(temperatura) + "C " + str(umidita) +"%",1,1)
            display.oled.text('PRENOTATO',30,30)
            display.oled.show()  # mostriamo l'avvenuta prenotazione sull'OLED ed i valori di temperatura ed umidità
            yellow.off()
            green.off()
            red.on()             # accendiamo il semaforo rosso
            set_angle(0)         # chiudiamo o manteniamo chiusa la sbarra
        
        
        '''Terza condizione: è stato effettuato il pagamento (il veicolo deve uscire) e l'interno è occupato'''
        
        if stato.pagamento and not foundMatch:
            foundMatch = True
            
            if not stato.libero:                  # rivalutiamo l'if finchè il veicolo non è fuori dalla struttura
                display.clear()
                display.oled.text('PAGATO',40,30) # mostriamo la riuscita del pagamento
                display.oled.show()
                red.off()
                yellow.on()
                set_angle(90)                     # apriamo la sbarra per permettere l'uscita 
                buzzer.play_ladyg()               # suoniamo ABRACADABRA sul buzzer
            if stato.libero:
                stato.pagamento = False


        '''Quarta condizione: il garage è libero e nessun veicolo è posto all'esterno'''
                
        if (stato.libero and not waiting) and not foundMatch:
            foundMatch = True
            set_angle(0)             # chiudiamo o manteniamo chiusa la sbarra
            display.show_logo()
            display.oled.text(str(temperatura) + "C", 1, 1, 0)
            display.oled.text(str(umidita) + "%", 1, 10, 0)
            display.oled.show()      # mostriamo la temperatura, l'umidità ed il nostro logo
            red.off()
            yellow.off()
            green.on()               # accendiamo il semaforo verde
  
  
        '''Quinta condizione: il garage è libero ed un veicolo sta aspettando all'esterno'''
        
        if (stato.libero and waiting) and not foundMatch:
            foundMatch = True
            green.off()
            red.off()
            yellow.on()              # accendiamo il semaforo giallo
            set_angle(90)            # apriamo la sbarra  
            buzzer.play_ladyg()      # suoniamo ABRACADABRA sul buzzer
            
                        
        '''Sesta condizione: il garage è occupato'''
            
        if not stato.libero and not foundMatch:
            foundMatch = True
            display.clear()
            display.oled.text(str(temperatura) + "C " + str(umidita) +"%",1,1)
            display.oled.text('OCCUPATO',30,30)
            display.oled.show()      # mostriamo OCCUPATO, temperatura ed umidità sull'OLED
            yellow.off()
            green.off()
            red.on()                 # accendiamo il semaforo rosso
            set_angle(0)             # chiudiamo o manteniamo chiusa la sbarra 
            
        
    except OSError as ex:
        print('Errore:', ex)
    sleep(0.5)

