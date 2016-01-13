#!/cygdrive/c/Python27/python

#import required libraries
from visual import *
import numpy as np
import sys
import time
import math
import serial
import Arm
import re

ser = serial.Serial('COM3', 115200, timeout=3)
#ser.baudrate=9600
tmp_pos = [0.0,0.0,0.0]

#define dimensions for the MeArm
linkage_1 = 8.5 #length of link 1 in cm
linkage_1_angle = 0.0
linkage_2 = 8.5 #length of link 2 in cm
linkage_2_angle = 0.0
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



#Create virtual environment:
scene = display(title='Robot movements', width=1200, height=1200, center=(8,4,0)) #set up the scene


#To improve clarity, create a set of x, y and z axis
x_axis= arrow(pos=(0,0,0), axis=(15,0,0), shaftwidth=0.1, headwidth=0.3)
y_axis= arrow(pos=(0,0,0), axis=(0,15,0), shaftwidth=0.1, headwidth=0.3)
pos_z_axis= arrow(pos=(0,0,0), axis=(0,0,-15), shaftwidth=0.1, headwidth=0.3)
neg_z_axis= arrow(pos=(0,0,0), axis=(0,0,15), shaftwidth=0.1, headwidth=0.3)

#Indicators for the target, link 1 and link 2 respectively
#indicator = arrow(pos=(0,0,0), axis=(10,10,0), shaftwidth=0.2, headwidth=0.3, color=color.yellow)
linkage_1_ind = arrow(pos=(0+x_offset,0+y_offset,0+z_offset), axis=(0,linkage_1,0), shaftwidth=0.2, headwidth=0.3, color=color.red)
linkage_1_angle = 90
linkage_2_ind = arrow(pos=(0+x_offset,linkage_1+y_offset,0+z_offset), axis=(linkage_2,0,0), shaftwidth=0.2, headwidth=0.3, color=color.green)
linkage_2_angle = 0
linkage_3_ind = arrow(pos=(0+x_offset+linkage_2,linkage_1+y_offset,0+z_offset), axis=(linkage_3,0,0), shaftwidth=0.2, headwidth=0.3, color=color.yellow)
linkage_3_angle = 0
linkage_1_ind.visible=False
linkage_2_ind.visible=False
linkage_3_ind.visible=False

#Labels to show how to move the robot
label_1=label(pos=(8,18,0), text='Use arrows to move in plane. Use a and d to rotate. Use w and s to open/close the clamp')
label_2=label(pos=(8,-8,0), text='Clamp status = Close')
label_x=label(pos=(16,0,0), text='x')
label_x=label(pos=(0,16,0), text='y')
label_z=label(pos=(0,0,16), text='z')


#Labels to improve the visualization of the position of the arm
in_x_plane=arrow(pos=(0,0,0), axis=(10,0,0), shaftwidth=0.1, headwidth=0.1, color=color.blue, opacity=0.3)
in_y_plane=arrow(pos=(0,0,0), axis=(0,10,0), shaftwidth=0.1, headwidth=0.1, color=color.cyan, opacity=0.3)
in_z_plane=arrow(pos=(0,0,0), axis=(0,0,10), shaftwidth=0.1, headwidth=0.1, color=color.green, opacity=0.3)

mearm_frame = frame()
cabin = box(frame=mearm_frame,pos=(0,3,0), length=4,height=4, width=4, opacity=0.5)
stilts = box(pos=(0,0.5,0), length=2,height=1, width=2, opacity=0.7)
mearm_curve=curve(frame=mearm_frame,pos=[(x_offset,y_offset,z_offset)],color=color.blue,radius=0.50)
mearm_curve.append(pos=(x_offset,y_offset+linkage_1,z_offset),color=color.green)
mearm_curve.append(pos=(x_offset+linkage_2,y_offset+linkage_1,z_offset),color=color.red)
mearm_curve.append(pos=(x_offset+linkage_2+linkage_3,y_offset+linkage_1,z_offset),color=color.yellow)

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

#offset=1.0
offset=1.0
#degrees=1.0
degrees=1.0

in_x_plane.axis=(x*np.cos(phi*0.01745),0,0)
in_y_plane.axis=(0,y,0)
in_z_plane.axis=(0,0,x*np.sin(phi*0.01745))
label_y_offset=2
label_target=label(pos=(x,y+label_y_offset, z), text=("Target: %.2f,%.2f,%.2f phi(%d) offset(%.2f)" % (x,y,z,phi,offset)))
#print("linkage_1_ind.length = %.2f, linkage_2_ind.length = %.2f" % (linkage_1_ind.length, linkage_2_ind.length))

#draw initial compact disc
disc=cylinder(pos=(in_x_plane.axis[0]+3,in_y_plane.axis[1]-3,in_z_plane.axis[2]),axis=(0,0.12,0),radius=6)

