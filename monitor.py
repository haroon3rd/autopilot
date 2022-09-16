import os
import time
import timeit
import subprocess
import configparser
import fifoQueue
import docker
import logging.config
from threading import Thread
from datetime import datetime
from logging.handlers import RotatingFileHandler
import pickle


#lxcPath="/var/lib/lxc/"

# Most important time constatnts in seconds
updateInterval= 30           # Scaling interval in seconds
agrgt_interval = 300
cpuHalfLife = 60
memoryHalfLife = 120

# Scaling Constants
upFactor = 1.75
downFactor = 0.75
lastCPU = 0.0
lastMemory = 0.0

# Other important time constatnts in seconds
recordLengthinSec = 7200    # Record Length is 7200 Secs, e.g: 48 Samples of 5 mins aggregation 
monitorInterval = 1         # Monitor interval is 2 Secs i.e: added by I/O delay

agrgtSize = agrgt_interval/(monitorInterval+2) # 5 minutes aggreagtion period.
                                    # Aggregation Sample size  = 5 mins divided by monitor interval
                                    # (2 Sec for I/O delay in monitoring e.g: "docker stats")

# Record and FifoQueue related variables
maxQueueSize = recordLengthinSec/(monitorInterval)
cpuQueueMap = dict()
memQueueMap = dict()

# Record and Bucket related variables
cpuBucketMap = dict() # this bucket will store CPU data in samples per bucket upper border
#memBucketMap = dict()
cpuBucWidth = 5000000     # in milicores
#memBucWidth = 5     # in MBits

# CPU and Memory scaling unit
unitCPU = 10000         # 1/100 core
unitMemory = 16         # Measured in MB

cpuMin = 50000000   # Min CPU in nanocores
cpuMax = 1000000000 # Max CPU in nanocores
cpuMinMil = 100     # Min CPU in milicores
cpuMaxMil = 1000    # Max CPU in milicores


# constants related to CPU and Memory unit conversions
nano2Mili = 0.000001     # NanoCPU to MiliCPU conversion multiplier
percentToNano = 10000000 # 1000000000/100 (NanoCores)
percentToMili = 10       # percent(100)*10 = 1000 (MiliCores)
sigavToMili = 5
bit2Mbit = 1/(1024*1024) # bit value to MBit conversion multiplier

# docker specific string, for "docker container inspect"
cpuStr = "NanoCpus"
memStr = "Memory"

# docker client
client = docker.from_env()
scaleModel = 'CPU'
subModel = 0

def initRotatingLog(logFolderPath, logFileName, configFile, loggerName):
    if not os.path.exists(logFolderPath):
        os.makedirs(logFolderPath)
    logging.config.fileConfig(configFile)
    logger = logging.getLogger(loggerName)
    fh = RotatingFileHandler(logFolderPath + '/' + logFileName + '-{:%Y%m%d-%H.%M.%S}.log'.format(datetime.now()), mode='a+', maxBytes=5*1024*1024,backupCount=2, encoding=None, delay=0)
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

myLogger = initRotatingLog("logs","Autopilot", "logConfig.conf", "Monitor")

DEBUG = myLogger.debug 	#10
INFO = myLogger.info	#20
WARNING = myLogger.warning	#30
ERROR = myLogger.error	#40
CRITICAL = myLogger.critical	#50



# Method to check current resource usage by a container based on asking
def check_resource_usage(appName, keyString):
    """ Check resource usage of a container based on keyString """
    cmd = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,keyString)
    cmdOut = subprocess.check_output(cmd, shell=True, encoding='utf8').replace(',', ' ')
    currentValue = cmdOut.split(": ")
    #print(currentValue[1])``
    return currentValue[1]


# Method to check current resource usage by a container for both memory and cpu
def check_allresource_usage(appName):
    """ Check resource usage of a container for both memory and cpu """
    cmdCPU = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"NanoCpus")
    cmdCPUOut = subprocess.check_output(cmdCPU, shell=True, encoding='utf8').replace(',', ' ')
    cpuValue = cmdCPUOut.split(": ")

    cmdMem = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"Memory")
    cmdMemOut = subprocess.check_output(cmdMem, shell=True, encoding='utf8').replace(',', ' ')
    memValue = cmdMemOut.split(": ")
    #print(currentValue[1])
    return cpuValue[1], memValue[1]


