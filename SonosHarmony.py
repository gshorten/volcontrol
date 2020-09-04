#!/usr/bin/env python
"""
Module for controlling the Logitech Harmony hubs / remotes from my Sonos wallbox controllers
muchas gracias to EScape 2018 and others for figuring this all out
"""

import harmony
import time


class HarmonyHubDevice:
    """
    Great Room Logitech Harmony hub
    subclass of harmony.py
    pass instance of this class into SonosVolControl in SonosControl, use volume control on wallbox controller to
    change TV volume when it's not being used for controlling the volume of the sonos system.
    """

    def __init__(self, ip="192.168.1.25", rport="14255516", device="60692019"):
        """
        :param ip:      ip address of the harmony hub
        :type ip:       str
        :param rport:   remote port of the harmony device, note NOT the "port" - its "remoteId"
        :type rport:    str
        :param device:  the harmony number of the device.  On my system 60692019 is the Onkyo reciever
        :type device:   str
        """
        self.device = device
        self.ip = ip
        self.rport = rport
        # the harmonysock class was a super class but we have to recreate it every time we reference it because it times
        #   out, I don't know how to stop this from happening.
        self.onkyo = harmony.harmonysock(host=self.ip, hubid=self.rport, timeout=30)

    def volume_up(self):
        """
        turns the volume up on the selected device, one increment....have no idea how much this is but on tv shows
        one number up.
        :return:
        :rtype:
        """
        # we have to make the harmony unit object inside this class because we have to refresh it every time
        #    we call the volume up or down methods!!!
        # self.harmony_unit = harmony.harmonysock(self.ip, self.rport)
        print("turning TV volume up")
        try:
            self.onkyo.sendkey(self.device, key="VolumeUp")
        except:
            # if sock has died we have to recreate it and issue command again
            print("error changing volume up")
            self.onkyo = harmony.harmonysock(host=self.ip, hubid=self.rport, timeout=30)
            self.onkyo.sendkey(self.device, key="VolumeUp")
        time.sleep(0.01)

    def volume_down(self):
        """
        turns volume down
        :return:
        :rtype:
        """
        # we have to make the harmony unit object inside this class because we have to refresh it every time
        #    we call the volume up or down methods!!!
        # self.harmony_unit = harmony.harmonysock(self.ip, self.rport)
        print("turning TV volume down")
        try:
            self.onkyo.sendkey(self.device, key="VolumeDown")
        except:
            print("error changing voluem down")
            self.onkyo = harmony.harmonysock(host=self.ip, hubid=self.rport, timeout=30)
            self.onkyo.sendkey(self.device, key="VolumeDow")
        time.sleep(0.01)

    def Mute(self):
        """
        Mutes audio.  turning volume up or down unmutes.
        :return:
        :rtype:
        """
        # we have to make the harmony unit object inside this class because we have to refresh it every time
        #    we call the volume up or down methods!!!
        # self.harmony_unit = harmony.harmonysock(self.ip, self.rport)
        pass
