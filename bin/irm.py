#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import serial
import time
import json
import argparse
import os

here = os.path.abspath(os.path.dirname(__file__))
ir_serial = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
#ir_serial = serial.Serial("/dev/tty.usbmodem01231", 9600, timeout = 1)

def temperIR(path):
  print "Temperature IR..."
  ir_serial.write("T\r\n")
  time.sleep(3.0)
  msg = ir_serial.readline()
  #print msg
  celsiusTemp = None
  try:
    celsiusTemp = ((5.0 / 1024.0 * float(msg)) - 0.4) / 0.01953
  except (ValueError, TypeError):
    print "Error: raw => %s, status => %s" % (msg, status)

  print "%s" % celsiusTemp

  if path and not 'Error' in msg:
    txt_temperature = str(celsiusTemp)
    f = open(path, 'w')
    f.write(txt_temperature)
    f.close()
    sys.exit()

def captureIR(path):
  print "Capturing IR..."
  ir_serial.write("c\r\n")
  time.sleep(3.0)
  msg = ir_serial.readline()
  print msg
  if path and not 'Time Out' in msg:
    saveIR(path)

def playIR(path):
  if path and os.path.isfile(path):
    print ("Playing IR with %s ..." % path)
    f = open(path)
    data = json.load(f) 
    f.close()
    recNumber = len(data['data'])
    rawX = data['data']

    ir_serial.write("n,%d\r\n" % recNumber)
    ir_serial.readline()

    postScale = data['postscale']
    ir_serial.write("k,%d\r\n" % postScale)
    #time.sleep(1.0)
    msg = ir_serial.readline()
    #print msg
    
    for n in range(recNumber):
        bank = n / 64
        pos = n % 64
        if (pos == 0):
          ir_serial.write("b,%d\r\n" % bank)
    
        ir_serial.write("w,%d,%d\n\r" % (pos, rawX[n]))
    
    ir_serial.write("p\r\n")
    msg = ir_serial.readline()
    print msg
    #ir_serial.close() 
  else:
    print "Playing IR..."
    ir_serial.write("p\r\n")
    time.sleep(1.0)
    msg = ir_serial.readline()
    print msg

def saveIR(path):
  print ("Saving IR data to %s ..." % path)
  rawX = []
  ir_serial.write("I,1\r\n")
  time.sleep(1.0)
  recNumberStr = ir_serial.readline()
  recNumber = int(recNumberStr, 16)
  
  ir_serial.write("I,6\r\n")
  time.sleep(1.0)
  postScaleStr = ir_serial.readline()
  postScale = int(postScaleStr, 10)
  
  #for n in range(640):
  for n in range(recNumber):
      bank = n / 64
      pos = n % 64
      if (pos == 0):
          ir_serial.write("b,%d\r\n" % bank)
  
      ir_serial.write("d,%d\n\r" % pos)
      xStr = ir_serial.read(3) 
      xData = int(xStr, 16)
      rawX.append(xData)
  
  data = {'format':'raw', 'freq':38, 'data':rawX, 'postscale':postScale}

  f = open(path, 'w')
  json.dump(data, f)
  f.close()
  print "Done !"

if __name__ == "__main__":
  # parse options
  parser = argparse.ArgumentParser(description='irMagician CLI utility.')
  parser.add_argument('-c', '--capture', action="store_true", dest="cap", help="capture IR data", default=False)
  parser.add_argument('-p', '--play', action="store_true", dest="play", help="play IR data", default=False)
  parser.add_argument('-s', '--save', action="store_true", dest="save", help="save IR data", default=False)
  parser.add_argument('-t', '--temper', action="store_true", dest="temper", help="temper IR data", default=False)
  parser.add_argument('-f', '--file', action="store", dest="file", help="IR data file (json)", default=False)
  args = parser.parse_args()

  if args.play:
    playIR(args.file)

  if args.save and args.file:
    saveIR(args.file)

  if args.cap:
    captureIR(args.file)

  if args.temper:
    temperIR(args.file)


  # release resources 
  ir_serial.close()

