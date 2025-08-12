import time
import paho.mqtt.client as mqtt
import board
import adafruit_tca9548a 
from utils import initADS, initBME, showData
from gpiozero import LED
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

import adafruit_ssd1306

logging.basicConfig(level=logging.INFO)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_TEMPERATURA = "sensore/bme280/temperatura"
TOPIC_UMIDITA = "sensore/bme280/umidità"
TOPIC_PRESSIONE = "sensore/bme280/pressione"
TOPIC_ACQUA = "sensore/analog/wl"

WL_MAX = 25000
WL_MIN = 1000

PIN_TCA__ADS = 5
PIN_TCA__BME = 2
PIN_TCA__DISPLAY = 1
PIN_LED_VERDE = 27
PIN_LED_ROSSO = 22

i2c = board.I2C() # uses board.SCL and board.SDA
tca = adafruit_tca9548a.TCA9548A(i2c)
display_i2c = tca[PIN_TCA__DISPLAY]

# Inizializza il display SSD1306 (128x64)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, display_i2c)



# INIZIO DEBUG
for channel in range(8):
    if tca[channel].try_lock():
        logging.info("Channel {}:".format(channel))
        addresses = tca[channel].scan()
        logging.info([hex(address) for address in addresses if address != 0x70])
        tca[channel].unlock()
# FINE DEBUG

greenLed = LED(PIN_LED_VERDE)
redLed = LED(PIN_LED_ROSSO)

ads = initADS(tca, PIN_TCA__ADS)
bme280_sensor = initBME(tca)
wl = AnalogIn(ads, ADS.P0)  # A0

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        t = bme280_sensor.temperature
        h = bme280_sensor.humidity
        p = bme280_sensor.pressure
        wl_val = wl.value
        client.publish(TOPIC_TEMPERATURA, t)
        client.publish(TOPIC_UMIDITA, h)
        client.publish(TOPIC_PRESSIONE, p)
        client.publish(TOPIC_ACQUA, wl_val)
        logging.info("Pubblicati dati")
        showData(display, {
            "Temp": f"{round(t,2)}deg", 
            "Hum" : f"{round(h,2)}%", 
            "Press": f"{round(p,2)}atm", 
            "Water": f"{round((wl_val - WL_MIN)/(WL_MAX - WL_MIN) * 100,2)}%"
        })
        time.sleep(5)
except KeyboardInterrupt:
    logging.info("Interrotto")
    client.disconnect()