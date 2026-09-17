import time
import machine
from machine import Pin
from time import sleep_ms
import stato

# parametri per gestire il debounce del bottone
last_press_time = 0        # ms passati dalla pressione precedente del bottone
debounce_time = 200        # ms di ritardo del debounce
double_click_time = 500    # Il tempo massimo (in ms) per individuare una doppia pressione

#interrupt handler
def payment_simulation(pin):
    
    global last_press_time
    time_ms = time.ticks_ms()
    elapsed_time = time.ticks_diff(time_ms, last_press_time)

    if elapsed_time < debounce_time:  # se non è passato abbastanza tempo dall'ultima chiamata,
        return                        # ignoro quella attuale
    
    stato.pagamento = True            # se il pulsante di pagamento è stato premuto,
                                      # settiamo a TRUE la variabile pagamento

    last_press_time = time_ms         # aggiorno il press time di last button
    
class BUTTON:            
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=payment_simulation) # settiamo l'interrupt fornendo condizione di TRIGGER e ISR