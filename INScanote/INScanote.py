'''
Created on 15 mai 2017

@author: arthur
'''

import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math
import os
from gps import *
import threading
 
gpsd = None #seting the global variable
 
os.system('clear') #clear the terminal (optional)

SETTINGS_FILE = "RTIMULib"


def computeHeight(pressure):
    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263));
    
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer


if __name__ == '__main__':
    gpsp = GpsPoller() # create the thread
    print("Using settings file " + SETTINGS_FILE + ".ini")
    if not os.path.exists(SETTINGS_FILE + ".ini"):
        print("Settings file does not exist, will be created")
    s = RTIMU.Settings(SETTINGS_FILE)
    imu = RTIMU.RTIMU(s)
    pressure = RTIMU.RTPressure(s)

    print("IMU Name: " + imu.IMUName())
    print("Pressure Name: " + pressure.pressureName())

    if (not imu.IMUInit()):
        print("IMU Init Failed")
        sys.exit(1)
    else:
        print("IMU Init Succeeded");

    # this is a good time to set any fusion parameters

    imu.setSlerpPower(0.02)
    imu.setGyroEnable(True)
    imu.setAccelEnable(True)
    imu.setCompassEnable(True)

    if (not pressure.pressureInit()):
        print("Pressure sensor Init Failed")
    else:
        print("Pressure sensor Init Succeeded")

    poll_interval = imu.IMUGetPollInterval()
    print("Recommended Poll Interval: %dmS\n" % poll_interval)

    try:
        gpsp.start() # start it up
        while True:
            #It may take a second or two to get good data
            #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
         
              
            os.system('clear')
         
            print
            print ' GPS reading'
            print '----------------------------------------'
            print 'latitude    ' , gpsd.fix.latitude
            print 'longitude   ' , gpsd.fix.longitude
            print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
            print 'altitude (m)' , gpsd.fix.altitude
            print 'eps         ' , gpsd.fix.eps
            print 'epx         ' , gpsd.fix.epx
            print 'epv         ' , gpsd.fix.epv
            print 'ept         ' , gpsd.fix.ept
            print 'speed (m/s) ' , gpsd.fix.speed
            print 'climb       ' , gpsd.fix.climb
            print 'track       ' , gpsd.fix.track
            print 'mode        ' , gpsd.fix.mode
            print
            print 'sats        ' , gpsd.satellites
            
            if imu.IMURead():
                # x, y, z = imu.getFusionData()
                # print("%f %f %f" % (x,y,z))
                data = imu.getIMUData()
                (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = pressure.pressureRead()
                fusionPose = data["fusionPose"]
                # print("r: %f p: %f y: %f" % (math.degrees(fusionPose[0]), math.degrees(fusionPose[1]), math.degrees(fusionPose[2])))
                print("accX:%f accY:%f accZ:%f" % (data["accel"]))
                print("                    gyrX:%f gyrY:%f gyrZ:%f" % (data["gyro"]))
                print("                                            magX:%f magY:%f magZ:%f" % (data["compass"]))
                #    if (data["pressureValid"]):
                #        print("Pressure: %f, height above sea level: %f" % (data["pressure"], computeHeight(data["pressure"])))
                #    if (data["temperatureValid"]):
                #        print("Temperature: %f" % (data["temperature"]))
                time.sleep(poll_interval*1.0/1000.0)
         
            time.sleep(1) #set to whatever
     
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print "\nKilling Thread..."
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing
        print "Done.\nExiting."
