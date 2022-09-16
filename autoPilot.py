# This algorithom is an implementation of Google's AutoPilot for Borge
# to work on Docker

import pickle
import time
import os
# from terminater import terminate
# from edgeManager import has_enough_resource
from operator import itemgetter
import subprocess
import psutil

# Variables for Google AutoPilot Algorithm
recommendation = 0      # recommendation score in int
cpu_halftime = 1800     # 30 mins counted in Seconds
ram_halftime = 3600     # 60 minutes counted in seconds


# Old variables / Will use for custom recommender or our contribution
scaleInterval=300       # Scaling interval is every 5 minutes
unitCPU = 1000000       # 1 core
unitMemory = 16         # Measured in MB
pmApproach = "SPS"      # Priority management approach, choose from "SPS", "wDPS", "cDPS", "sDPS"
priceModel = "PFP"      # Pricing model, choose from "PFP", "PFR", "Hybrid"

networkLatency=5.689    # Average ping time between Edge node and users measured beforehand


cpuStr = "NanoCpus"
memStr = "Memory"

# Method to check current resource usage by a container based on asking
def check_resource_usage(appName, keyString):
    cmd = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,keyString)
    cmdOut = subprocess.check_output(cmd, shell=True, encoding='utf8').replace(',', ' ')
    currentValue = cmdOut.split(": ")
    #print(currentValue[1])
    return currentValue[1]

# Method to check current resource usage by a container for both memory and cpu
def check_allresource_usage(appName):
    cmdCPU = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"NanoCpus")
    cmdCPUOut = subprocess.check_output(cmdCPU, shell=True, encoding='utf8').replace(',', ' ')
    cpuValue = cmdCPUOut.split(": ")
    
    cmdMem = 'docker container inspect %s  | grep -i \'"%s":\'' % (appName,"Memory")
    cmdMemOut = subprocess.check_output(cmdMem, shell=True, encoding='utf8').replace(',', ' ')
    memValue = cmdMemOut.split(": ")
    #print(currentValue[1])
    return cpuValue[1], memValue[1]


def custom_recommender(input1, input2, input3):
    if input1:
        recommendation = 1
    elif input2:
        recommendation = 2
    elif input3:
        recommendation = 3
    else:
        recommendation = 0
    
    return recommendation


def scale_up(appName, sortedRunning, record):
    # measure current allocation
    
    # This is where we get the current CPU allocation for a container
    # cmdCPU = "lxc-cgroup -n %s cpu.cfs_quota_us" % appName
    currentCPU = float(check_resource_usage(appName, cpuStr))
    
    # This is where we get the current Memory allocation for a container
    # cmdMemory = "lxc-cgroup -n %s memory.limit_in_bytes)/1024/1024" % appName
    currrentMemory = float(check_resource_usage(appName, cpuStr))
    
    # only act if container has not been allocated the maximum resources
    if currentCPU < psutil.cpu_count() and currrentMemory < psutil.virtual_memory().total:
        
        # calculate resources to add
        indApp, lxc = next(((index, d) for (index, d) in enumerate(record) if d['App'][0] == appName), None)
        
        # calculate CPU resources to add
        cpu2Add = currentCPU * record[indApp]['violationRate']
        
        # calculate Memory resources to add
        memory2Add = currrentMemory * record[indApp]['violationRate']
        
        if has_enough_resource(cpu2Add, memory2Add):
            # add required resource to the app container
            
            # add required CPU resource to the app container
            os.system('lxc-cgroup -n %s cpu.cfs_quota_us %s' % (appName, currentCPU + cpu2Add))
            
            # add required Memory resource to the app container
            os.system('lxc-cgroup -n %s memory.limit_in_bytes %sM' % (appName, currrentMemory + memory2Add))
            
            # update Scaled Stats in registry
            if record[indApp]['Scale']:
                record[indApp]['Scale'] += 1
            else:
                record[indApp]['Scale'] = 1
        else:
            # terminate other containers from the one with lowest priority
            
            while not has_enough_resource(cpu2Add, memory2Add) and len(sortedRunning) > 1:
                
                # terminate the container with least priority
                terminate(sortedRunning[-1])
                
                # update status in registry
                ind = next((index for (index, d) in enumerate(record) if d['App'] == sortedRunning[-1]['App']), None)
                record[ind]['Status'] = 'off'
                
                # remove this container from sorted list
                del sortedRunning[-1]
            
            # Once the while loop frees up some CPU and Memory in the System

            if has_enough_resource(cpu2Add, memory2Add):
                # add required resource to the app container
                
                # Add required unit of CPU resource from the app container
                os.system('lxc-cgroup -n %s cpu.cfs_quota_us %s' % (appName, currentCPU + cpu2Add))
                
                # Add required unit of Memory resource from the app container
                os.system('lxc-cgroup -n %s memory.limit_in_bytes %sM' % (appName, currrentMemory + memory2Add))
                
                # update Scaled Stats in registry
                if record[indApp]['Scale']:
                    record[indApp]['Scale'] += 1
                else:
                    record[indApp]['Scale'] = 1
            else:
                print ("Scaling up aborted for lack of resources.")
    else:
        print ("Scaling up aborted, maximum resources allocated already.")


