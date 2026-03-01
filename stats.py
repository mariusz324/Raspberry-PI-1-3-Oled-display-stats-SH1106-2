#!/usr/bin/env python3
import time
import psutil as PS
import socket
import os
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas

# --- WENTYLATOR ---
FAN_PIN = 4        
TEMP_THRESHOLD = 30 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

# --- WYŚWIETLACZ ---
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
try:
    font = ImageFont.truetype('/root/rpi_oled_stats/PixelOperator.ttf', 16)
except:
    font = ImageFont.load_default()

def draw_icons(draw):
    # LEWE IKONY (0-15)
    draw.rectangle((2, 2, 12, 9), outline=255) # Ethernet
    draw.rectangle((4, 9, 10, 11), outline=255)
    draw.rectangle((4, 19, 11, 26), outline=255, fill=255) # CPU
    for i in range(17, 29, 3):
        draw.line((1, i, 2, i), fill=255)
        draw.line((13, i, 14, i), fill=255)
    draw.rectangle((2, 36, 14, 42), outline=255) # RAM
    for i in range(4, 14, 4):
        draw.rectangle((i, 37, i+1, 38), fill=255)
    draw.polygon([(3, 51), (9, 51), (12, 54), (12, 61), (3, 61)], outline=255) # SD

    # PRAWE IKONY (120-128) - przesunięte na sam brzeg
    draw.ellipse((121, 23, 126, 27), outline=255) # Termometr
    draw.line((123, 17, 123, 23), fill=255)
    draw.line((120, 50, 126, 50), fill=255) # Klepsydra
    draw.line((120, 60, 126, 60), fill=255)
    draw.line((120, 50, 126, 60), fill=255)
    draw.line((126, 50, 120, 60), fill=255)

def get_uptime_formatted():
    t = int(time.time() - PS.boot_time())
    d, h, m = t // 86400, (t % 86400) // 3600, (t % 3600) // 60
    return f"{d}d {h}h {m}m" # Bez kropek, by zaoszczędzić miejsce

while True:
    try:
        temp_val = PS.sensors_temperatures()['cpu_thermal'][0].current
        GPIO.output(FAN_PIN, GPIO.HIGH if temp_val >= TEMP_THRESHOLD else GPIO.LOW)
    except: temp_val = 0

    with canvas(device) as draw:
        IP = socket.gethostbyname(socket.gethostname())
        CPU = f"{int(PS.cpu_percent())}%"
        TEMP = f"{temp_val:.1f}C" # Bez znaku stopnia, by nie nachodził na ikonę
        
        mem = PS.virtual_memory()
        # Poprawka wyświetlania 2G (round zamiast int)
        RAM_TOTAL = round(mem.total / (1024**3))
        RAM_TXT = f"{mem.percent}% {int(mem.used/1024**2)}M/{RAM_TOTAL}G"
        
        DISK = f"{PS.disk_usage('/').percent}%"
        UPTIME = get_uptime_formatted()

        draw_icons(draw)

        # POZYCJONOWANIE (przesunięte w lewo, by zwolnić miejsce po prawej)
        draw.text((20, 0),  IP, font=font, fill=255)
        draw.text((20, 16), CPU, font=font, fill=255)
        draw.text((68, 16), TEMP, font=font, fill=255) # Przesunięcie Temp w lewo
        draw.text((20, 32), RAM_TXT, font=font, fill=255)
        draw.text((20, 48), DISK, font=font, fill=255)
        draw.text((58, 48), UPTIME, font=font, fill=255) # Przesunięcie Uptime w lewo

    time.sleep(1.0)
