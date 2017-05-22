#!/usr/bin/python
from bluepy import btle
import struct
import time
import BB8_driver
import sys
import ViconTrackerPoseHandler
import math
import threading
#import sphero

def bot_movement( botOb, viconOb, points = [] ):
	try:
		bb8 = botOb	
		a = viconOb
		bb8.set_rgb_led(0,255,0,0,False)

		time.sleep(2)

		init_heading = detect_bot_zero(bb8, a)
		for point in points:	
			move_to_dest(bb8, a, point[0], point[1], init_heading)
		bb8.disconnect()
	except:
		print "something is wrong"

def moveBot(bb8, v, w):

	L = 0.08154*100
	
	vRight = (v*2 + w*L)/2*4
	vLeft = (v*2 - w*L)/2*4
	bb8.circle(vLeft, vRight, False)

def moveBotScaled(bb8, v, w):

	L = 0.08*100
	
	vRight = (v*2 + w*L)/2
	vLeft = (v*2 - w*L)/2

	if w==0:
		w = 0.001
	k = float(v)/w
	l = 8
	if v*w > 0:
		if abs(vRight) > 284:
			vRight = 284 if vRight>0 else -284
			vLeft = (2*k-l) * vRight/ (2*k+l) 
		
		elif abs(vRight) < 165:
			vRight = 165 if vRight>0 else -165
			vLeft = (2*k - l) * vRight/ (2*k+l) 
		
		"""
		elif abs(vLeft) < 142:
			vLeft = 142 if vLeft>0 else -142
			vRight = (2*k + l) * vLeft/ (2*k-l) 
		"""
	elif v*w < 0:
		if abs(vLeft) > 284:
			vLeft = 284 if vLeft>0 else -284
			vRight = (2*k + l) * vLeft / (2*k - l)
				
		if abs(vLeft) < 165:
			vLeft = 165 if vLeft>0 else -165
			vRight = (2*k+l) * vLeft / (2*k - l)
		
		"""
		elif abs(vRight)<142:
			vRight = 142 if vRight>0 else -142
			vLeft = (2*k - l) * vRight / (2*k + l)
		"""	
	if abs(vLeft) < 24:
		vLeft = 0
	if abs(vRight) < 24:
		vRight = 0
	
	print "vLeft, vRight", vLeft, vRight
	bb8.circle_scaled(vLeft, vRight, False)

def move_try(bb8, a, x, y):
	"""
Function tomove bot to a particular destination

Parameters: 
	BB8_driver Object
	ViconTrackerPoseHandler object
	x coordinate of the bot
	y coordinate of the bot
	"""
	count=0
	""" some random thought - but may be not needed now."""	
	while 1:
		
		
		pose = a.getPose()
		curr_x = pose[0]
		curr_y = pose[1]
		if math.sqrt((curr_x-x)**2 + (curr_y-y)**2) < 0.1:
			bb8.roll(0, 0, 0, False)
			break;
		# calculate heading angle
		phi = math.atan2((y-curr_y),(x-curr_x)) # -pi to pi
		theta = pose[2]
		net_angle = phi - theta
		vbx = math.cos(net_angle)*math.sqrt((curr_x-x)**2 + (curr_y-y)**2)*100
		vby = math.sin(net_angle)*math.sqrt((curr_x-x)**2 + (curr_y-y)**2)*100
		radius = 10
		w = vby/radius
		moveBot(bb8, vbx, w)
		time.sleep(0.05)
		
