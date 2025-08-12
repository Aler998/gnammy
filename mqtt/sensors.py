import time
import paho.mqtt.client as mqtt
import board
import adafruit_tca9548a 
from utils import initADS, initBME
from gpiozero import LED
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

logging.basicConfig(level=logging.INFO)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_TEMPERATURA = "sensore/bme280/temperatura"
TOPIC_UMIDITA = "sensore/bme280/umidità"
TOPIC_PRESSIONE = "sensore/bme280/pressione"
TOPIC_ACQUA = "sensore/analog/wl"

PIN_TCA__ADS = 5
PIN_TCA__BME = 2
PIN_LED_VERDE = 27
PIN_LED_ROSSO = 22

i2c = board.I2C() # uses board.SCL and board.SDA
tca = adafruit_tca9548a.TCA9548A(i2c)

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
        client.publish(TOPIC_TEMPERATURA, bme280_sensor.temperature)
        client.publish(TOPIC_UMIDITA, bme280_sensor.humidity)
        client.publish(TOPIC_PRESSIONE, bme280_sensor.pressure)
        client.publish(TOPIC_ACQUA, wl.value)
        logging.info("Pubblicati dati")
        time.sleep(5)
except KeyboardInterrupt:
    logging.info("Interrotto")
    client.disconnect()