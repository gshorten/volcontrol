

import soco
import time

active = soco.discovery.by_name('Portable')
old_playstate = ""

# print out the events as they arise
while True:

    # loop continuously to listen for events
    playstate = active.device.get_current_transport_info()
    if playstate != old_playstate:
       print(playstate)

    old_playstate = playstate
    time.sleep(.5)