def scale_down(appName, record):
    # measure current allocation
    # This is where we get the current CPU allocation for a container
    cmdCPU = "lxc-cgroup -n %s cpu.cfs_quota_us" % appName
    currentCPU = float(subprocess.check_output(cmdCPU, shell=True))

    # This is where we get the current CPU allocation for a container
    cmdMemory = "lxc-cgroup -n %s memory.limit_in_bytes)/1024/1024" % appName
    currrentMemory = float(subprocess.check_output(cmdMemory, shell=True))

    # only act if container has not been allocated the minimum resources
    if currentCPU > unitCPU and currrentMemory > unitMemory:
        # remove one unit of CPU resource from the app container
        os.system('lxc-cgroup -n %s cpu.cfs_quota_us %s' % (appName, currentCPU - unitCPU))
        
        # remove one unit of memory resource from the app container
        os.system('lxc-cgroup -n %s memory.limit_in_bytes %sM' % (appName, currrentMemory - unitMemory))
        
        # update Scaled Stats in registry
        indApp = next((index for (index, d) in enumerate(record) if d['App'][0] == appName), None)
        if record[indApp]['Scale']:
            record[indApp]['Scale'] += 1
        else:
            record[indApp]['Scale'] = 1
    else:
        print ("Scaling down aborted as minimum threshold reached.")


def mw_recommender(input, appName):
    # Select the primary recommender
    if input == 1:
        recommender = 1
    elif input == 2:
        recommender = 2
    elif input == 3:
        recommender = 3
    else:
        recommender = 0
    # measure current allocation
    # This is where we get the current CPU allocation for a container
    cmdCPU = "lxc-cgroup -n %s cpu.cfs_quota_us" % appName
    currentCPU = float(subprocess.check_output(cmdCPU, shell=True))
    # This is where we get the current Memory allocation for a container
    cmdMemory = "lxc-cgroup -n %s memory.limit_in_bytes)/1024/1024" % appName
    currrentMemory = float(subprocess.check_output(cmdMemory, shell=True))
    


    return recommendation


