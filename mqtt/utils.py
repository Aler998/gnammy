import board
import time
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def initADS(tca, pin):
    for i in range(5):
        try:
            return ADS.ADS1115(tca[pin])
        except:
            time.sleep(2)
    print("[FALLIMENTO] Impossibile inizializzare ADS dopo vari tentativi.")
    return None



def initBME(tca):
    for i in range(5):
        try:
            return adafruit_bme280.Adafruit_BME280_I2C(tca[2], address=0x76)
        except:
            time.sleep(2)
    print("[FALLIMENTO] Impossibile inizializzare BME dopo vari tentativi.")
    return None
         
bme280_sensors = initBME()