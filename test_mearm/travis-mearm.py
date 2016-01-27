#!/cygdrive/c/Python27/python

#import required libraries
from __future__ import division
from visual import *
import numpy as np
import sys
import time
import math
import serial
import Arm
import re
import scanf
import platform
import os
import ctypes
import subprocess
import wmi
from random import randint

if (len(sys.argv)<3):
    print "usage: " + sys.argv[0] + " <load|unload|quiet> <drive number: 1|2> <optional: calibrate>"
    sys.exit()

#make sure everyone goes in order
milli=time.time()*1000
print repr(milli)

queue_directory="c:/Windows/Temp/robot_queue"

if not os.path.exists(queue_directory):
    os.makedirs(queue_directory)

lock_file=open(queue_directory + "/" + repr(milli), 'w+')
lock_file.write(repr(milli))
lock_file.close()

direntries=os.listdir(queue_directory)
#print "queue_directory contents: "
#print repr(direntries)
top=0
while(top==0):
    sleep(1)
    direntries=os.listdir(queue_directory)
    print "queue_directory contents: "
    print repr(direntries)
    print direntries[0]
    print repr(milli)
    if(direntries[0]==repr(milli)):
        top=1
#end of make sure everyone goes in order
#wait to make sure previous processes have let go of the serial port
sleep(1)

#make sure the drive is closed
#ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door closed wait", None, 0, None)
#ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!D door closed wait", None, 0, None)

ser = serial.Serial('COM3', 115200, timeout=3)
tmp_pos = [0.0,0.0,0.0]

#define dimensions for the MeArm
linkage_1 = 8.5 #length of link 1 in cm
linkage_2 = 8.5 #length of link 2 in cm
linkage_3 = 4.0 #length of claw in cm

arm = Arm.Arm3Link(L = np.array([linkage_1*10,linkage_2*10,1]))
#move it a bit to make sure it's facing to the right
arm.q = arm.inv_kin([-31,1]) # get new arm angles
arm.q = arm.inv_kin([31,1]) # get new arm angles
arm.q = arm.inv_kin([120,1]) # get new arm angles

mearm_base_initial=90
mearm_left_initial=148
mearm_right_initial=68
mearm_gripper_initial=90

mearm_base=mearm_base_initial
mearm_left=mearm_left_initial
mearm_right=mearm_right_initial
mearm_gripper=mearm_gripper_initial
mearm1_offset=417;
mearm2_offset=518;

x_offset=1;
y_offset=2;
z_offset=0;

#Initial position
x=0.0+x_offset+linkage_2+linkage_3
x_initial=x
y=0.0+y_offset+linkage_1
y_initial=y
z=0.0+z_offset
z_initial=z
phi=0.0 #angle for base rotation
phi_initial=phi
clamp = 'neither open nor closed' #Clamp is close
suction = 0

offset=1.0
degrees=1.0
delay=0.30

#initialise the mearm location 
sleep(1)
ser.write("%d,%d,%d,%d,%d\n" % (mearm_base, mearm_left, mearm_right, mearm_gripper, suction))
print ("%d,%d,%d,%d,%d" % (mearm_base, mearm_left, mearm_right, mearm_gripper, suction))
sleep(1)

scaling=15.0

def calibrate_pause():
    print "pausing until you hit enter"
    sys.stdin.readline()

def move_arm_to(x,y,z):
    global delay
    #bring it back somewhere sensible
    arm.q = arm.inv_kin([120,1]) # get new arm angles
    print "move_arm_to(%d,%d,%d)" % (x,y,z)
    negativez=0
    if (z<0):
        negativez=1
        z=-z
    if (z==0):
        zrotate=0.0
        #print ("zrotate = %d" % (zrotate))
    else:
	#work out the rotation angle for the base
        o=x
        a=z
        h=sqrt(o**2+a**2)
        zrotate=np.degrees(acos(a/h))
        zrotate=90-zrotate
        #print ("o=%d a=%d h=%.2f zrotate = %.2f" % (o,a,h,zrotate))
        #because we're further out ... 
        x=h

    arm.q = arm.inv_kin([x,y]) # get new arm angles
    arm1_angle=(np.degrees(arm.q[0])+np.degrees(arm.q[1]))-212
    arm2_angle=(180-np.degrees(arm.q[0]))-22
    print "arm1_angle,arm2_angle - %.2f,%.2f" % (arm1_angle,arm2_angle)
    #move the arm via arduino
    if (negativez==1):
        ser.write("%d,%d,%d,%d,%d\n" % (mearm_base+zrotate, np.int(arm1_angle), np.int(arm2_angle), mearm_gripper, suction))
    else:
        ser.write("%d,%d,%d,%d,%d\n" % (mearm_base-zrotate, np.int(arm1_angle), np.int(arm2_angle), mearm_gripper, suction))

    #move the arm on the screen
    joints_x = np.array([ 0,
        arm.L[0]*np.cos(arm.q[0]),
        arm.L[0]*np.cos(arm.q[0]) + arm.L[1]*np.cos(arm.q[0]+arm.q[1]),
        arm.L[0]*np.cos(arm.q[0]) + arm.L[1]*np.cos(arm.q[0]+arm.q[1]) +
            arm.L[2]*np.cos(np.sum(arm.q)) ])

    joints_y = np.array([ 0,
        arm.L[0]*np.sin(arm.q[0]),
        arm.L[0]*np.sin(arm.q[0]) + arm.L[1]*np.sin(arm.q[0]+arm.q[1]),
        arm.L[0]*np.sin(arm.q[0]) + arm.L[1]*np.sin(arm.q[0]+arm.q[1]) +
            arm.L[2]*np.sin(np.sum(arm.q)) ])
    sleep(delay)

