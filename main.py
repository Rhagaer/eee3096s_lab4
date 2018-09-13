import time
from datetime import datetime

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT   = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


def convert_pot(adc_reading):
    return round((adc_reading/1024.0)*3.3,1)

def convert_ldr(adc_reading):
    norm = adc_reading-30
    total = 750.0-30.0
    return round((norm/total)*100)


print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
column_headers = ['Time', 'Timer', 'Pot', 'Temp', 'Light']
print('| {0:>8} | {1:>8} | {2:>6} | {3:>4} | {4:>6} |'.format(*column_headers))
print('-' * 57)
# Main program loop.
timer = 0
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    values[0] = time.strftime('%H:%M:%S')
    values[1] = datetime.fromtimestamp(timer).strftime('%H:%M:%S')
    values[2] = convert_pot(mcp.read_adc(7))
    values[3] = mcp.read_adc(6)
    values[4] = convert_ldr(mcp.read_adc(5))

    # Print the ADC values.
    print('| {0:>8} | {1:>8} | {2:>4} V | {3:>4} | {4:>5}% |'.format(*values))
    # Pause for half a second.
    time.sleep(2)
