# -*- coding: utf-8 -*-

import network
import sys
import time

def getip(net_name, net_pass):
    
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        sta_if.active(True)
        
        try:
            sta_if.config(dhcp_hostname="test")
            sta_if.connect(net_name, net_pass)
        except Exception as err:
            sta_if.active(False)
            print("Error:", err)
            sys.exit()
        print("Connecting", end="")
        n = 0
        while not sta_if.isconnected():
            print(".", end="")
            time.sleep(1)
            n += 1
            if n == 200:
                break
        if n == 200:
            sta_if.active(False)
            print("\nGiving up! Not connected!")
            return ""
        else:
            print("\nNow connected with IP: ", sta_if.ifconfig()[0])
            return sta_if.ifconfig()[0]
    else:
        print("Already Connected. ", sta_if.ifconfig()[0])
        return sta_if.ifconfig()[0]