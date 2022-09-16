# This algorithom is an implementation of Google's AutoPilot for Borge
# to work on Docker

import pickle
import time
import timeit
import os
import fifoQueue
# from terminater import terminate
# from edgeManager import has_enough_resource
from operator import itemgetter
import subprocess
import psutil

nano2Mili = 0.000001
bit2Mbit = 1/(1024*1024)



def check_resource_usage(appName, keyString):
    cmd = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,keyString)
    cmdOut = subprocess.check_output(cmd, shell=True, encoding='utf8').replace(',', ' ')
    currentValue = cmdOut.split(": ")
    #print(currentValue[1])
    return currentValue[1]

def check_allresource_usage(appName):
    cmdCPU = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"NanoCpus")
    cmdCPUOut = subprocess.check_output(cmdCPU, shell=True, encoding='utf8').replace(',', ' ')
    cpuValue = cmdCPUOut.split(": ")
    
    cmdMem = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"Memory")
    cmdMemOut = subprocess.check_output(cmdMem, shell=True, encoding='utf8').replace(',', ' ')
    memValue = cmdMemOut.split(": ")
    
    #print(currentValue[1])
    return cpuValue[1], memValue[1]

def avgWeightedSignal(mylist, halfSize):      # S(avg)
        total = 0
        wtTotal = 0
        for i in range(len(mylist)):
            #print("Items are : " + str(self[i]))
            wt = 2**(-i/halfSize)
            total = total+ mylist[i]*wt
            wtTotal += wt
        return total/wtTotal

def containerList():
    cmd = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,keyString)
    cmdOut = subprocess.check_output(cmd, shell=True, encoding='utf8').replace(',', ' ')
    currentValue = cmdOut.split(": ")
    #print(currentValue[1])
    return currentValue[1]

def maxSignal(mylist):
        max = 0
        for i in mylist:
            # print(i)
            max = i if i>max else max
        return max


start = timeit.default_timer()
t1 = time.time()
print(t1)
print('Start Time: ', start)
cpuQ = fifoQueue.fifoQueue(20)
memQ = fifoQueue.fifoQueue(20)
cpu, memory =check_allresource_usage("mongodb")
cpuQ.put(float(cpu)*nano2Mili)

#print(float(cpu)*nano2Mili)

#cpuQ.put(float(cpu)*nano2Mili*2)
#print("cpuQ Size " + str(cpuQ.size()))
#print("cpuQ Average Signal " + str(cpuQ.avgSignal()))
memQ.put(float(memory)*bit2Mbit)
print(float(memory)*bit2Mbit)

cpu2 = check_resource_usage("mongodb", "NanoCpus")

mylist = [5,8,6,7,9,4,8,5,9,8,3,4,3]

abc =37
print(int(37/5))
print("BucketList : " + str(mylist))
print("Max Bucket Size : " + str(maxSignal(mylist)))
print(avgWeightedSignal(mylist,12))

#Your statements here

time.sleep(3)
stop = timeit.default_timer()
print('Start Time: ', stop)
print('Age: ', stop - start)  
t2 = time.time()
print(t2)
print('Age 2:', t2-t1)