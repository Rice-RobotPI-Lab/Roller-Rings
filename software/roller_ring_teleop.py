"""
--------------------------------------------------------------------------
Roller Ring Teleop
--------------------------------------------------------------------------
License:   
Copyright 2025 - Hayden Webb

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
"""

import multiprocessing
from multiprocessing import Process, Manager, Lock, Queue
import sys
import time
import numpy as np
import os
from rg_serial import *
import pygame
import ASController

mode = 1
motor_cpr = 11836.9
com_baud = 1000000
port = '/dev/ttyUSB0'
# port = 'COM0'


def teleop_process(dc_motors):
    pygame.init()

    pygame.display.set_mode((300, 300))
    clock = pygame.time.Clock()
    busy = False
    cur_pos = [.0,.0,.0]
    target_pos = [.0,.0,.0]
    joysticks = {}
    toggle = False
    direction = False

    while True: 
        clock.tick(60)
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            # Keyboard Option - Values can be changed/flipped as needed
            if event.type == pygame.KEYDOWN:
                print("~")

                if event.type == pygame.K_w:
                    dc_motors.set_all_velocity = [50, 50, -50, -50]

                if event.type == pygame.K_a:
                    dc_motors.set_all_velocity = [-50, -50, 50, 50]

                if event.type == pygame.K_s:
                    dc_motors.set_all_velocity = [-50, 50, 50, -50]

                if event.type == pygame.K_d:
                    dc_motors.set_all_velocity = [50, -50, -50, 50]

            # Controller Option
            if event.type == pygame.JOYBUTTONDOWN:
                print("~")
                joystick = joysticks[event.instance_id]
                if event.button == 1:
                    dc.motors.set_all_velocity(speed)

                if event.button == 2:
                    dc.motors.set_all_velocity(-speed)

                #Choose Rotation Axis for given frame
                if event.button == 3:
                    print("SET Direction")
                    axes = joystick.get_numaxes()
                    motionAxis = np.zeros(axes)
                    speed = controllerAngle(motionAxis)


            #Stop DC Motors
            if event.type == pygame.JOYBUTTONUP or event.type == pygame.KEYUP:
                print("Stop DC")
                dc_motors.set_all_velocity([0, 0, 0, 0])
            
            #Failsafe Stop
            if event.type == pygame.K_SPACE or event.button == 4:
                print("Stop DC")
                dc_motors.set_all_velocity([0, 0, 0, 0])
        
        if not move:
            busy = False

def controllerAngle (motionAxis):
    '''
    Derives the speed of the DC motors based on the joystick input. Roller Rings are assumed coradial and concentric, if not use self-derived IK angle values for eeAngle.
    INPUT: Joystick Angles (Radians)
    OUTPUT: Weighted Speed Values for each DC Motor
    '''
    speedDerive = np.zeros(3)
    eeAngle = ([np.pi*(1/4), np.pi*(2/4), np.pi*(3/4), np.pi]) # End Effector Angles in Radians
    
    # Setting direction of rotation from axes
    if motionAxis[1] < 0 and motionAxis [0] > 0:
        angleRot = np.arctan(np.abs(motionAxis[1])/np.abs(motionAxis[0]))
    if motionAxis[1] < 0 and motionAxis [0] < 0:
        angleRot = np.pi - np.arctan(np.abs(motionAxis[1])/np.abs(motionAxis[0]))
    if motionAxis[1] > 0 and motionAxis [0] < 0:
        angleRot = np.arctan(np.abs(motionAxis[1])/np.abs(motionAxis[0])) + np.pi
    if motionAxis[1] > 0 and motionAxis [0] > 0:
        angleRot = 2*np.pi - np.arctan(np.abs(motionAxis[1])/np.abs(motionAxis[0]))
    
    speedDerive[0] = np.floor(np.sin(np.pi - eeAngle[0] - angleRot)*60)
    speedDerive[1] = np.floor(np.sin(angleRot - eeAngle[1])*60)
    speedDerive[2] = np.floor(np.sin(np.pi + eeAngle[2] + angleRot)*60)

    print("Set Speed to:", speed)
    return speedDerive

if __name__ == '__main__':
    
    dc_motors= SBMotor("/dev/ttyUSB0", com_baud)
    if mode == 0: #Position Control
        ctrl_mode = 0; p = 15; i = 0.2; d = 100
    if mode == 1: #Velocity Control
        ctrl_mode = 1; p = 14; i = 0; d = 0.3
    
    dc_motors_TT.init_single_motor(4, motor_cpr, p, i, d, ctrl_mode=ctrl_mode)
    dc_motors_TT.init_single_motor(5, motor_cpr, p, i, d, ctrl_mode=ctrl_mode)
    dc_motors_TT.init_single_motor(6, motor_cpr, p, i, d, ctrl_mode=ctrl_mode)
    dc_motors_TT.init_single_motor(7, motor_cpr, p, i, d, ctrl_mode=ctrl_mode)

    teleop_process(dc_motors)
