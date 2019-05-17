#!/usr/bin/env python

"""
Plays and controls a Sonos music system with inputs from a 1957 Seeburg wallbox.

Has an 2x16 lcd display, rotary encoder for volume control, rgb led on the rotary control to indicate playstate,
and a pushbutton for selecting the sonos unit to play through.

"""

import SonosControl
import SonosHW
import RPi.GPIO as GPIO
import i2cCharLCD
import time

# LCD on the wallbox
WallboxLCD = i2cCharLCD.ExtendedAdafruitI2LCD()

# Sonos units
Units = SonosControl.SonosUnits(lcd=WallboxLCD, default_name='Kitchen')

# currently playing track
CurrentTrack = SonosControl.CurrentTrack(units=Units,lcd = WallboxLCD)

# Wallbox sonos player
SeeburgWallboxPlayer = SonosControl.WallboxPlayer(units=Units, current_track=CurrentTrack, lcd=WallboxLCD)

# The Seeburg wallbox
SeeburgWallbox = SonosHW.WallBox(pin=9, callback=SeeburgWallboxPlayer.play_selection)

# Playstate change LED
WallboxPlaystateLED = SonosControl.PlaystateLED(Units, green=6, blue=13, red=5)

# Volume Control
WallboxRotaryControl = SonosControl.SonosVolCtrl(units=Units, lcd=WallboxLCD,
                                                 vol_ctrl_led=WallboxPlaystateLED, up_increment=4, down_increment=5)
# Rotary Encoder
VolumeKnob = SonosHW.RotaryEncoder(pinA=11, pinB=7, rotary_callback=WallboxRotaryControl.change_volume)

# button on the volume control
VolumeButton = SonosHW.PushButton(button_pin=12, callback=WallboxRotaryControl.pause_play_skip,
                                  gpio_up_down='down', long_press=1, debounce=25)

# little black button on front of volume control box; used to change sonos unit
SelectUnitButton = SonosHW.SinglePressButton(pin=18, callback=Units.select_unit_single_press,
                                         gpio_up = 1, debounce=3000)

# Something to show on the screen when vol control box starts up
print('active unit: :', Units.active_unit_name)
WallboxLCD.display_text("Wallbox On", Units.active_unit_name, sleep=5)


while True:
    # Main program loop
    try:
        # change rotary encoder LED depending on play state
        WallboxPlaystateLED.play_state_LED()
        # display what is currently playing
        CurrentTrack.display_track_info(timeout=60)
        # check to see if display is timed out, turn off back light if it has
        WallboxLCD.check_display_timeout(timeout=60)
        # check to see if playstate LED should be turned off after 1/2 hour
        WallboxPlaystateLED.led_timeout()
        # no need to run this loop more than once every few seconds, so sleep.
        time.sleep(5)

    except KeyboardInterrupt:
        # do some cleanup on devices, etc
        GPIO.cleanup()                      # clean up GPIO on CTRL+C exit
        WallboxLCD.clean_up()               # clean up lcd, turn off backlight