# get docker container list
def container_list():
    """ Get list of containers """
    contList = list()
    for container in client.containers.list():
        contList.append(container.name)
    return contList


# Old and not using right now
def calculate_latency(log, objective):
    """ Calculate latency of a container """
    cmd = "grep 'startTime\|endTime' %s/serverLog | grep --no-group-separator -B1 ^'endTime' | awk '{s=$2;getline;print $2-s;next}'" % log
    latency = subprocess.check_output(cmd, shell=True).rstrip('\n').split('\n')
    computeLatency = sum(map(float, latency)) / len(latency)
    violationRate =  sum(float(i) > float(objective) for i in latency) / len(latency)
    return computeLatency, violationRate


# get usage stats by docker containers
def get_usage():
    """ Get resource usage stats by docker containers """
    #print("Getting usage...")
    cmd = 'docker stats --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}"'
    stats = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n').split('\n')
    for stat in stats:
        stat = stat.split()
        if stat[0] != 'NAME':
            stat[1] = remove_percent(stat[1]) #stat[1][:-1]
            stat[2] = remove_unit(stat[2])
            DEBUG(stat[0] + " has a CPU usage of " + stat[1]*10 + "Milicore and a memory usage of " + stat[2] + " MByte" )


# remove % from CPU usage
def remove_percent(data):
    """ Remove % from CPU usage """
    if data != None and len(data) > 1:
        data = data[:-1]
    return data


# remove MiB from Memory data
def remove_unit(data):
    """ Remove MiB from Memory data """
    if data != None and len(data) > 3:
        data = data[:-3]
    return data

def scale_up(appName, cpuM, cpuRec, memM, memRec):
    #print("Scaling up '" + appName + "'" )
    INFO("Scaling up '" + appName + "'")
    # measure current allocation

    # only act if container has not been allocated the maximum resources
    if cpuM !=0:
        # This is where we get the current CPU allocation for a container
        # cmdCPU = "lxc-cgroup -n %s cpu.cfs_quota_us" % appName
        global lastCPU
        if (cpuRec*upFactor)/1000<=1.0 and abs(cpuRec-lastCPU)>=0.2*lastCPU:
            # Check if CPU scaling is required..
            lastCPU = cpuRec
            cmd = "docker update --cpus=%s %s" % (round((cpuRec*upFactor)/1000,3), appName)
            #print("docker update --cpus=%s %s" % (round((currentCPUMili*1.35)/1000,3), appName))
            INFO("docker update --cpus=%s %s" % (round((cpuRec*upFactor)/1000,3), appName))
            statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n').split('\n')
        
        
        #currentCPUMili = float(check_resource_usage(appName, cpuStr))*nano2Mili

        # if (currentCPUMili*upFactor)/1000<=1:
        #     # Check if CPU scaling is required..
        #     cmd = "docker update --cpus=%s %s" % (round((currentCPUMili*upFactor)/1000,3), appName)
        #     #print("docker update --cpus=%s %s" % (round((currentCPUMili*1.35)/1000,3), appName))
        #     INFO("docker update --cpus=%s %s" % (round((currentCPUMili*upFactor)/1000,3), appName))
        #     statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n').split('\n')

    if memM !=0:
        # This is where we get the current Memory allocation for a container
        # cmdMemory = "lxc-cgroup -n %s memory.limit_in_bytes)/1024/1024" % appName
        currrentMemory = float(check_resource_usage(appName, memStr))*bit2Mbit
        # Check if Memory scaling is required..
        cmd = "docker update -m %sM %s" % (unitMemory*memM + currrentMemory, appName)
        INFO("docker update -m %sM %s" % (unitMemory*memM + currrentMemory, appName))
        statsMemory = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n').split('\n')