def insert_disc(drive):
    global delay
    global suction
    global calibrate

    status_file=open("C:/Windows/Temp/robot_status.txt" + drive, 'w+')
    status_file_contents=status_file.read()
    status_file.close()
    print repr(status_file_contents)
    if(status_file_contents=="load"):
        print "pausing until you hit enter (to stop accidental duplicate loads)"
        sys.stdin.readline()

    suction=0
    move_arm_to(0,80,-80)
    sleep(delay)
    if(drive=="1"):
        #ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door open wait", None, 0, None)
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door open", None, 0, None)
    if(drive=="2"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!D door open", None, 0, None)
    sleep(delay)
    move_arm_to(0,20,-80)

    move_arm_to(0,-30,-80)
    if(calibrate==1):
        calibrate_pause()
    suction=1
    move_arm_to(0,-30,-80)
    move_arm_to(0,-30,-80)
    move_arm_to(0,-10,-80)
    move_arm_to(0,0,-80)
    move_arm_to(0,20,-80)
    move_arm_to(0,40,-80)
    move_arm_to(0,50,-80)
    move_arm_to(0,40,-80)
    move_arm_to(0,80,-80)

    move_arm_to(0,80,-80)
    move_arm_to(70,80,0)
    move_arm_to(75,80,20)
    move_arm_to(80,50,20)
    move_arm_to(80,40,20)
    
    if(drive=="1"):
        move_arm_to(80,30,25)
    if(drive=="2"):
        move_arm_to(60,40,10)
        move_arm_to(70,20,10)
        move_arm_to(80,-10,25)

    if(calibrate==1):
        calibrate_pause()

    suction=0
    if(drive=="1"):
        move_arm_to(80,30,25)
    if(drive=="2"):
        move_arm_to(60,-10,10)

    if(drive=="1"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door closed", None, 0, None)
    if(drive=="2"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!D door closed", None, 0, None)
    status_file=open("C:/Windows/Temp/robot_status.txt" + drive, 'w+')
    status_file.write("load")
    status_file.close()

def remove_disc(drive):
    global delay
    global suction
    global calibrate
    suction=0
    move_arm_to(80,80,0)
    move_arm_to(70,90,0)
    move_arm_to(80,80,0)
    if(drive=="1"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door open", None, 0, None)
    if(drive=="2"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!D door open", None, 0, None)
    sleep(delay)
    move_arm_to(80,80,10)
    move_arm_to(80,40,10)

    if(calibrate==1):
        calibrate_pause()
    suction=1
    if(drive=="1"):
        move_arm_to(80,00,10)
    if(drive=="2"):
        move_arm_to(80,30,10)
        move_arm_to(80,20,10)
        move_arm_to(80,10,10)
        move_arm_to(80,-10,10)
        move_arm_to(80,-20,10)
        move_arm_to(80,-30,10)
        move_arm_to(70,-40,10)
    sleep(delay)
    sleep(delay)
    if(calibrate==1):
        calibrate_pause()
    move_arm_to(80,80,10)

    if(drive=="1"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!E door closed", None, 0, None)
    if(drive=="2"):
        ctypes.windll.WINMM.mciSendStringW(u"set cdaudio!D door closed", None, 0, None)
    sleep(delay)
    if(drive=="1"):
        move_arm_to(70,20,10)
    if(drive=="2"):
        move_arm_to(40,10,10)
    move_arm_to(70,50,10)
    move_arm_to(40,10,50)
    move_arm_to(90,-10,80)
    if(calibrate==1):
        calibrate_pause()
    suction=0
    move_arm_to(90,-10,80)
    move_arm_to(0,80,-80)
    status_file=open("C:/Windows/Temp/robot_status.txt" + drive, 'w+')
    status_file.write("unload")
    status_file.close()

def quiet_position():
    global suction
    global calibrate
    suction=0
    move_arm_to(40,40,0)
    move_arm_to(30,40,0)
    move_arm_to(30,30,0)

if (len(sys.argv)==4):
    calibrate=1
else:
    calibrate=0


#print repr(sys.argv) + " " + repr(len(sys.argv))
#sys.exit()

#if(calibrate==1):
    #calibrate_pause()

if (sys.argv[1]=="load"):
    insert_disc(sys.argv[2])
    quiet_position()

if (sys.argv[1]=="unload"):
    remove_disc(sys.argv[2])
    quiet_position()

if (sys.argv[1]=="quiet"):
    quiet_position()

#remove your entry in the queue
os.remove(queue_directory + "/" + repr(milli))

sys.exit()
