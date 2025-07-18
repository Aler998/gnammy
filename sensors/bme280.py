import board
import busio
import adafruit_bh1750

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bh1750.BH1750(i2c)
print("Luce:", sensor.lux)
