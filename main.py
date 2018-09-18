import time
from datetime import datetime
import os


# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO

# Software SPI configuration:
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# STATE
freq = 0.5
timer = 0
on = True
readings = []


def reset(channel=False):
    os.system('clear')
    global timer
    timer = 0


def change_freq(channel=False):
    global freq
    if freq == 0.5:
        freq = 1
    elif freq == 1:
        freq = 2
    elif freq == 2:
        freq = 0.5


def stop(channel=False):
    global on, readings
    readings = []
    on = not on



def display(channel=False):
    print("FIRST FIVE READINGS SINCE LAST STOP")
    global readings
    for reading in readings:
        print(reading)


# PINS
GPIO.setmode(GPIO.BCM)

FREQ_PIN = 21
RESET_PIN = 20
STOP_PIN = 16
DISPLAY_PIN = 12

GPIO.setup(FREQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(FREQ_PIN, GPIO.RISING,
                      callback=change_freq, bouncetime=300)

GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(RESET_PIN, GPIO.RISING,
                      callback=reset, bouncetime=300)

GPIO.setup(STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(STOP_PIN, GPIO.RISING,
                      callback=stop, bouncetime=300)

GPIO.setup(DISPLAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(DISPLAY_PIN, GPIO.RISING,
                      callback=display, bouncetime=300)

# Hardware SPI configuration:
# SPI_PORT   = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


def convert_pot(adc_reading):
    return round((adc_reading/1024.0)*3.3, 1)


def convert_ldr(adc_reading):
    min_value = 30.0  # reading on ADC when no light
    norm = adc_reading-min_value

    max_value = 750.0  # reading on ADC with phone torch directly on it
    total = max_value-min_value
    if norm < 0:
        norm = 0
    elif norm > max_value:
        norm = total
    return round((norm/total)*100)


def convert_temp(adc_reading):
    voltage = adc_reading*3.3/1024.0
    ref_voltage = voltage - 0.5
    temp = ref_voltage/0.01
    return round(temp, 0)


def convert_timer(val):
    hours, rem = divmod(val, 3600)
    minutes, seconds = divmod(rem, 60)
    return ("{:0>2}:{:0>2}:{:02.0f}".format(int(hours), int(minutes), seconds))


print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
column_headers = ['Time', 'Timer', 'Pot', 'Temp', 'Light']
print('| {0:>8} | {1:>8} | {2:>6} | {3:>5} | {4:>6} |'.format(*column_headers))
print('-' * 57)
# Main program loop.
try:
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*8
        values[0] = datetime.now().strftime("%H:%M:%S")
        values[1] = convert_timer(timer)
        values[2] = convert_pot(mcp.read_adc(7))
        values[3] = convert_temp(mcp.read_adc(6))
        values[4] = convert_ldr(mcp.read_adc(5))

        if len(readings) <= 5:
            readings.append(
                '| {0:>8} | {1:>8} | {2:>4} V | {3:>5} | {4:>5}% |'.format(*values))

        # Print the ADC values.
        if on:
            print(
                '| {0:>8} | {1:>8} | {2:>4} V | {3:>5}C | {4:>5}% |'.format(*values))
        # Pause for half a second.
        timer += freq
        time.sleep(freq)

except KeyboardInterrupt:
    GPIO.cleanup()
