#!/usr/bin/env python3

"""
Plays and controls a Sonos music system with inputs from a 1957 Seeburg wallbox.

Has an 2x16 OLED display, rotary encoder for volume control, rgb playstate_led on the rotary control to indicate playstate,
and a pushbutton for selecting the sonos unit to play through.  It's completely event driven, except for some loops that
run in separate threads that listen for changes on the currently selected sonos unit.

When nothing is playing on the Sonos and the display is timed out the display shows the current and forecast weather.

"""

import SonosControl
import SonosHW
import OLED128X64
import Weather
import SonosHarmony

# Create all the objects required.  These are all event driven, there is no main program loop

# weather updater
WeatherUpdater = Weather.UpdateWeather(update_freq=10)
# LCD on the wallbox
WallboxLCD = OLED128X64.OLED(
    WeatherUpdater, showing_weather=False, char_width=24, pixels_high=64
)
# Sonos units
Units = SonosControl.SonosUnits(display=WallboxLCD, default_name="Kitchen")
# on start up trigger rfid read of loaded page manually
# Wallbox sonos player
SeeburgWallboxPlayer = SonosControl.WallboxPlayer(units=Units, display=WallboxLCD)
# The Seeburg wallbox
SeeburgWallbox = SonosHW.WallBox(pin=9, callback=SeeburgWallboxPlayer.play_selection)
# Playstate change LED
WallboxPlaystateLED = SonosControl.PlaystateLED(
    Units, green=6, blue=13, red=5, on="low"
)
# Display updater
Updater = SonosControl.SonosDisplayUpdater(
    Units, WallboxLCD, WallboxPlaystateLED, WeatherUpdater
)
# Onkyo receiver on the Logitech Harmony hub, use this to change volume when volume control is not being used for Sonos
HarmonyTV = SonosHarmony.HarmonyHubDevice()
# Volume Control
WallboxRotaryControl = SonosControl.SonosVolCtrl(
    units=Units,
    updater=Updater,
    display=WallboxLCD,
    vol_ctrl_led=WallboxPlaystateLED,
    weather=WeatherUpdater,
    tv=HarmonyTV,
    up_increment=4,
    down_increment=5,
)
# Rotary Encoder (for the volume control)
VolumeKnob = SonosHW.RotaryEncoder(
    pinA=11, pinB=7, rotary_callback=WallboxRotaryControl.change_volume
)
# button on the volume control
PausePlayButton = SonosHW.TimedButtonPress(
    pin=12, callback=WallboxRotaryControl.pause_play_skip, long_press_sec=1
)
# Button that manually selects wallbox pages
SelectPageSetButton = SonosHW.ButtonPress(
    pin=18, callback=SeeburgWallboxPlayer.select_wallbox_pageset
)
# display time out loop
OLEDTimeOut = SonosControl.DisplayTimeOut(WallboxLCD, Updater, timeout=5)
# RFID reader that gets the page tag number and switches the wallbox page set
PageReader = SonosHW.RFIDReader(
    callback=SeeburgWallboxPlayer.get_wallbox_tracks, port="/dev/ttyUSB0"
)

# Something to show on the screen when vol control box starts up
print("active unit: :", Units.active_unit_name)

# get list of sonos units, print list
Units.get_units()
