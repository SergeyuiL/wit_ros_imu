#!/usr/bin/env python3

import rospy
from vpython import *
import math
import wx

from sensor_msgs.msg import Imu
from tf.transformations import euler_from_quaternion

rad2degrees = 180.0 / math.pi
precision = 2  # round to this number of digits
yaw_offset = 0  # used to align animation upon key press
yaw = 0


# Create shutdown hook to kill visual displays
def shutdown_hook():
    # print "Killing displays"
    wx.Exit()


# register shutdown hook
rospy.on_shutdown(shutdown_hook)


# Main scene
scene = canvas(title="Wit IMU Main Screen")
# scene.range = (1.3, 1.3, 1.3)
scene.range = (5, 5, 5)
scene.forward = vector(1, 0, -0.25)
# Change reference axis (x,y,z) - z is up
scene.up = vector(0, 0, 1)
scene.width = 500
scene.height = 500

# Second scene (Roll, Pitch, Yaw)
scene2 = canvas(
    title='Wit IMU Roll, Pitch, Yaw',
    x=550,
    y=0,
    width=500,
    height=500,
    center=vector(
        0,
        0,
        0),
    background=vector(
        0,
        0,
        0))
scene2.range = (1, 1, 1)
scene2.select()
# Roll, Pitch, Yaw
# Default reference, i.e. x runs right, y runs up, z runs backward (out of
# screen)
cil_roll = cylinder(pos=vector(-0.5, 0.3, 0), axis=vector(0.2, 0, 0),
                    radius=0.01, color=color.red)
cil_roll2 = cylinder(pos=vector(-0.5, 0.3, 0), axis=vector(-0.2, 0, 0),
                     radius=0.01, color=color.red)
cil_pitch = arrow(
    pos=vector(
        0.5, 0.3, 0), axis=vector(
            0, 0, -0.4), shaftwidth=0.02, color=color.green)
arrow_course = arrow(pos=vector(0.0, -0.4, 0), color=color.cyan,
                     axis=vector(0, 0.2, 0), shaftwidth=0.02, fixedwidth=1)

# Roll,Pitch,Yaw labels
label(pos=vector(-0.5, 0.6, 0), text="Roll (degrees)", box=0, opacity=0)
label(pos=vector(0.5, 0.6, 0), text="Pitch (degrees)", box=0, opacity=0)
label(pos=vector(0.0, 0.02, 0), text="Yaw (degrees)", box=0, opacity=0)
label(pos=vector(0.0, -0.16, 0), text="N", box=0, opacity=0, color=color.yellow)
label(pos=vector(0.0, -0.64, 0), text="S", box=0, opacity=0, color=color.yellow)
label(pos=vector(-0.24, -0.4, 0), text="W", box=0, opacity=0, color=color.yellow)
label(pos=vector(0.24, -0.4, 0), text="E", box=0, opacity=0, color=color.yellow)
label(pos=vector(0.18, -0.22, 0), height=7, text="NE", box=0, color=color.yellow)
label(pos=vector(-0.18, -0.22, 0), height=7, text="NW", box=0, color=color.yellow)
label(pos=vector(0.18, -0.58, 0), height=7, text="SE", box=0, color=color.yellow)
label(pos=vector(-0.18, -0.58, 0), height=7, text="SW", box=0, color=color.yellow)

rollLabel = label(pos=vector(-0.5, 0.52, 0), text="-", box=0, opacity=0, height=12)
pitchLabel = label(pos=vector(0.5, 0.52, 0), text="-", box=0, opacity=0, height=12)
yawLabel = label(pos=vector(0, -0.06, 0), text="-", box=0, opacity=0, height=12)

# acceleration labels
label(
    pos=vector(
        0,
        0.9,
        0),
    text="Linear Acceleration x / y / z (m/s^2)",
    box=0,
    opacity=0)
label(pos=vector(0, -0.8, 0), text="Angular Velocity x / y / z (deg/s)", box=0, opacity=0)
linAccLabel = label(pos=vector(0, 0.82, 0), text="-", box=0, opacity=0, height=12)
angVelLabel = label(pos=vector(0, -0.88, 0), text="-", box=0, opacity=0, height=12)

# Main scene objects
scene.select()
# Reference axis (x,y,z) - using ROS conventions (REP 103) - z is up, y left (west, 90 deg), x is forward (north, 0 deg)
# In visual, z runs up, x runs forward, y runs left (see scene.up command earlier)
# So everything is good
arrow(color=color.green, axis=vector(1, 0, 0), shaftwidth=0.04, fixedwidth=1)
arrow(color=color.green, axis=vector(0, 1, 0), shaftwidth=0.04, fixedwidth=1)
arrow(color=color.green, axis=vector(0, 0, 1), shaftwidth=0.04, fixedwidth=1)

