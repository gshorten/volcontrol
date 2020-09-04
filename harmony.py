#!/usr/bin/python3
#
# Logitech Harmony Class using websocket instead of old (removed) api
# Credit for finding/sharing knowledge about the api goes to:
# 	https://github.com/jlynch630/Harmony.NET
# 	https://github.com/chadcb/harmonyhub
#
# This is a very early version. Consider it Alpha
#
# Written by: EScape 2018

import json
import time
import requests
import websocket
from websocket import create_connection


class harmonysock:
    def __init__(self, host, port="8088", protocol="http", hubid="", timeout=30):
        self.hub_ip = host
        self.hub_port = port
        self.harmony_api = "http://" + self.hub_ip + ":" + self.hub_port
        self.timeout = timeout
        if hubid != "":
            self.hub_id = hubid
        else:
            self.hub_id = self.gethubid()
        print("hubid:", self.hub_id)
        self.hubsocket = create_connection(
            "ws://"
            + self.hub_ip
            + ":"
            + self.hub_port
            + "/?domain=svcs.myharmony.com&hubId="
            + self.hub_id
        )
        self.cacheconfig = ""

    def hubconfig(self, refresh=False):
        if self.cacheconfig == "" or refresh:
            self.cacheconfig = self.getconfig()
        return self.cacheconfig

    def startactivity(self, activity):
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "Origin": "http//:localhost.nebula.myharmony.com",
        }
        response = ""
        try:
            response = requests.post(
                self.harmony_api,
                json={
                    "cmd": "harmony.activityengine?runactivity",
                    "params": {"activityId": activity},
                },
                headers=headers,
            )
            print(response.text)
        except:
            return False
        if response.status_code == 200:
            return True
        else:
            return False

    def gethubid(self):
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "Origin": "http//:localhost.nebula.myharmony.com",
        }
        r = requests.post(
            self.harmony_api,
            json={"id": 111, "cmd": "connect.discoveryinfo?get", "params": {}},
            headers=headers,
        )
        hub_data = json.loads(r.text)
        hub_id = hub_data["data"]["remoteId"]
        return hub_id

    def getconfig(self):
        payload = {}
        # payload['hubId']=self.hub_id #Doesn't even need the hubid?
        payload["timeout"] = self.timeout
        payload["hbus"] = {}
        payload["hbus"][
            "cmd"
        ] = "vnd.logitech.harmony/vnd.logitech.harmony.engine?config"
        payload["hbus"]["id"] = "0"
        payload["hbus"]["params"] = '{"verb":"get"}'
        self.hubsocket.send(json.dumps(payload))
        hubsocket_data = self.hubsocket.recv()
        hub_data = json.loads(hubsocket_data)
        return hub_data["data"]

    def getstate(self):
        payload = {}
        # payload['hubId']=self.hub_id #Doesn't even need the hubid?
        payload["timeout"] = self.timeout
        payload["hbus"] = {}
        payload["hbus"]["cmd"] = "vnd.logitech.connect/vnd.logitech.statedigest?get"
        payload["hbus"]["id"] = "0"
        payload["hbus"]["params"] = '{"verb":"get","format":"json"}'
        self.hubsocket.send(json.dumps(payload))
        hubsocket_data = self.hubsocket.recv()
        hub_data = json.loads(hubsocket_data)
        return hub_data["data"]

    def currentactivity(self):
        state = self.getstate()
        return state["activityId"]

    def listactivities(self):
        base = self.hubconfig()["activity"]
        list = {}
        for item in base:
            list[item["label"]] = item["id"]
        return list

    def listdevices(self):
        base = self.hubconfig()["device"]
        list = {}
        for item in base:
            list[item["label"]] = item["id"]
        return list

    def getactivitybyname(self, name):
        all = self.listactivities()
        if name in all:
            return all[name]
        else:
            return None

    def startactivity(self, activity):
        # If the activity is a number it is assumed to be an ID, otherwise a label (name)
        if activity.isdigit():
            activityid = activity
        else:
            activityid = self.getactivitybyname(activity)
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "Origin": "http//:localhost.nebula.myharmony.com",
        }
        try:
            response = requests.post(
                self.harmony_api,
                json={
                    "cmd": "harmony.activityengine?runactivity",
                    "params": {"activityId": activityid},
                },
                headers=headers,
            )
        except:
            return False
        if response.status_code == 200:
            return True
        else:
            return False

    def sendkey(self, device="", key="", hold=False):
        stroke = {}
        stroke["deviceId"] = device
        stroke["command"] = key
        stroke["type"] = "IRCommand"
        payload = {}
        # payload['hubId']=self.hub_id #Doesn't even need the hubid?
        payload["timeout"] = self.timeout
        payload["hbus"] = {}
        payload["hbus"][
            "cmd"
        ] = "vnd.logitech.harmony/vnd.logitech.harmony.engine?holdAction"
        payload["hbus"]["id"] = "222"
        payload["hbus"]["params"] = {}
        payload["hbus"]["params"]["action"] = json.dumps(stroke)
        if hold:
            payload["hbus"]["params"]["status"] = "hold"
        else:
            payload["hbus"]["params"]["status"] = "press"
        payload["hbus"]["params"]["timestamp"] = "0"
        self.hubsocket.send(json.dumps(payload))
        return True
