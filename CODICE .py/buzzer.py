import time
import machine
from machine import Pin, PWM
from time import sleep_ms

class BUZZER:
    def __init__(self, sig_pin):
        self.sig_pin = sig_pin
        self.pwm = PWM(Pin(sig_pin, Pin.OUT))
        self.stop()  # Inizialmente spento
        self.pwm.deinit()  # disattiviamo il pwm all'inizio per evitare errori di segnale in inizializzazione
        self.first = True
    
    def __init_pwm(self):
        self.pwm = PWM(Pin(self.sig_pin, Pin.OUT))  # Riattiva PWM
        
    def play(self, melodies, wait, duty):
        if self.first == True:   # se è la prima esecuzione riattiviamo il pin disattivato in __init__
            self.__init_pwm()
            self.first = False
        
        for note in melodies:
            if note == 0:
                self.pwm.duty(0) # Pausa
            else:
                self.pwm.freq(note)
                self.pwm.duty(duty) # Imposta il volume del suono
            sleep_ms(wait) # Durata della nota
        self.stop() # Ferma il suono alla fine
    
    # Spegne il suono
    def stop(self):
        self.pwm.duty(0)  
    
    #suona Lady Gaga
    def play_ladyg(self):
        self.play(ladyg,110,512)
    
    #suona l'allarme
    def play_alarm(self): 
        self.play(alarm,100,512)
        
# Note e rispettive frequenze per il BUZZER
A5=880
B5=988
C6=1047
D6=1175
E6=1319
E7=2637

# Abracadabra di Lady Gaga sul BUZZER
ladyg = [
    
    E6, 0, E6, 0, E6, 0, E6, E6, E6, 
    0, C6, 0, C6, C6, C6, 0, 
    D6, 0, D6, D6, D6,  0, D6, D6, D6, 0,  
    B5, 0, B5, B5, B5, 0, 
    D6,  0, D6, D6, D6,  0, D6, D6, D6, 0,  
    B5, 0, B5, B5, B5, 0, 
    D6, 0, C6, 0, B5, 0, A5, A5, A5, A5,
    0, 0, 0, 0
    
    ]

# Allarme sul BUZZER
alarm = [
    
    E7, E7, E7, 0, 0, E7, E7, E7, 0, 0, 
    
    ]