# labels
label(pos=vector(0, 0, -1.2), text="Press 'a' to align", box=0, opacity=0)
label(pos=vector(1, 0.1, 0), text="X", box=0, opacity=0)
label(pos=vector(0, 1, -0.1), text="Y", box=0, opacity=0)
label(pos=vector(0, -0.1, 1), text="Z", box=0, opacity=0)
# IMU object
platform = box(length=1.0, height=0.05, width=0.65,
               color=color.red, up=vector(0, 0, 1), axis=vector(-1, 0, 0))
p_line = box(length=1.1, height=0.08, width=0.1,
             color=color.yellow, up=vector(0, 0, 1), axis=vector(-1, 0, 0))
plat_arrow = arrow(length=-0.8, color=color.cyan, up=vector(0, 0, 1),
                   axis=vector(-1, 0, 0), shaftwidth=0.06, fixedwidth=1)
plat_arrow_up = arrow(length=0.4, color=color.cyan, up=vector(-1, 0, 0),
                      axis=vector(0, 0, 1), shaftwidth=0.06, fixedwidth=1)
rospy.init_node("display_3D_visualization_node")

def keydown(evt):
    global yaw_offset
    global yaw
    s = evt.key
    if s == 'a':
        # 当 'a' 键被按下时，调整偏航角偏移量
        # 假设 'yaw' 是在此函数外部定义并更新的当前偏航角
        # 你需要确保 'yaw' 可以在这里被访问和修改
        yaw_offset += -yaw  # 这里需要访问当前的偏航角 'yaw'
        print("已校准偏航角")
        
scene.bind('keydown', keydown)

def processIMU_message(imuMsg):
    global yaw_offset
    global yaw

    roll = 0
    pitch = 0
    yaw = 0

    quaternion = (
        imuMsg.orientation.x,
        imuMsg.orientation.y,
        imuMsg.orientation.z,
        imuMsg.orientation.w)
    (roll, pitch, yaw) = euler_from_quaternion(quaternion)

    # add align offset to yaw
    yaw += yaw_offset

    axis = vector(-cos(pitch) * cos(yaw), -cos(pitch) * sin(yaw), sin(pitch))
    up = vector(sin(roll) *
          sin(yaw) +
          cos(roll) *
          sin(pitch) *
          cos(yaw), -
          sin(roll) *
          cos(yaw) +
          cos(roll) *
          sin(pitch) *
          sin(yaw), cos(roll) *
          cos(pitch))
    platform.axis = axis
    platform.up = up
    platform.length = 1.0
    plat_arrow_up.axis = up
    plat_arrow_up.up = axis
    plat_arrow_up.length = 0.4
    plat_arrow.axis = axis
    plat_arrow.up = up
    plat_arrow.length = -0.8
    p_line.axis = axis
    p_line.up = up
    p_line.length = 1.1
    cil_roll.axis = vector(-0.2 * cos(roll), 0.2 * sin(roll), 0)
    cil_roll2.axis = vector(0.2 * cos(roll), -0.2 * sin(roll), 0)
    cil_pitch.axis = vector(0, -0.4 * sin(pitch), -0.4 * cos(pitch))
    # remove yaw_offset from yaw display
    arrow_course.axis = vector(-0.2 * sin(yaw - yaw_offset),
                         0.2 * cos(yaw - yaw_offset), 0)

    # display in degrees / radians
    rollLabel.text = str(round(roll * rad2degrees, precision))
    pitchLabel.text = str(round(pitch * rad2degrees, precision))
    # remove yaw_offset from yaw display
    yawLabel.text = str(round((yaw - yaw_offset) * rad2degrees, precision))

    linAccLabel.text = "%8s \t %8s \t %8s" % (str(round(imuMsg.linear_acceleration.x, precision)), str(
        round(imuMsg.linear_acceleration.y, precision)), str(round(imuMsg.linear_acceleration.z, precision)))
    angVelLabel.text = "%12s \t %12s \t %12s" % (str(
        round(
            imuMsg.angular_velocity.x * rad2degrees,
            precision)),
        str(
            round(
                imuMsg.angular_velocity.y * rad2degrees,
                precision)),
        str(
        round(
            imuMsg.angular_velocity.z * rad2degrees,
            precision)))

    # # check for align key press - if pressed, next refresh will be aligned
    # if scene.kb.keys:  # event waiting to be processed?
    #     s = scene.kb.getkey()  # get keyboard info
    #     if s == 'a':
    #         # align key pressed - align
    #         yaw_offset += -yaw


sub = rospy.Subscriber('/wit/imu', Imu, processIMU_message)
rospy.spin()