def move_scaled(bb8, a, x, y):
	"""
Function tomove bot to a particular destination

Parameters: 
	BB8_driver Object
	ViconTrackerPoseHandler object
	x coordinate of the bot
	y coordinate of the bot
	"""
	count=0
	""" some random thought - but may be not needed now."""	
	while 1:
		
		print(count)
		pose = a.getPose()
		curr_x = pose[0]
		curr_y = pose[1]
		if math.sqrt((curr_x-x)**2 + (curr_y-y)**2) < 0.1:
			bb8.roll(0, 0, 0, False)
			break;
		# calculate heading angle
		phi = math.atan2((y-curr_y),(x-curr_x)) # -pi to pi
		theta = pose[2]
		#if previous_theta and abs(theta - previous_theta) > 2:
			#theta = previous_theta 
			#bb8.set_stablization(0x01, False)
			#print "***************************stabilised*************", theta
			#moveBotScaled(bb8, 0, 0.001)
			#time.sleep(0.2)
			#previous_theta = theta
			#continue
		net_angle = phi - theta
		print "net_angle, theta", net_angle, theta
		#velocities, vbx and vby are in cm/s		
		vbx = math.cos(net_angle)*math.sqrt((curr_x-x)**2 + (curr_y-y)**2)*100
		vby = math.sin(net_angle)*math.sqrt((curr_x-x)**2 + (curr_y-y)**2)*100
		count += 1
		radius = 10  #in cm 
		w = vby/radius
		moveBotScaled(bb8, vbx, w)
		time.sleep(0.1) 

def detect_bot_zero(bb8, a):
	bb8.roll(50, 0, 1, False)
	time.sleep(1)
	init_pose = a.getPose()
	print "init_pose is:", init_pose
	bb8.roll(0, 0, 1, False)
	return init_pose[2]

def move_to_dest(bb8, a, x, y, init_heading):
	"""
	Function to move bot to a particular destination given by a combination of x, y axis positions

	Parameters: 
		BB8_driver Object
		ViconTrackerPoseHandler object
		x coordinate of the bot
		y coordinate of the bot
	"""
	count=0
	# initializing the heading angle of the bot to 0 (in the local frame of bot)
	heading = 0
	while 1:
		pose = a.getPose()
		curr_x = pose[0]
		curr_y = pose[1]
		if math.sqrt((curr_x-x)**2 + (curr_y-y)**2) < 0.25:
			bb8.roll(0, int(heading), 0, False)
			break;
		# calculate heading angle of the bot with respect ot the global frame of viconTracker

		angle = math.atan2((y-curr_y),(x-curr_x)) # -pi to pi
		
		heading = (math.degrees(-angle + init_heading)+360)%360
		
		bb8.roll(0, int(heading), 1, False)
		bb8.roll(51, int(heading), 1, False)
		time.sleep(0.01)
		
'''
1. Create an object of ollie driver
2. Connect to the bot
'''

bb8 = BB8_driver.Sphero()
bb8.connect()

bb8.start()
bb8.join()

Ollie_white_address = "FF:9D:38:AE:A9:51"
### Connect with Ollie_white
wb8 = BB8_driver.Sphero(address = Ollie_white_address)
wb8.connect()

wb8.start()
wb8.join()

'''If unable to connect to the bot'''
if False:
    print "Could not connect"
    

print "Starting to blink"

'''Blink the ollies'''
bb8.set_rgb_led(255,0,0,0,False)
wb8.set_rgb_led(0,255,0,0,False)

time.sleep(2)

'''
Code for moving the bot to a particular position using vicon tracker
'''

print "Start moving"
a = ViconTrackerPoseHandler.ViconTrackerPoseHandler(None, None, "",51012, "Ollie_7")
b = ViconTrackerPoseHandler.ViconTrackerPoseHandler(None, None, "",51013, "Ollie_white")

'''
Input set of destination points to follow as trajectory
'''
blackPoints = [ (-1,1),(1,1), (1,-1) , (-1,-1),(-1,1) ]
whitePoints = [ (1,1), (1,-1),(-1,-1), (-1,1),(1,1) ]

try:
	t1 = threading.Thread( target = bot_movement, args = (bb8,a,blackPoints))
	t1.start()
	t2 = threading.Thread( target = bot_movement, args = (wb8, b, whitePoints) )
	t2.start()
except Exception as e:
	print "Could not connect to the bot(s)"

