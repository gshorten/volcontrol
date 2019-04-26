#!/usr/bin/env python
import SonosHW
import SonosControl
import RPi.GPIO as GPIO
import soco
import time
import Adafruit_CharLCD as LCD


# this is morphing into my new OOP based volume control
# RGBRotaryEncoder is a class for a generic RGB Rotary Encoder.

# NOTE I had to edit soco core.py module to fix group discovery to make by_name and other functions work
# see patch file text below... i manually edited "for group_element in tree.findall('ZoneGroup')
# and replaced it with the following patch line.  This fixed discovery methods.
# --- soco/core.py	(revision 671937e07d7973b78c0cbee153d4f3ad68ec48c6)
# +++ soco/core.py	(date 1554404884029)
# @@ -949,7 +949,7 @@
#          self._all_zones.clear()
#          self._visible_zones.clear()
#          # Loop over each ZoneGroup Element
# -        for group_element in tree.findall('ZoneGroup'):
# +        for group_element in tree.find('ZoneGroups').findall('ZoneGroup'):
#              coordinator_uid = group_element.attrib['Coordinator']
#              group_uid = group_element.attrib['ID']
#              group_coordinator = None


# -------------------------- Main part of program -------------------

# assign sonos player to unit object
#todo use a second rotary control to select sonos units!
# for now it is hard coded :-(
#unit = soco.discovery.by_name("Garage"
unit = soco.discovery.by_name("Portable")
print(unit, unit.player_name)

# create LED for the volume knob
VolCtrlLED = SonosHW.KnobLED(green=22, red=27, blue=17)

# create play state change LED object
# it changes the colour of the VolCtrlLED based on if the sonos is paused or playing
VolCtrl_PlaystateLED = SonosControl.PlaystateLED(unit,VolCtrlLED)

# This changes the volume of the sonos unit
# contains the callback method called by the PiZeroEncoder object
# it's not called directly, but via the callback when the volume knob is turned (or pushed)
PiZeroSonosVolumeKnob = SonosControl.SonosVolCtrl(unit, VolCtrlLED, up_increment=4, down_increment=5)

# create rotary encoder instance, it decodes the rotary encoder and generates the callbacks for the VolumeKnob
PiZeroEncoder = SonosHW.RotaryEncoder(pinA=19, pinB=26, button=4, callback=PiZeroSonosVolumeKnob.change_volume)

# make track info instance
PiVolTrackInfo = SonosControl.TrackInfo(unit)

# make generic adafruit lcd instance, uses i2C interface so no parameters required!
TwoLineLCD = LCD.Adafruit_CharLCDPlate()
# make a sonos version; this has all the custom functions for the adafruit two line display
SonosLCDDisplay = SonosHW.ExtendedLCD(TwoLineLCD)

while True:
    try:
        VolCtrl_PlaystateLED.play_state_LED()
        # change LED knob LED depending on play state
        # the volume control triggers methods based on interrupts, changing the colour of the LED has to be polled in
        # in the main program loop
        # display what is currently playing

        SonosLCDDisplay.display_stuff('This is', 'A test')

        #todo see if we can use soco.events to trigger light change with a callback function.
        # but probably unecessary as this method is faster than the sonos app on phone :-)

    except KeyboardInterrupt:
        PiVolTrackInfo.lcd_cleanup()
        GPIO.cleanup()  # clean up GPIO on CTRL+C exit