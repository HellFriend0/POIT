import serial
import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial("/dev/ttyS0")
ser.baudrate = 9600

i =-1
while i <10:
     read_ser = ser.readline()
     print(read_ser.decode())
     print(i)
     p[i] = read_ser.decode()     
     i=i+1
     
i=-1

while i <10:
     ser.write(bytes(x,"utf-8"))
     read_ser = ser.readline()
     print(read_ser.decode())
     print(i)
     p[i] = read_ser.decode()
     i=i+1