#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import psutil as PS
import socket
import os
from PIL import Image, ImageDraw, ImageFont

# Importy dla sterownika SH1106 (wyświetlacz 1.3")
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

KB=1024
MB=KB*1024
GB=MB*1024

WIDTH = 128
HEIGHT = 64
FONTSIZE = 16
LOOPTIME = 1.0

def get_ipv4():
    ifaces=PS.net_if_addrs()
    for key in ifaces:
        if (key!="lo"):
            iface = ifaces[key]
            for addr in iface:
                if addr.family is socket.AddressFamily.AF_INET:
                    return "IP {0}".format(addr.address)
    return "IP ?"

# Konfiguracja wyświetlacza SH1106
try:
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial)
except Exception as e:
    print(f"Błąd inicjalizacji ekranu: {e}")
    exit(1)

# Czcionka - upewnij się, że plik PixelOperator.ttf jest w tym samym folderze
try:
    font = ImageFont.truetype('PixelOperator.ttf', FONTSIZE)
except:
    font = ImageFont.load_default()

while True:
    # Tworzymy czysty obraz do rysowania
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)

    IP = get_ipv4()
    CPU = "CPU {:.1f}%".format(round(PS.cpu_percent(),1))

    try:
        temps = PS.sensors_temperatures()
        TEMP = "{:.1f}°C".format(round(temps['cpu_thermal'][0].current,1))
    except:
        TEMP = "N/A"

    mem = PS.virtual_memory()
    MemUsage = "Mem {:d}/{:d}MB".format(int(mem.used/MB), int(mem.total/MB))

    root = PS.disk_usage("/")
    Disk = "Disk {:d}/{:d}GB".format(int(root.used/GB), int(root.total/GB))

    # Rysowanie tekstu
    draw.text((0, 0), IP, font=font, fill=255)
    draw.text((0, 16), CPU, font=font, fill=255)
    draw.text((80, 16), TEMP, font=font, fill=255)
    draw.text((0, 32), MemUsage, font=font, fill=255)
    draw.text((0, 48), Disk, font=font, fill=255)

    # Wyświetlenie obrazu na ekranie
    device.display(image)
    
    time.sleep(LOOPTIME)