def scale_down(appName, cpuM, cpuRec, memM, memRec):
    #print("Scaling down '" + appName + "'" )
    INFO("Scaling down '" + appName + "'")
    # measure current allocation
    # only act if container has not been allocated the maximum resources
    if cpuM !=0:
        # This is where we get the current CPU allocation for a container
        # cmdCPU = "lxc-cgroup -n %s cpu.cfs_quota_us" % appName
        global lastCPU
        if (cpuRec*downFactor)>= cpuMinMil and abs(cpuRec-lastCPU)>=0.2*lastCPU:
            # Check if CPU scaling is required..
            lastCPU = cpuRec
            cmd = "docker update --cpus=%s %s" % (round((cpuRec*downFactor)/1000,3), appName)
            #print("docker update --cpus=%s %s" % (round((currentCPUMili*0.75)/1000,3), appName))
            INFO("docker update --cpus=%s %s" % (round((cpuRec*downFactor)/1000,3), appName))
            statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')#.split('\n')
        elif (cpuRec*downFactor) < cpuMinMil and cpuRec > cpuMinMil:
            lastCPU = cpuRec
            cmd = "docker update --cpus=0.1 %s" % appName
            #print("docker update --cpus=0.05 %s" % appName)
            INFO("docker update --cpus=0.1 %s" % appName)
            statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')#.split('\n')
        
        
        # currentCPUMili = float(check_resource_usage(appName, cpuStr))*nano2Mili
        # if (currentCPUMili*downFactor)>= 50:
        #     # Check if CPU scaling is required..
        #     cmd = "docker update --cpus=%s %s" % (round((currentCPUMili*downFactor)/1000,3), appName)
        #     #print("docker update --cpus=%s %s" % (round((currentCPUMili*0.75)/1000,3), appName))
        #     INFO("docker update --cpus=%s %s" % (round((currentCPUMili*downFactor)/1000,3), appName))
        #     statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')#.split('\n')
        # elif (currentCPUMili)> 50:
        #     cmd = "docker update --cpus=0.05 %s" % appName
        #     #print("docker update --cpus=0.05 %s" % appName)
        #     INFO("docker update --cpus=0.05 %s" % appName)
        #     statsCPU = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')#.split('\n')

    if memM !=0:
        # This is where we get the current Memory allocation for a container
        # cmdMemory = "lxc-cgroup -n %s memory.limit_in_bytes)/1024/1024" % appName
        currrentMemory = float(check_resource_usage(appName, memStr))*bit2Mbit
        # Check if Memory scaling is required..
        cmd = "docker update -m %sM %s" % (currrentMemory - unitMemory*memM, appName)
        #print("docker update -m %sM %s" % (currrentMemory - unitMemory*memM, appName))
        statsMemory = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')#.split('\n')


def doCPUScaling():
    print()

def signalAvg(aDict):
    sAvgDict = dict()
    for key, value in aDict.items():
        upSum = 0.
        downSum = 0.
        weight=0.
        current = timeit.default_timer()
        for key1, value1 in value.items():
            upSum += float(key1) * 2**(-(float(current)-float(value1))/cpuHalfLife)
            downSum += 2**(-(float(current)-float(value1))/cpuHalfLife)
        sAvg = (upSum/downSum)*1.1
        #value.clear()
        sAvgDict.update({key : str(sAvg)})
        #print("CPU average Signal for '" + key + "' is : " +  str(sAvg))
        INFO("CPU average Signal for '" + key + "' is : " +  str(sAvg))
    return sAvgDict


# def signalAvg_old(aDict):
#     sAvgDict = dict()
#     for key, value in aDict.items():
#         upSum = 0
#         downSum = 0
#         for key1, value1 in value.items():
#             upSum += int(key1) * int(value1)
#             downSum += int(value1)
#         sAvg = upSum/downSum
#         value.clear()
#         sAvgDict.update({key : str(sAvg)})
#         #print("CPU average Signal for '" + key + "' is : " +  str(sAvg))
#         INFO("CPU average Signal for '" + key + "' is : " +  str(sAvg))
#     return sAvgDict


