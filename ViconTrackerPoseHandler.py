#!/usr/bin/env python
"""
============================================
viconPose.py - Pose Handler for Vicon System
============================================
"""

import sys, time
from numpy import *
import socket
import struct
import threading

import os

class ViconTrackerPoseHandler(object):
    def __init__(self, executor, shared_data,host,port,VICON_name):
        """
        Pose handler for VICON system

        host (string): The ip address of VICON system (default="")
        port (int): The port of VICON system (default=51001)
        VICON_name (string): The name of the robot in VICON system (default="SubjectName")
        """
        self.host = host
        self.port = port
        self.VICON_name = VICON_name

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print "af_inet=",socket.AF_INET, "sock_dgram=" , socket.SOCK_DGRAM
        print "Connecting..."
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
	
	self.x = 0
        self.y = 0
        self.o = 0
        self.thread = threading.Thread(target=self.updatePose)
	
        self.thread.daemon = True
	
        self.thread.start()

    def updatePose(self):
        while True:
            try:
            	data, addr = self.s.recvfrom(256)
            except:
            	print "error "
            
            body = struct.unpack("<d24s28d", data)

            (self.t, self.x, self.y, self.o) = [body[0]/100, body[2]/1000, body[3]/1000, body[7]]

    def _stop(self):
        print "Vicon pose handler quitting..."
        self.thread.join()
        print "Terminated."

    def getPose(self, cached=False):
        return array([self.x, self.y, self.o])

if __name__ == "__main__":

    # replace the port number and device name in the following command to run the code
    a = ViconTrackerPoseHandler(None, None, "",51013, "Ollie_white")
    
    while(1):
	print "Ollie_white " ,a.getPose()
    	time.sleep(5)
    print a.getPose()
