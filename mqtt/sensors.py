import time
import paho.mqtt.client as mqtt
import board
import adafruit_tca9548a 
from utils import initADS, initBME, showData, checkScore
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
TOPIC_A1 = "sensore/analog/a1"
TOPIC_A2 = "sensore/analog/a2"
TOPIC_A3 = "sensore/analog/a3"
TOPIC_A4 = "sensore/analog/a4"

PIN_TCA__ADS = 0
PIN_TCA__BME = 1
PIN_TCA__DISPLAY = 2
PIN_LED_VERDE = 22
PIN_LED_ROSSO = 27

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
display_i2c = tca[PIN_TCA__DISPLAY]

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
bme280_sensor = initBME(tca, PIN_TCA__BME)
#lettura analogici
a1 = AnalogIn(ads, ADS.P0)  # A0
a2 = AnalogIn(ads, ADS.P1)  # A0
a3 = AnalogIn(ads, ADS.P2)  # A0
a4 = AnalogIn(ads, ADS.P3)  # A0

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        t = bme280_sensor.temperature
        h = bme280_sensor.humidity
        p = bme280_sensor.pressure
        
        status = checkScore(t,h)
        if status:
            redLed.off()
            greenLed.on()
        else:
            greenLed.off()
            redLed.on()
        
        client.publish(TOPIC_TEMPERATURA, t)
        client.publish(TOPIC_UMIDITA, h)
        client.publish(TOPIC_PRESSIONE, p)
        
        if a1:
            client.publish(TOPIC_A1, a1.value)
        if a2:
            client.publish(TOPIC_A2, a2.value)
        if a3:
            client.publish(TOPIC_A2, a2.value)
        if a4:
            client.publish(TOPIC_A4, a4.value)
        
        showData(display, {
            "Temp": f"{round(t,2)}deg", 
            "Hum" : f"{round(h,2)}%", 
            "Press": f"{round(p * 0.000987,4)}atm", 
        })
        
        logging.info("Pubblicati dati")
        time.sleep(5)
except KeyboardInterrupt:
    logging.info("Interrotto")
    client.disconnect()