# get docker container resource usage and log
def monitor():
    INFO("########################-Monitoring Begins-######################## ")
    INFO("Scaling interval  = " + str(updateInterval) + " and CPU HalfLife = " + str(cpuHalfLife) + " UP is " + str(upFactor) + " down is " + str(downFactor))
    contList = container_list()
    for container in contList:
        cpuQ = fifoQueue.fifoQueue(maxQueueSize)
        cpuQueueMap.update({container : cpuQ})
        cpuBuc = dict()
        cpuBucketMap.update({container : cpuBuc})

        memQ = fifoQueue.fifoQueue(maxQueueSize)
        memQueueMap.update({container : memQ})
        #memBuc = dict()
        #memBucketMap.update({container : memBuc})

    argBegin = timeit.default_timer()
    #agrTime = timeit.default_timer()
    while True:
        start = timeit.default_timer()
        t = time.localtime()
        #current_time = time.strftime("%H:%M:%S", t)
        #print(str(current_time) + " -- While Loop ----------- ")
        WARNING("----------- While Loop ----------- ")
        cmd = 'docker stats --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}"'
        stats = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n').split('\n')
        #print("I am working...2")
        for stat in stats:
            stat = stat.split()
            #print(stat)
            DEBUG(stat)
            if stat[0] != 'NAME':
                #print("I am working...3")
                stat[1] = remove_percent(stat[1])
                stat[2] = remove_unit(stat[2])
                DEBUG(stat[0] + " CPU usage :" + stat[1] + " percent core and memory usage :" + stat[2] + " MBits")
                tempFifoQ = cpuQueueMap.get(stat[0])#.put(stat[1])
                tempFifoQ.put(stat[1])
                DEBUG("Temp Fifo Queue for " + stat[0] + " is : " + str(tempFifoQ))
                tempDict = cpuBucketMap.get(stat[0])
                # added after mod
                agrKey = tempFifoQ.agrSignal(agrgt_interval)
                #WARNING(stat[0] + " - AGRKEY = " + str(agrKey))
                tempDict.update({str(agrKey):str(timeit.default_timer())})
                # commented out after mod
                # if tempDict is not None:
                #     if str(int(float(stat[1])*percentToNano/cpuBucWidth)+1) in tempDict:
                #         tempDict.update({str(int(float(stat[1])*percentToNano/cpuBucWidth)+1):str(int(tempDict.get(str(int(float(stat[1])*percentToNano/cpuBucWidth)+1)))+1)})
                #     else:
                #         tempDict.update({str(int(float(stat[1])*percentToNano/cpuBucWidth)+1):'1'})

                DEBUG(tempDict)
                tempFifoQ = memQueueMap.get(stat[0])#.put(stat[2])
                tempFifoQ.put(stat[2])
                #print(tempFifoQ)

                """
                tempDict = memBucketMap.get(stat[0])
                if tempDict is not None and (str(int(float(stat[2])/memBucWidth)+1) in tempDict): 
                    tempDict.update({str(int(float(stat[2])/memBucWidth)+1) : str(int(tempDict.get(str(int(float(stat[2])/memBucWidth)+1)))+1)})
                else:
                     tempDict.update({str(int(float(stat[2])/memBucWidth)+1) :'1' })
                #print(tempDict)
                """
        #print(client.containers.list())
        
        # Scaling decisions here..
        if timeit.default_timer() - argBegin >= updateInterval:
            sigAvgDict = signalAvg(cpuBucketMap)
            #print(type(cpuBucketMap))
            contList = container_list()
            for container in contList:
                INFO(container + " : " + str(cpuQueueMap.get(container)))
                #currentCPU = float(check_resource_usage(container, cpuStr))#*nano2Mili
                currentCPUMil = float(check_resource_usage(container, cpuStr))*nano2Mili
                DEBUG(container + ", current CPU Share : " + str(currentCPUMil))
                if container in sigAvgDict:
                    sigAvMil = float(sigAvgDict.get(container))*sigavToMili
                    #print(container + " Savg :\t" + str(sigAvMil) + " mCores")
                    INFO(container + " Signal Average in MiliCore :\t" + str(sigAvMil))
                    if (sigAvMil > 0.90*currentCPUMil) and (currentCPUMil < cpuMaxMil):
                        scale_up(container, 1, sigAvMil, 0, 0)
                    elif (sigAvMil < 0.70*currentCPUMil) and (currentCPUMil > cpuMinMil):
                        scale_down(container, 1, sigAvMil, 0, 0)
                    # if (sigAvMil > 0.85*currentCPU*nano2Mili) and (upFactor*currentCPU < cpuMax):
                    #     scale_up(container, 1, sigAvMil, 0, 0)
                    # elif (sigAvMil < 0.75*currentCPU*nano2Mili) and (currentCPU > cpuMin):
                    #     scale_down(container, 1, sigAvMil, 0, 0)
            argBegin = timeit.default_timer()

        DEBUG("Loop time is :" + str(timeit.default_timer() - start))

        #time.sleep(monitorInterval)


if __name__ == "__main__":
    #get_usage()
    monitor()
    #while True:
    #    monitor()
        #time.sleep(updateInterval)