#draw source and destination spindles
#dest
dst_base=cylinder(pos=(1,0,11),axis=(0,0.5,0),radius=6.3, color=color.green)
dst_spindle=cylinder(pos=(1,0,11),axis=(0,5,0),radius=0.7, color=color.green)

#source
source_base=cylinder(pos=(1,0,-11),axis=(0,0.5,0),radius=6.3, color=color.red)
source_spindle=cylinder(pos=(1,0,-11),axis=(0,5,0),radius=0.7, color=color.red)
#put some cd's on the spindle
for tmpx in range(0,30):
    source_cds=cylinder(pos=(1,(0.5+(tmpx*(0.12 + 0.01))),-11),axis=(0,0.12,0),radius=6)

#draw cdrom
cdrom = box(pos=(30,2.14,0), width=14.9, height=4.28, length=20, color=color.blue)
tray = box(pos=(13.75,3,0), width=13.4, height=1.5, length=13.25, color=color.green)

#initialise the mearm location 
sleep(2)
ser.write("%d,%d,%d,%d\n" % (mearm_base, mearm_left, mearm_right, mearm_gripper))
print ("%d,%d,%d,%d" % (mearm_base, mearm_left, mearm_right, mearm_gripper))
#line = ser.readline()
#print "Serial line = '%s'" % (line)
#numbers=re.findall(r'\d+', line)
#print "numbers: " + repr(numbers)

delay=0.05

scaling=15.0
#scaling=1.0

