import os, sys, time

sys.path.append('')
sys.path.append('.')

# chdir to "/flash" - loading from SD card breaks custom model functionality
devices = os.listdir("/")
if "sd" in devices:
    sys.path.append('/sd')
os.chdir("/flash")
sys.path.append('/flash')

print("[cyberEye] init end") # for IDE
for i in range(200):
    time.sleep_ms(1) # wait for key interrupt(for maixpy ide)
del i

# check IDE mode
ide_mode_conf = "/flash/ide_mode.conf"
ide = True
try:
    f = open(ide_mode_conf)
    f.close()
except Exception:
    ide = False

if ide:
    os.remove(ide_mode_conf)
    from machine import UART
    import lcd
    lcd.init(color=lcd.PINK)
    repl = UART.repl_uart()
    repl.init(1500000, 8, None, 1, read_buf_len=2048, ide=True, from_ide=False)
    sys.exit()


# MaixCube PMU AXP173
from machine import I2C
i2c_bus = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
axp173_addr = 0x34
dev_list = i2c_bus.scan()

if axp173_addr in dev_list:
    # print("I2C:" + str(i2c_bus.scan()))
    i2c_bus.writeto_mem(axp173_addr, 0x46, 0xFF)  # Clear the interrupts
    i2c_bus.writeto_mem(axp173_addr, 0x33, 0xC1)  # set target voltage and current of battery(axp173 datasheet PG.)

    # REG 10H: EXTEN & DC-DC2 control
    reg = (i2c_bus.readfrom_mem(axp173_addr, 0x10, 1))[0] # read reg value
    i2c_bus.writeto_mem(axp173_addr, 0x10, reg & 0xFC)
    del reg

del dev_list
del axp173_addr
del i2c_bus
del I2C


import gc
import machine
from board import board_info
from fpioa_manager import fm
from pye_mp import pye
from Maix import FPIOA, GPIO


# detect boot.py
main_py = '''
from fpioa_manager import *
import os, Maix, lcd, image, time
from Maix import FPIOA, GPIO

first_boot = "first_boot" in os.listdir("/flash")

boot_pressed = 0
test_pin=16
fpioa = FPIOA()
fpioa.set_function(test_pin,FPIOA.GPIO7)
test_gpio=GPIO(GPIO.GPIO7,GPIO.IN)

lcd.init(color=(255,0,0))
lcd.rotation(1)

if first_boot:
    lcd.display(image.Image('first_boot.jpg'))
    os.remove("/flash/first_boot")
    time.sleep(2)
    from preloaded import *
else:
    lcd.display(image.Image('logo.jpg'))
    start_time =  time.ticks_ms()
    while (time.ticks_ms() - start_time) < 2000:
        if test_gpio.value() == 0:
            boot_pressed += 1
            time.sleep(0.5)
            lcd.draw_string(0,0,str(boot_pressed),lcd.RED, lcd.BLACK)
        if boot_pressed == 2:
            from preloaded import *
    
try:
    from user import *
except Exception as e:
    lcd.clear()
    lcd.draw_string(0,0,str(e),lcd.RED, lcd.BLACK)
    raise


'''

flash_ls = os.listdir()
if not "main.py" in flash_ls:
    f = open("main.py", "wb")
    f.write(main_py)
    f.close()
del main_py

flash_ls = os.listdir("/flash")
try:
    sd_ls = os.listdir("/sd")
except Exception:
    sd_ls = []
if "cover.boot.py" in sd_ls:
    code0 = ""
    if "boot.py" in flash_ls:
        with open("/flash/boot.py") as f:
            code0 = f.read()
    with open("/sd/cover.boot.py") as f:
        code=f.read()
    if code0 != code:
        with open("/flash/boot.py", "w") as f:
            f.write(code)
        import machine
        machine.reset()

if "cover.main.py" in sd_ls:
    code0 = ""
    if "main.py" in flash_ls:
        with open("/flash/main.py") as f:
            code0 = f.read()
    with open("/sd/cover.main.py") as f:
        code = f.read()
    if code0 != code:
        with open("/flash/main.py", "w") as f:
            f.write(code)
        import machine
        machine.reset()

try:
    del flash_ls
    del sd_ls
    del code0
    del code
except Exception:
    pass

banner = '''
 _ _ _  __     __  ___     _____   ____     _____  __     __  _____
/  ___| \ \   / / |  _ \  |  _ _| | _  \   |  _ _| \ \   / / |  _ _|
| /      \ \_/ /  | |_|/  | |_ _  | \| /   | |_ _   \ \_/ /  | |_ _
| |       \   /   |  _  \ |  _ _| |  _ |   |  _ _|   \   /   |  _ _|
| \___     | |    | |_| | | |_ _  | | \ \  | |_ _     | |    | |_ _
\_ _ _|    |_|    |_ _ /  |_ _ _| |_|  \_\ |_ _ _|    |_|    |_ _ _|

Official Site : https://www.tinkergen.com
Wiki          : https://docs.tinkergen.com
'''
print(banner)
del banner