# Optional for custom recommendation
def calculate_ps(lxc):
    if pmApproach == 'SPS':
        ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty'])
    if pmApproach == 'wDPS':
        if priceModel == 'PFP':
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + 1/float(lxc['Requests']) + 1/float(lxc['Users']) + 1/float(lxc['Data'])
        else:
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + lxc['Requests'] + lxc['Users'] + lxc['Data']
    if pmApproach == 'cDPS':
        if priceModel == 'PFP':
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + 1/float(lxc['Requests']) + 1/float(lxc['Users']) + 1/float(lxc['Data']) + lxc['Reward']
        else:
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + lxc['Requests'] + lxc['Users'] + lxc['Data'] + lxc['Reward']
    if pmApproach == 'sDPS':
        # initalise scale factor
        if not lxc.get('Scale'):
            lxc['Scale'] = 1
        if priceModel == 'PFP':
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + 1/float(lxc['Requests']) + 1/float(lxc['Users']) + 1/float(lxc['Data']) + lxc['Reward'] + 1/float(lxc['Scale'])
        else:
            ps = lxc['Aging'] + 1/float(lxc['ID']) + float(lxc['Premium'][0]) + float(lxc['Loyalty']) + lxc['Requests'] + lxc['Users'] + lxc['Data'] + lxc['Reward'] + 1/float(lxc['Scale'])
    return ps


def release_ports(lxc):
    """
    Release ports from Edge node
    """
    for p in lxc['Ports']:
        os.system('iptables -t nat -D PREROUTING -i eth0 -p tcp --dport %d -j DNAT --to %s:%d' % (p, lxc['IP'], p))
    print ("Done port releasing.")


def migrate(lxc):
    print("This is a dummy function")


def terminate(lxc):
    if lxc['Database'] == 'Yes':
        migrate(lxc)
    os.system('lxc-stop -n %s' % lxc['App'])
    os.system('lxc-destroy -n %s' % lxc['App'])
    release_ports(lxc)
    print ('%s is terminated.') % lxc['App']


def has_enough_resource(cpuLimit, memoryLimit):
    # measure current system usage
    print ("Checking resource availability...")
    
    # Check available CPU in the System
    availableCPU = 100 - psutil.cpu_percent()

    # Check available Memory in the System
    availableMemory = psutil.virtual_memory()[1]/1024/1024

    print ("Free CPU: %s, free memory: %s") % (availableCPU, availableMemory)
	
    if availableCPU >= cpuLimit and availableMemory >= memoryLimit:
        return True


def auto_pilot():
    if os.path.exists("contList.txt"):
        with open("contList.txt", 'rb') as f:
            contList = pickle.load(f)
        # scale running LXC only
        runningLXC = [d for d in contList if d['Status'] == 'on']
        if len(runningLXC) > 0:
            print ("%d LXCs to scale") % len(contList)
            if pmApproach == "SPS":
                for lxc in runningLXC:
                    if not lxc.get('Priority'):
                        lxc['Priority'] = calculate_ps(lxc)
            else:
                for lxc in runningLXC:
                    lxc['Priority'] = calculate_ps(lxc)
            # sort by priority
            sortedLXC = sorted(runningLXC, key=itemgetter('Priority'), reverse=True)
            for lxc in sortedLXC:
                ind = next((index for (index, d) in enumerate(contList) if d['App'] == lxc['App']), None)
                # check activeness
                if lxc['Requests'] > 0 and networkLatency < float(lxc['Objective'][0]):
                    print ("Scaling %s") % lxc['App'][0]
                    appLatency = networkLatency + lxc['computeLatency']
                    if appLatency > float(lxc['Objective'][0]):
                        scale_up(lxc['App'][0], sortedLXC, contList)
                    elif appLatency > float(lxc['Threshold'][0]) * float(lxc['Objective'][0]):
                        if lxc['Donation'][0] == 'Yes':
                            scale_down(lxc['App'][0], contList)
                            # update Reward in registry
                            contList[ind]['Reward'] += 1
                    else:
                        scale_down(lxc['App'][0], contList)
                else:
                    print ("App %s will be terminated due to inactivity or long network delay.") % lxc['App']
                    terminate(lxc)
                    # update status in registry
                    contList[ind]['Status'] = 'off'
                    # remove this lxc from sorted list
                    del sortedLXC[-1]
        else:
            print ("No running LXCs to scale.")

while True:
    auto_pilot()
    time.sleep(scaleInterval)