#now we made an infinite while loop to keep the program running
cabin_degrees=0
first=1
while (1==1):
    rate(10) #refresh rate required for VPython
    ev = scene.waitfor('keydown')
    if ev.key == 'up':
        #print "up"
        y=y+(offset/scaling)

        tmp_pos = disc.pos
        tmp_pos[1] = tmp_pos[1] + (offset/scaling)
        disc.pos=tmp_pos

        print ("after for loop: %d,%d,%d,%d" % (mearm_base, mearm_left, mearm_right, mearm_gripper))

    elif ev.key == 'down':
        #print "down"
        y=y-(offset/scaling)

        tmp_pos = disc.pos
        tmp_pos[1] = tmp_pos[1] - (offset/scaling)
        disc.pos=tmp_pos

        print ("after for loop: %d,%d,%d,%d" % (mearm_base, mearm_left, mearm_right, mearm_gripper))
    elif ev.key == 'right':
        #print "right"
        x=x+(offset/scaling)

        tmp_pos = disc.pos
        tmp_pos[0] = tmp_pos[0] + (offset/scaling)
        disc.pos=tmp_pos

    elif ev.key == 'left':
        #print "left"
        x=x-(offset/scaling)

        tmp_pos = disc.pos
        tmp_pos[0] = tmp_pos[0] - (offset/scaling)
        disc.pos=tmp_pos

    elif ev.key == 'k':
        #print "k"
	z=z-(offset/scaling)
    elif ev.key == 'm':
        #print "m"
	z=z+(offset/scaling)
    elif ev.key == 'a':
        #print "a"
        if (phi-degrees) <= -90:
            print 'Attempt to move beyond minimum angle ... '
            tmp_degrees=-(-90-phi)
        else:
            tmp_degrees=degrees
        print("tmp_degrees=%d phi=%d" % (tmp_degrees, phi))
        phi=phi-tmp_degrees
        cabin_degrees=cabin_degrees-tmp_degrees;
        mearm_frame.rotate(angle=radians(tmp_degrees), axis=(0,1,0), origin=(0,0,0))
        disc.rotate(angle=radians(tmp_degrees), axis=(0,1,0), origin=(0,0,0))
        mearm_base=mearm_base+offset

    elif ev.key == 'd':
        #print "d"
        if (phi+degrees) >= 90:
            print 'Attempt to move beyond maximum angle ... '
            tmp_degrees=90-phi
        else:
            tmp_degrees=degrees
        print("tmp_degrees=%d phi=%d" % (tmp_degrees, phi))
        phi=phi+tmp_degrees
        cabin_degrees=cabin_degrees+tmp_degrees;
        mearm_frame.rotate(angle=radians(-tmp_degrees), axis=(0,1,0), origin=(0,0,0))
        disc.rotate(angle=radians(-tmp_degrees), axis=(0,1,0), origin=(0,0,0))
        mearm_base=mearm_base-offset

    elif ev.key == 'r':
        #print "r"
        print 'Going to initial position...'

        #reset the mearm
        mearm_base=mearm_base_initial
        mearm_left=mearm_left_initial
        mearm_right=mearm_right_initial
        #commented out to leave the gripper in the state it was
        #mearm_gripper=mearm_gripper_initial

        x=x_initial
        y=y_initial
        z=z_initial
        phi=phi_initial

    	mearm_frame.rotate(angle=radians(cabin_degrees), axis=(0,1,0), origin=(0,0,0))
    	disc.rotate(angle=radians(cabin_degrees), axis=(0,1,0), origin=(0,0,0))
        disc.pos=(in_x_plane.axis[0]+3,in_y_plane.axis[1]-3,in_z_plane.axis[2])
	cabin_degrees=0;

    elif ev.key == 'w':
        #print "w"
        print 'Opening clamp...'
        clamp = 'Open'
        mearm_gripper=70
    elif ev.key == 'o':
        #print "o"
        #open the cdrom
	tray.pos=(13.75,3,0)
    elif ev.key == 'c':
        #print "c"
        #close the cdrom
	tray.pos=(13.75+12.75,3,0)
    elif ev.key == 's':
        #print "s"
        print 'Closing clamp...'
        clamp = 'Close'
        mearm_gripper=140
    elif ev.key == ']':
        #print "]"
	offset=offset*2
	degrees=degrees*2
	print "offset = " + repr(offset) + ", degrees = " + repr(degrees)
    elif ev.key == '[':
        #print "["
	offset=offset/2
	degrees=degrees/2
	print "offset = " + repr(offset) + ", degrees = " + repr(degrees)
    elif ev.key == 'q':
        #print "q"
        exit()
    elif ev.key == 'y':
        mearm1_offset+=5;
    elif ev.key == 'h':
        mearm1_offset-=5;
    elif ev.key == 'u':
        mearm2_offset+=5;
    elif ev.key == 'j':
        mearm2_offset-=5;

    #print("x,y,z - %.2f,%.2f,%.2f" %(x,y,z))
    realx=x-linkage_3
    #print("realx,y,z - %.2f,%.2f,%.2f" %(realx,y,z))
    simplex=realx-x_offset
    simpley=y-y_offset
    simplez=z-z_offset
    #print("simplex,simpley,simplez - %.2f,%.2f,%.2f" %(simplex,simpley,simplez))

    arm.q = arm.inv_kin([simplex*10,simpley*10]) # get new arm angles

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

    #print "joints_x: " + repr(joints_x)
    #print "joints_y: " + repr(joints_y)

    mearm_curve.pos=([
        (x_offset+(joints_x[0]/10),y_offset+(joints_y[0]/10),z_offset),
        (x_offset+(joints_x[1]/10),y_offset+(joints_y[1]/10),z_offset),
        (x_offset+(joints_x[2]/10),y_offset+(joints_y[2]/10),z_offset),
        (x_offset+(joints_x[2]/10)+linkage_3,y_offset+(joints_y[2]/10),z_offset)])

    print "x,y = %d,%d" % (simplex*10,simpley*10)
    arm1_angle=(np.degrees(arm.q[0])+np.degrees(arm.q[1]))-212
    arm2_angle=(180-np.degrees(arm.q[0]))-22

    print "armoo1: 0 - " + repr(arm1_angle)
    print "armoo1: 1 - " + repr(arm2_angle)

    #print "armoo1: 2 - " + repr(np.degrees(arm.q[2]))
    #arm1_angle=arm.q[0]
    #arm2_angle=arm.q[1]
    #arm1_angle=mearm1_offset-np.degrees(arm1_angle)
    #arm2_angle=mearm2_offset-np.degrees(arm2_angle)
    #print("armoo2: angle1(%.2f) angle2(%.2f)" % (arm1_angle,arm2_angle))
    #arm1_angle=arm1_angle
    #arm2_angle=arm2_angle
    #print("armoo3: angle1(%.2f) angle2(%.2f) offset(%d,%d)" % (arm1_angle,arm2_angle,mearm1_offset,mearm2_offset))

    #reset rotation to make it easier to think about
    disc.rotate(angle=radians(phi), axis=(0,1,0), origin=(0,0,0))

    #return objects to their correct rotation
    disc.rotate(angle=radians(-phi), axis=(0,1,0), origin=(0,0,0))


    #print("x,y,z: %.2f,%.2f,%.2f" % (x,y,z))
    label_target.pos=(x,y+label_y_offset, z)
    label_target.text=("Target: %.2f,%.2f,%.2f phi(%d) offset(%.2f)" % (x,y,z,phi,offset))
    #print("linkage_1_ind.length = %.2f, linkage_2_ind.length = %.2f" % (linkage_1_ind.length, linkage_2_ind.length))

    #move the arm
    #ser.write("%d,%d,%d,%d\n" % (mearm_base, mearm_left, mearm_right, mearm_gripper))
    #print ("%d,%d,%d,%d" % (mearm_base, mearm_left, mearm_right, mearm_gripper))
    ser.write("%d,%d,%d,%d\n" % (mearm_base, arm1_angle, arm2_angle, mearm_gripper))
    print ("%d,%d,%d,%d" % (mearm_base, arm1_angle, arm2_angle, mearm_gripper))
    #line = ser.readline()
    #print "Serial line = '%s'" % (line)
    #numbers=re.findall(r'\d+', line)
    #print "numbers: " + repr(numbers)
    #if (first==1):
        #mearm1_offset+=int(numbers[1])-arm1_angle
        #mearm2_offset+=int(numbers[2])-arm2_angle
        #first=0
