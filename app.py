from flask import Flask, render_template, Response
import time
import json
import board
from gpiozero import LED
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_tca9548a 
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from utils import is_half_hour, load_data, update_file, FILE_PATH, FILE_PATH2

MOISTURE_LEVEL = 14000
WATER_LEVEL_MIN = 4000
WATER_LEVEL_MAX = 14000

i2c = board.I2C() # uses board.SCL and board.SDA
tca = adafruit_tca9548a.TCA9548A(i2c)

def initADS():
    for i in range(5):
        try:
            return ADS.ADS1115(tca[5])
        except:
            time.sleep(2)
    print("[FALLIMENTO] Impossibile inizializzare ADS dopo vari tentativi.")
    return None

ads = initADS()

for channel in range(8):
    if tca[channel].try_lock():
        print("Channel {}:".format(channel), end=
        "")
        addresses = tca[channel].scan()
        print([hex(address) for address in addresses if address != 0x70])
        tca[channel].unlock()

greenLeds = [LED(17), LED(24)]
redLeds = [LED(27), LED(23)]


def initBME():
    for i in range(5):
        try:
            return [adafruit_bme280.Adafruit_BME280_I2C(tca[2], address=0x76), adafruit_bme280.Adafruit_BME280_I2C(tca[3], address=0x76)]
        except:
            time.sleep(2)
    print("[FALLIMENTO] Impossibile inizializzare BME dopo vari tentativi.")
    return None
         
bme280_sensors = initBME()

app = Flask(__name__)

def get_percentage(cur_val, max_val, min_val):
    percentuale = (cur_val - min_val) / (max_val - min_val) * 100
    # opzionale: limita tra 0 e 100
    percentuale = max(0, min(100, percentuale))
    return percentuale

def get_wellness_score(temperature, humidity):
    def score_in_range(value, min_val, ideal_min, ideal_max, max_val):
        if value < min_val or value > max_val:
            return 0
        if ideal_min <= value <= ideal_max:
            return 100
        if value < ideal_min:
            return 100 * (value - min_val) / (ideal_min - min_val)
        else:
            return 100 * (max_val - value) / (max_val - ideal_max)

    temp_score = score_in_range(temperature, 10, 22, 28, 40)      # °C
    humidity_score = score_in_range(humidity, 30, 80, 90, 100)    # %

    wellness = (temp_score * 0.3) + (humidity_score * 0.7)
    
    # if wl < WATER_LEVEL or ml < MOISTURE_LEVEL:
    #     return 1

    return max(1, round(wellness))


def read_data():
    while True:
        try:
            
            t = [bme280_sensors[0].temperature, bme280_sensors[1].temperature]
            p = [bme280_sensors[0].pressure, bme280_sensors[1].pressure]
            h = [bme280_sensors[0].humidity, bme280_sensors[1].humidity]
            wl = AnalogIn(ads, ADS.P0)  # A0
            wl2 = AnalogIn(ads, ADS.P1)  # A1
            ml = AnalogIn(ads, ADS.P2)  # A2
            ml2 = AnalogIn(ads, ADS.P3)  # A2
            scores = [get_wellness_score(t[0], h[0]), get_wellness_score(t[1], h[1])]
            
            if scores[1] > 50:
                greenLeds[1].on()
                redLeds[1].off()
            else:
                redLeds[1].on()
                greenLeds[1].off()
                
            if scores[0] > 50:
                greenLeds[0].on()
                redLeds[0].off()
            else:
                redLeds[0].on()
                greenLeds[0].off()
            
            if is_half_hour():
                temperatures1 = update_file(t[0], FILE_PATH)
                temperatures2 = update_file(t[1], FILE_PATH2)
            else:
                temperatures1 = load_data(FILE_PATH)
                temperatures2 = load_data(FILE_PATH2)
            
            data = {'terrari': [
                {
                    'score': scores[0],
                    'temperatures': temperatures1,
                    't': t[0],
                    'p': p[0],
                    'h': h[0],
                    'wl': 70,
                    'mo': ml.value,
                },
                {
                    'score': scores[1],
                    'temperatures': temperatures2,
                    't': t[1],
                    'p': p[1],
                    'h': h[1],
                    'wl': get_percentage(wl2.value, WATER_LEVEL_MIN, WATER_LEVEL_MAX),
                    'mo': ml2.value
                }
            ]}
        except Exception as e:
            data = {"errore": str(e)}
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(2)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def index2():
    return render_template('index2.html')

@app.route('/stream')
def stream():
    return Response(read_data(), mimetype='text/event-stream')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
