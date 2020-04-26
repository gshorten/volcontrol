
"""
Adafruit OLED Display, 128 X 64
"""

import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import digitalio
import threading
import SonosUtils
import datetime

class OLED:
    """
    Tiny little Adafruit OLED display
    Can display 2 - 4 number_of_lines of text, up to 16 characters wide with decent legibility.

    """
    def __init__(self, weather_updater, showing_weather = True, pixels_wide=128, pixels_high=32,
                 font_size=14, lines=3, char_width = 26):
        '''

        :param weather_updater:     Weather class
        :type weather_updater:      object
        :param showing_weather:     if true then show weather info periodically when display is timed out
        :type showing_weather:      bool
        :param timeout_on:          if true then display timeout is active
        :type timeout_on:           bool
        :param timeout:             time that display is on before timing out (turning off)
        :type timeout:              int seconds
        :param pixels_wide:         width of display in pixels
        :type pixels_wide:          int
        :param pixels_high:         height of display in pixels
        :type pixels_high:          int
        :param font_size:           size of font in points
        :type font_size:            int
        :param lines:               number of lines to display
        :type lines:                int
        :param char_width:          how many characters wide to display
        :type char_width:           int
        '''


        # Create the I2C interface.
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create the SSD1306 OLED class.
        # The first two parameters are the pixel width and pixel height.  Change these
        # to the right size for your display!
        reset_pin = digitalio.DigitalInOut(board.D20)
        self.disp = adafruit_ssd1306.SSD1306_I2C(pixels_wide, pixels_high, i2c, reset=reset_pin)
        # First define some constants to allow easy resizing of shapes.
        self.font_size = font_size
        self.lines = lines
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        padding = -1
        self.top = padding
        self.bottom = self.height - padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0
        self.char_wide = char_width
        self.draw = ImageDraw.Draw(self.image)
        self.display_start_time = time.time()
        self.showing_weather = showing_weather
        # different fonts that seem to work ok. LiberationSansNarrow-Regular seems to be the best
        # self.font = ImageFont.load_default()
        # self.font = ImageFont.truetype('/usr/share/fonts/truetype/piboto/PibotoCondensed-Regular.ttf', self.font_size)
        # self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', self.font_size)
        # self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf', self.font_size)
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Regular.ttf', self.font_size)
        # flag for determining if display is is_busy or not
        self.is_busy = False
        self.timed_out = False
        self.weather_updater = weather_updater
        # self.timeout = timeout
        # if timeout_on == True then start display time out loop in seperate thread
        # self.timeout_on = timeout_on
        # if self.showing_weather:
        #     self.timer_thread = threading.Thread(target=self.display_timeout)
        #     self.timer_thread.start()

    def no_display(func):
        # decorator to modify display_text function because display is temporarily broken.
        def wrapper():
            print('no display decorator instead of display')
        return wrapper

    @no_display
    def clear_display(self):
        '''
        clears the display - - for OLED this means displaying black box, no pixels lit
        '''

        print('clearing the display')
        # Clear display.
        self.disp.fill(0)
        self.disp.show()
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(self.image)
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    @no_display
    def display_text(self, line1, line2 = "", line3="", showing_info = True, sleep=0):
        """
        Displays two strings.  If display is set up to show 3 number_of_lines, the first string is split over the first two
        number_of_lines.  If it is setup to display 4 number_of_lines, the first line is displayed on the first two number_of_lines, the second string
        is split up over the 3rd and 4th number_of_lines.
        :param line1:   first line to display
        :type line1:    str
        :param line2:   second line to display
        :type line2:    str
        :param line3:   third line to display
        :type line3:    str
        :param sleep:   not used for OLED; more for lcd displays that need time to write to display
        :type sleep:    int seconds
        """
        try:
            if self.is_busy:
                # if the display is busy don't try to write to it.  This is left over from lcd type displays
                #   that seem to break if you try to write to display too quickly successivly.
                print("Display is is_busy")
                return
            self.is_busy = True
            line1 = SonosUtils.center_text(line1,self.char_wide)
            line2 = SonosUtils.center_text(line2,self.char_wide)

            if showing_info:
                # print extra line of information - time and temperature
                infoline = time.strftime("%b %-d %-I:%M %p") + " " + SonosUtils.get_outside_temp() + "c"
                line3 = SonosUtils.center_text(infoline,self.char_wide)
            else:
                line3 = line3

            print("Updating Display")
            print(line1)
            print(line2)
            print(line3)
            self.clear_display()
            #  print('displaying lines on OLED')
            self.draw.text((self.x, self.top + 1),line1, font=self.font, fill=255)
            self.draw.text((self.x, self.top + self.font_size + 4), line2, font=self.font, fill=255)
            self.draw.text((self.x, self.top + 2*self.font_size + 8), line3, font=self.font, fill=255)
            # Display image.
            self.disp.image(self.image)
            self.disp.show()
            self.display_start_time = time.time()
            time.sleep(sleep)
            self.is_busy = False
            self.timed_out = False

        except Exception as e:
            print("Error writing to OLED display: ", e)



class NoDisplay:

    def __init__(self,weather_updater, showing_weather = True, pixels_wide=128, pixels_high=32,
                 font_size=14, lines=3, char_width = 26):
        self.font_size = font_size
        self.lines = lines
        self.width = 128
        self.height = 64
        self.is_busy = False
        self.timed_out = False

    def display_text(self, line1, line2 = "", line3="", showing_info = True, sleep=0):
        print("no display, displaying nothing :-(")
        return

    def clear_display(self):
        print("no display, not clearing")
        return
