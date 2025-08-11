import time
import paho.mqtt.client as mqtt
import board
import adafruit_tca9548a 
from utils import initADS, initBME


MOISTURE_LEVEL = 14000
WATER_LEVEL_MIN = 4000
WATER_LEVEL_MAX = 14000

PIN_TCA__ADS = 5
PIN_TCA__BME = 2
PIN_LED_VERDE = 27
PIN_LED_ROSSO = 27

i2c = board.I2C() # uses board.SCL and board.SDA
tca = adafruit_tca9548a.TCA9548A(i2c)

# INIZIO DEBUG
for channel in range(8):
    if tca[channel].try_lock():
        print("Channel {}:".format(channel), end=
        "")
        addresses = tca[channel].scan()
        print([hex(address) for address in addresses if address != 0x70])
        tca[channel].unlock()
# FINE DEBUG

greenLed = LED(PIN_LED_VERDE)
redLed = LED(PIN_LED_ROSSO)

ads = initADS(tca, PIN_TCA__ADS)
bme280_sensor = initBME(tca)

broker = "localhost"
port = 1883
username = "nomeutente"
password = "password"
topic = "sensore/temperatura"

client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker, port, 60)

try:
    while True:
        temperatura = bme280_sensor.temperature
        client.publish(topic, temperatura)
        print(f"Pubblicato: {temperatura}   C")
        time.sleep(5)
except KeyboardInterrupt:
    print("Interrotto")
    client.disconnect()