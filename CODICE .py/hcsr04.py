import machine, time
from machine import Pin

class HCSR04:
    """
    Driver per il sensore HC-SR04.
    Il range del sensore va dai 2cm ai 4m.
    I timeouts degli echo pin son convertiti in OSError('Out of range')
    """
    
    # il timeout dell'echo ha come inizio 400 cm, il limite del range del chip
    
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        
        """
        trigger_pin: Il pin di output per gli impulsi.
        echo_pin: Pin readonly per misurare la distanza. Da proteggere con un resistore da 1k ohm
        echo_timeout_us: Timeout in microsecondi sull'ascolto dell'echo pin.
        Di default è nel limite di range del sensore (4m).
        """
        
        self.echo_timeout_us = echo_timeout_us
        
        # Inizializzazione del trigger pin
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Inizializzazione del pin di echo
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        """
        Manda il segnale sul pin trigger ed ascolta il pin di echo.
        Usa il metodo `machime.time_pulse_us()` per avere i microsecondi passati fino alla ricezione dell'echo.
        """
        self.trigger.value(0) # Stabilizza il sensore
        time.sleep_us(5)
        self.trigger.value(1)
        # Manda il segnale per 10us
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = Eccezione TimeOut (ETIMEDOUT)
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        """
        Restituisce la distanza in millimetri senza operazioni di floating point.
        """
        pulse_time = self._send_pulse_and_wait()

        # Per calcolare la distanza prendiamo il pulse_time e lo dividiamo per 2
        # (perchè l'impulso percorre la distanza due volte) e per 29.1 perchè
        # la velocità del suono nell'aria (343.2 m/s), equivale a 0.34320 mm/us
        # ed 1 mm equivale quindi a 2.91us
        # pulsetime // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582
        
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        Prende la distanza in centimetri con operazioni di floating point.
        Restituisce un float.
        """
        pulse_time = self._send_pulse_and_wait()

        # Per calcolare la distanza prendiamo il pulse_time e lo dividiamo per 2
        # (perchè l'impulso percorre la distanza due volte) e per 29.1 perchè
        # la velocità del suono nell'aria (343.2 m/s), equivale a 0.034320 cm/us
        # ed 1 cm equivale quindi a 29.1us
        
        cms = (pulse_time / 2) / 29.1
        return cms
    