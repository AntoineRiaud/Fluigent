#!/usr/bin/env python
# -*- coding: utf-8 -*-

#******************************************************************************
#software         : Python_Fluigent
#version          : 0.2
#date             : 16-02-2016
#******************************************************************************

from __future__ import print_function   # Used for "print" function compatibility between Python 2.x and 3.x versions
import platform                         # Library used for x64 or x86 detection
import time                             # Time library, use of sleep function
import ctypes                           # Used for variable definition types
from ctypes import *                    # Used to load dynamic linked libraries
import struct                                         #find if the system is 32 or 64 bits
import exceptions

# This function uses "raw_input" for Python 2.x versions and "input" for Python 3.x versions
def myinput(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


#------------------------------MFCS---------------------------------
class MFCS_EZ():
    #each time an MFCS object is created, N_mfcs increases
    N_mfcs = 0
    def __init__(self,verbose= False):
        # Load dll into memory
        Nbits_syst = 8 * struct.calcsize("P")
        if Nbits_syst==32:
            self.lib_mfcs = ctypes.WinDLL('mfcs_32.dll')
        else:
            self.lib_mfcs = ctypes.WinDLL('mfcs_64.dll')
        # Variable types definition 
        self.mfcsHandle = c_ulong(0)
        C_error = c_char()
        # Initialize the first MFCS-EZ in Windows enumeration list 
        self.mfcsHandle = self.lib_mfcs.mfcsez_initialisation(self.N_mfcs)
        # After initialization a short delay (at least 500ms) are required to make sure that 
        #   the USB communication is properly established
        time.sleep(1)
        self.status()
        print(self.status)
        self.__get_serial_number()
        print(self.serial_number)
        self.verbose = verbose
        MFCS_EZ.N_mfcs+=1

    def __del__(self):
        self.set_pressure([0],[0]) #sets all the channels to 0
        B_OK = bool(False) 
        # Close communication port 
        B_OK = self.lib_mfcs.mfcs_close(self.mfcsHandle);
        if (B_OK == True):
                print ('USB connection closed')
        else:# if (B_OK == False):
                print ('Failed to close USB connection')
                
        # Release the DLL
        ctypes.windll.kernel32.FreeLibrary(self.lib_mfcs._handle)
        self.N_mfcs-=1
        del self.lib_mfcs
        print ('MFCS library unloaded')
        MFCS_EZ.N_mfcs-=1


    def status(self):
        # Print status on MFCS initialization
        if (self.mfcsHandle != 0):
                self.status = 'MFCS-EZ initialized'
        else:
                self.status = 'Error on MFCS-EZ initialisation. Please check that device is plugged in.'

        

    def __get_serial_number(self):
        C_error = c_char()
        mySerial = c_ushort(0)
        # Get serial number of the MFCS-EZ associated to the MFCS session
        C_error = self.lib_mfcs.mfcs_get_serial(self.mfcsHandle, byref(mySerial))
        # Get status and SN value of called library function
        if (C_error == 0):
                print('MFCS-EZ SN: '+ str(mySerial.value))
        else:
                print('Failed to get MFCS-EZ SN.')
        self.serial_number = mySerial.value
                
        #C_error=self.lib_mfcs.mfcs_set_alpha(mfcsHandle,0,5);   # Sends channel configuration

    def purge(self):
        self.purge_status = c_byte(0) 
        C_error = c_char()
        # Connect all channels outputs directly to the pressure supply
        print ('Set purge on')
        C_error = self.lib_mfcs.mfcs_set_purge_on(self.mfcsHandle)
        # Wait 1s before getting purge status
        time.sleep(1)
        # Get the status of the purge
        C_error = self.lib_mfcs.mfcs_get_purge(self.mfcsHandle,byref(self.purge_status))
        # Display purge status
        if (self.purge_status.value == 0):
                print ('Purge is off')
        if (self.purge_status.value == 1):
                print ('Purge is on')
                
        # Ask user to confirm that chamber is closed
        myinput("Please confirm that the chamber is closed (press 'ENTER')")
        
        # Set purge off
        print ('Set purge off')
        C_error = self.lib_mfcs.mfcs_set_purge_off(self.mfcsHandle)
        # Wait 1s before getting purge status
        time.sleep(1)
        # Get the status of the purge
        C_error = self.lib_mfcs.mfcs_get_purge(self.mfcsHandle,byref(self.purge_status))
        # Display purge status
        if (self.purge_status.value == 0):
                print ('Purge is off')
        if (self.purge_status.value == 1):
                print ('Purge is on')

    def set_pressure(self,channel,pressure):
        if self.verbose:
            print ('Setting pressure')
        for i in range(len(channel)):
            C_channel =  c_char(chr(channel[i]))
            F_pressure = c_float(pressure[i])
            C_error = self.lib_mfcs.mfcs_set_auto(self.mfcsHandle,C_channel,F_pressure)
        if not (C_error == 0):
            #raise RuntimeError('failed to set the pressure')
            print('failed to set the pressure')

    def read_pressure(self,channel):
        if self.verbose:
            print('reading pressure')
        pressure = []
        for channel_i in channel:
            C_channel = c_char(chr(channel_i))
            F_pressure = c_float(0)
            US_chrono = c_ushort(0)
            C_error = self.lib_mfcs.mfcs_read_chan(self.mfcsHandle,C_channel,
                                                   byref(F_pressure),byref(US_chrono))
            pressure.append(F_pressure.value)
            if not (C_error == 0):
                #raise RuntimeError('failed to set the pressure')
                print('failed to read the pressure on channel '+str(channel_i))
        return pressure



#--------------------------Rot_switch-----------------------------




    
class ROT_switch():
    #each time an rot_switch object is created, N_rot_switch increases
    N_rot_switch = 0
    def __init__(self):
        essHandle = c_ulong(0)              # Used to get the device handle
        # Load dll into memory
        Nbits_syst = 8 * struct.calcsize("P")
        if Nbits_syst==32:# Load 32 bit dll into memory
            self.lib_ess = ctypes.WinDLL('ess_32.dll')
        else:
            self.lib_ess = ctypes.WinDLL('ess_64.dll')
        # Initialize the first FLOWBOARD in Windows enumeration list
        self.essHandle = self.lib_ess.ess_initialisation(self.N_rot_switch)
        # After initialization a short delay (at least 500ms) are required to make sure that 
        #   the USB communication is properly established
        time.sleep(1)
        # Print status on ESS initialization
        self.connection_status()
        print(self.connection_status)
        self.__get_serial_number()
        print(self.serial_number)
        ROT_switch.N_rot_switch+=1

    def __del__(self):
        B_OK = bool(False)
        # Close communication port 
        B_OK = self.lib_ess.ess_close(self.essHandle);
        if (B_OK == True):
                print ('USB connection closed')
        if (B_OK == False):
                print ('Failed to close USB connection')    
        # Release the DLL
        ctypes.windll.kernel32.FreeLibrary(self.lib_ess._handle)
        del self.lib_ess
        print ('ESS library unloaded')
        ROT_switch.N_rot_switch-=1

        
    def connection_status(self):
        if (self.essHandle != 0):
                self.connection_status = 'ESS initialized'
        else:
                self.connection_status = 'Error on ESS initialisation. Please check that device is plugged in.'
        

    def __get_serial_number(self):
        # Get serial number of the ESS associated to the session
        C_error = c_char()                              # State return of dll functions
        mySerial = c_ushort(0)              # Get device SN
        myVersion = c_ushort(0)             # Get device version
        C_error = self.lib_ess.ess_get_serial(self.essHandle, byref(mySerial), byref(myVersion))
    # Get status and SN value of called library function
        if (C_error == 0):
                print ('SWITCHBOARD SN: ', mySerial.value, ' version: ', myVersion.value)
        else:
                print ('Failed to get ESS SN and version.')
        self.serial_number = mySerial.value
        self.version = myVersion.value

    def get_status(self):
        myPresence = c_char()               # Definition of ROT-SWITCH variables used by dll functions
        myType = c_char()
        myModel = c_char()
        mySoft_Vers = c_char()
        myErr_code = c_char()
        myProcessing = c_char()
        myPosition = c_char()
        self.status = {'presence':None,'type':None,'model':None,'Software version':None}
        models = {'1':'M-SWITCH','3':'L-SWITCH'}
        # Get status on the 1st position switch "A"
        print ('Reading ROT-SWITCH data on 1st position:')
        C_error = self.lib_ess.ess_get_data_rot_switch(self.essHandle, 0, byref(myPresence), byref(myType),
                                        byref(myModel), byref(mySoft_Vers), byref(myErr_code), byref(myProcessing),
                                        byref(myPosition))  # Position 0 is the first switch (N°1 on the board)
    # Display read data
        if ((ord(myPresence.value) == 1) and (ord(myType.value) == 0)): # ord() converts char to decimal
            self.status = {'presence':True,'type':False,'model':models[str(ord(myModel.value))],
                               'Software version':ord(mySoft_Vers.value)}             
            self.switch_position = ord(myPosition.value)
            print (' ROT-SWITCH connected')
            print (' Model (1: M-SWITCH; 3: L-SWITCH): ', ord(myModel.value))
            print (' Software version: ', ord(mySoft_Vers.value))
            print ( 'Switch position: ', ord(myPosition.value))
        else:
            print (' No ROT-SWITCH was found on 1st position')
            

    def set_status(self):
        # Changing 1st switch status
        
        if self.status['presence'] and not self.status['type']:
                myinput("Press ENTER to change switch position")
                # Set ROT-SWITCH position
                self.switch_position = (self.switch_position+1)%2
                C_error = self.lib_ess.ess_set_rot_switch(self.essHandle, 0, self.switch_position, 0)   # Set on 1st channel, shorter sense
                time.sleep(1)                                               # Wait 1second in order to allow switch change





#----------------------------Flow rate platform-----------------------------------



class FRP():
     #each time an flow_rate object is created, N_flow_rate increases
    N_frp = 0
    def __init__(self,verbose = False):
        frpHandle = c_ulong(0)              # Used to get the device handle
        # Load dll into memory
        Nbits_syst = 8 * struct.calcsize("P")
        if Nbits_syst==32:# Load 32 bit dll into memory
            self.lib_frp = ctypes.WinDLL('frp_32.dll')
        else:
            self.lib_frp = ctypes.WinDLL('frp_64.dll')
        # Initialize the first FLOWBOARD in Windows enumeration list
        self.frpHandle = self.lib_frp.frp_initialisation(self.N_frp)
        # After initialization a short delay (at least 500ms) are required to make sure that 
        #   the USB communication is properly established
        time.sleep(1)
        # Print status on FRP initialization
        self.connection_status()
        print(self.connection_status)
        self.__get_serial_number()
        print(self.serial_number)
        self.verbose = verbose
        FRP.N_frp=1


    def connection_status(self):
        if (self.frpHandle != 0):
                self.connection_status = 'FRP initialized'
        else:
                self.connection_status = 'Error on FRP initialisation. Please check that device is plugged in.'

    def __get_serial_number(self):
        # Get serial number of the FRP associated to the session
        C_error = c_char()                              # State return of dll functions
        mySerial = c_ushort(0)              # Get device SN
        C_error = self.lib_frp.frp_data_FB(self.frpHandle, byref(mySerial))
        # Get status and SN value of called library function
        if (C_error == 0):
                print ('FRP SN: ', hex(mySerial.value)[2:])
        else:
                print ('Failed to get FRP SN.')
        self.serial_number = mySerial.value


    def read_flow_rate(self,channel):
        flow_rate = []
        if self.verbose:
            print('reading flow rate on sensor(s) '+str(channel))
        for channel_i in channel:
            C_channel = c_char(chr(channel_i))
            flow = c_short(0)
            scaleFactor = c_ushort(0)
            timeCheck = c_char()
            unit_index = c_char()
            timeBase_index = c_char()
            C_error = self.lib_frp.frp_read_Q(self.frpHandle, C_channel, byref(timeCheck), byref(flow),
                        byref(scaleFactor), byref(unit_index), byref(timeBase_index))
            if (C_error==0):
                Q = FRP.FLOW_RATE(flow.value/scaleFactor.value,
                              ord(timeBase_index.value),
                              ord(unit_index.value))
                flow_rate.append(Q)
                if self.verbose:
                    print(Q)
                
            else:
                    print ('Invalid data or no flowmeter on 1st position') 
            
        return flow_rate


    class FLOW_RATE():
        unit_table = ['nl', 'ul', 'ml', 'cl', 'dl', 'l']            # Used to convert units code
        timeBase_table = ['/µs', '/ms', '/s', '/min', '/h', '/day']# Used to convert timebase code
        def __init__(self,flow_rate,time_unit_code,volume_unit_code):
            self.value = flow_rate
            self.time_unit = self.timeBase_table[time_unit_code]
            self.volume_unit = self.unit_table[volume_unit_code]

        def __str__(self):
            return 'Flow-rate : '+str(self.value)+' '+self.volume_unit+self.time_unit


    def __del__(self):
        B_OK = bool(False) 
        # Close communication port 
        B_OK = self.lib_frp.frp_close(self.frpHandle);
        if (B_OK == True):
                print ('USB connection closed')
        else:# if (B_OK == False):
                print ('Failed to close USB connection')
                
        # Release the DLL
        ctypes.windll.kernel32.FreeLibrary(self.lib_frp._handle)
        self.N_frp-=1
        del self.lib_frp
        print ('FRP library unloaded')
        FRP.N_frp-=1


# Main function executed when this file is called
if __name__ == "__main__":
    mfcs = MFCS_EZ(verbose = True)
    mfcs.purge()
    mfcs.set_pressure([1,2],[150,150])
    p = mfcs.read_pressure([1,2])
    print(p)
    time.sleep(1)
    mfcs.set_pressure([1,2],[0,0])
    p = mfcs.read_pressure([1,2])
    del(mfcs)

    #ess = ROT_switch()
    #ess.get_status()
    #ess.set_status()
    #del(ess)

    frp = FRP(verbose = True)
    frp.read_flow_rate([1,2])
    del frp
