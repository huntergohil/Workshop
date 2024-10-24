from machine import Pin, I2C, ADC, Timer
from machine_i2c_lcd import I2cLcd
import utime
import urandom

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
addr = i2c.scan()[0]
lcd = I2cLcd(i2c, addr, 2, 16)

potent = ADC(26)

joy_vrx = ADC(27)
joy_vry = ADC(28)
joy_sw = Pin(22, Pin.IN, Pin.PULL_UP)  

key_switch = Pin(15, Pin.IN, Pin.PULL_UP)

sound_sensor = Pin(14, Pin.IN)

led = Pin(13, Pin.OUT) 

POT_TOLERANCE = 1000  

random_pot_target = urandom.randint(0, 65535)

spin_direction = urandom.choice(["clockwise", "counterclockwise"])

game_timer = None
time_left = 10  

def detect_spin(direction):
    spin_count = 0
    last_x = joy_vrx.read_u16()
    last_y = joy_vry.read_u16()

    while spin_count < 2:  
        x_value = joy_vrx.read_u16()
        y_value = joy_vry.read_u16()

        if direction == "clockwise":
            if last_x < x_value and last_y > y_value and (x_value - last_x > 1000) and (last_y - y_value > 1000):
                spin_count += 1
                lcd.clear()
                lcd.putstr("Keep Spinning!")

        elif direction == "counterclockwise":
            if last_x > x_value and last_y < y_value and (last_x - x_value > 1000) and (y_value - last_y > 1000):
                spin_count += 1
                lcd.clear()
                lcd.putstr("Keep Spinning!")

        last_x = x_value
        last_y = y_value

        utime.sleep(0.1) 

    return True

def countdown_callback(timer):
    global time_left, game_state
    if time_left > 0:
        time_left -= 1
    else:
        game_state = "game_over" 

game_state = "lock_door"

while True:
    pot_value = potent.read_u16()

    lcd.clear()

    if sound_sensor.value() == 1 and game_timer is None:
        lcd.putstr("Too Loud! Solve in 10 seconds!")
        led.value(1) 
        utime.sleep(1)
        game_timer = Timer() 
        game_timer.init(period=1000, mode=Timer.PERIODIC, callback=countdown_callback)

    if game_state == "lock_door":
        if key_switch.value() == 0:
            lcd.putstr("Lock The Door")
        else:
            game_state = "adjust_potentiometer"
        utime.sleep(0.5)
    elif game_state == "adjust_potentiometer":
        if abs(pot_value - random_pot_target) < POT_TOLERANCE:
            lcd.putstr("Potentiometer OK!")
            utime.sleep(1)
            game_state = "spin_joystick"
        else:
            lcd.putstr("Turn Potentiometer")
        utime.sleep(0.25)

    elif game_state == "spin_joystick":
        lcd.putstr(f"Spin {spin_direction}")
        utime.sleep(1)

        if detect_spin(spin_direction):
            lcd.clear()
            lcd.putstr("Spin Complete!")
            utime.sleep(1)
            game_state = "press_button"

    elif game_state == "press_button":
        lcd.clear()
        lcd.putstr("Turn The Key!")
        utime.sleep(0.5)

        if key_switch.value() == 0:
            lcd.clear()
            lcd.putstr("You win!")
            led.value(0) 
            utime.sleep(3) 
            break  

    elif game_state == "game_over":
        if key_switch.value() == 0:
            lcd.clear()
            lcd.putstr("You win!")
        else:
            lcd.clear()
            lcd.putstr("Game Over! You got caught!")
            led.value(0) 
            utime.sleep(3)

