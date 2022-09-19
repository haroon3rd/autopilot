import configparser
import logging
# from logging import log
import pickle
from queue import Empty

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERR = logging.ERROR
CRIT = logging.CRITICAL


share_dem = {}
resource_left = {}

cur_node = None
cpu_delta = 50
lte_delta = 5


""" Make changes here to change the results """
n11_cpu_dem = 200
n21_cpu_dem = 250
n22_cpu_dem = 250

n11_lte_dem = 0
n21_lte_dem = 25
n22_lte_dem = 25

leaf_nodes = ["N11", "N21", "N22"]

# A class that represents an individual node in a
# Binary Tree

# Binary Tree Class
class myNode:
    def __init__(self, name, dem_cpu, dem_lte):
        self.left = None
        self.right = None
        self.name = name
        self.dem_cpu = dem_cpu
        self.dem_lte = dem_lte
        self.cpu_share = 0
        self.lte_share = 0
        self.cpu_dem_vect = 0
        self.lte_dem_vect = 0
        self.dom_share = 0

# Driver code
root = myNode("N", 0, 0)
root.left = myNode("N1", 0, 0)
root.right = myNode("N2", 0, 0)
root.left.left = myNode("N11", n11_cpu_dem, n11_lte_dem)
root.left.right = None
root.right.left = myNode("N21", n21_cpu_dem, n21_lte_dem)
root.right.right = myNode("N22", n22_cpu_dem, n22_lte_dem)


def isLeafNode(root):
    if root.left is None and root.right is None:
        return True
    else:
        return False
# A function to do inorder tree traversal and print the nodes
def printInorder(root):
    if root:
        # First recur on left child
        printInorder(root.left)
        # then print the data of node
        if root.name in leaf_nodes:
            print(root.name + " " + str(root.dem_cpu) + " " + str(root.dem_lte)),
        # now recur on right child
        printInorder(root.right)

def print_leaf_node_details(root):
    if root:
        # First recur on left child
        print_leaf_node_details(root.left)
        # then print the data of node
        if root.name in leaf_nodes:
            print(root.name + " " + str(root.dem_cpu) + " " + str(root.dem_lte)),
            log(INFO, "Node " + root.name + " - CPU Demand: " + str(root.dem_cpu) + ", LTE Demand: " + str(root.dem_lte) +
             ", CPU Share: " + str(root.cpu_share) + ", LTE Share: " + str(root.lte_share) +
             ", CPU Dem Vector: " + str(root.cpu_dem_vect) + ", LTE Dem Vector: " + str(root.lte_dem_vect) + ", Dom Share: " + str(root.dom_share))
        # now recur on right child
        print_leaf_node_details(root.right)

# A function to do inorder tree traversal and return a dict of cpu demands
def get_parent_dict(root):
    if root and not isLeafNode(root):
        # First recur on left child
        get_parent_dict(root.left)
        if root.left is not None and root.right is not None:
            parent_dict.update({root.name: [root.left.name, root.right.name]})
        elif root.left is not None:
            parent_dict.update({root.name: [root.left.name]})   
        else:
            parent_dict.update({root.name: [root.right.name]})    
        get_parent_dict(root.right)

# A function to do inorder tree traversal and return a dict of cpu demands
def get_cpu_demand(root):
    if root:
        # First recur on left child
        get_cpu_demand(root.left)
        # then print the data of node
        if root.name in leaf_nodes and root.dem_cpu > 0:
            cpu_dem_dict.update({root.name: root.dem_cpu})
        # now recur on right child
        get_cpu_demand(root.right)

# A function to do inorder tree traversal and return a dict of cpu demands
def get_lte_demand(root):
    if root:
        # First recur on left child
        get_lte_demand(root.left)
        # then print the data of node
        if root.name in leaf_nodes and root.dem_lte > 0:
            lte_dem_dict.update({root.name: root.dem_lte})
        # now recur on right child
        get_lte_demand(root.right)

# A function to do inorder tree traversal and return a dict of cpu demands
def get_cpu_demand_vector(root):
    if root:
        # First recur on left child
        get_cpu_demand_vector(root.left)
        # then print the data of node
        if root.dem_cpu > 0:
            root.cpu_dem_vect = (root.dem_cpu/float(total_cpu_demands)*100)
            cpu_dem_vect_dict.update({root.name: root.cpu_dem_vect})
        get_cpu_demand_vector(root.right)

# A function to do inorder tree traversal and return a dict of cpu demands
def get_lte_demand_vector(root):
    if root:
        # First recur on left child
        get_lte_demand_vector(root.left)
        # then print the data of node
        if root.dem_lte > 0:
            root.lte_dem_vect = (root.dem_lte/float(total_lte_demands)*100)
            lte_dem_vect_dict.update({root.name: root.lte_dem_vect})
        
        get_lte_demand_vector(root.right)

def update_parent_demand(root):
    if root and not isLeafNode(root):
        # First recur on left child
        update_parent_demand(root.left)    
        update_parent_demand(root.right)
        log(DEBUG, "Updating :" + root.name)
        if root.left is not None and root.right is not None:
            root.dem_cpu = root.left.dem_cpu + root.right.dem_cpu
            root.dem_lte = root.left.dem_lte + root.right.dem_lte
            log(DEBUG,root.name + " : " + str(root.dem_cpu) + " : " + str(root.dem_lte))
            # parent_dict.update({root.name: [root.left.name, root.right.name]})
        elif root.left is not None:
            root.dem_cpu = root.left.dem_cpu
            root.dem_lte = root.left.dem_lte
            log(DEBUG,root.name + " : " + str(root.dem_cpu) + " : " + str(root.dem_lte))
            # parent_dict.update({root.name: [root.left.name]})   
        else:
            root.dem_cpu = root.right.dem_cpu
            root.dem_lte = root.right.dem_lte
            log(DEBUG,root.name + " : " + str(root.dem_cpu) + " : " + str(root.dem_lte))
            # parent_dict.update({root.name: [root.right.name]})

def print_parent_demands(root):
    if root and not isLeafNode(root):
        # First recur on left child
        print_parent_demands(root.left) 
        log(INFO, root.name + " : " + str(root.dem_cpu) + " : " + str(root.dem_lte))   
        print_parent_demands(root.right)

def allocate_cpu(root):
    global c_cpu
    global cpu_break
    global t_cpu
    if root:
        # First recur on left child
        allocate_cpu(root.left)
        # then print the data of node
        if root.name in leaf_nodes and root.dem_cpu > 0:
            cpu_to_allocate = float(root.dem_cpu)*cpu_alloc_delta
            log(DEBUG, "Trying to Allocate " + str(cpu_to_allocate) + " to " + root.name)
            if cpu_to_allocate <= t_cpu - c_cpu:
                root.cpu_share = float(root.cpu_share) + cpu_to_allocate
                c_cpu += cpu_to_allocate
            else :
                cpu_break = True
                log(DEBUG, "CPU allocation break due to insufficient resources")

            log(DEBUG, "Allocated CPU to " + root.name + " : " + str(root.cpu_share))
            log(DEBUG, "Total CPU allocated : " + str(c_cpu))
        allocate_cpu(root.right)

def allocate_lte(root):
    global c_lte
    global lte_break
    global t_lte
    if root:
        # First recur on left child
        allocate_lte(root.left)
        # then print the data of node
        if root.name in leaf_nodes and root.dem_lte > 0:
            lte_to_allocate = float(root.dem_lte)*lte_alloc_delta
            log(DEBUG, "Trying to Allocate " + str(lte_to_allocate) + " to " + root.name)
            if lte_to_allocate <= t_lte - c_lte:
                root.lte_share = float(root.lte_share) + lte_to_allocate
                c_lte += lte_to_allocate
            else :
                lte_break = True
                log(DEBUG, "LTE allocation break due to insufficient resources")

            log(DEBUG, "Allocated LTE to " + root.name + " : " + str(root.lte_share))
            log(DEBUG, "Total LTE allocated : " + str(c_lte))
        allocate_lte(root.right)


# Log helper function
def log(level, message):
    logging.log(level, message)

# Write to config file
def update_config_file():
    with open('hdrf_config.conf', 'w') as configFile:
        config.write(configFile)


parent_dict = {}
parent_list = []


# Main Algorithm

config = configparser.ConfigParser()
config.read('hdrf_config.conf')

# Logger configuration
logLevel = config.get("LOGGING", "level")
logFile = config.get("LOGGING", "filename")
logging.basicConfig(filename=logFile, filemode='a+', format='%(asctime)s | %(levelname)s : %(message)s', level=DEBUG)
log(INFO, "**********************************************")

t_cpu = int(config.get("TOTALRES", "cpu"))
t_mem = int(config.get("TOTALRES", "mem"))
t_lte = int(config.get("TOTALRES", "lte"))
c_cpu = int(config.get("INITALLOC", "cpu"))
c_mem = int(config.get("INITALLOC", "mem"))
c_lte = int(config.get("INITALLOC", "lte"))

cpu_dem_dict = {}
lte_dem_dict = {}
cpu_dem_vect_dict = {}
lte_dem_vect_dict = {}
dom_share_dict = {}

# Get the parent nodes
get_parent_dict(root)
print("Printing Parent Nodes Dict:")
log(INFO,parent_dict)
print(parent_dict)

# printInorder(root)
get_cpu_demand(root)
log(INFO,"Printing CPU Demands:")
log(INFO,cpu_dem_dict)

total_cpu_demands = sum(cpu_dem_dict.values())
log(INFO,"Total CPU deands: " + str(total_cpu_demands))

get_lte_demand(root)
log(INFO,"Printing LTE Demands:")
log(INFO,lte_dem_dict)

total_lte_demands = sum(lte_dem_dict.values())
log(INFO,"Total LTE demands: " + str(total_lte_demands))

update_parent_demand(root)
print("Printing Parent Demands:")
print_parent_demands(root)

get_cpu_demand_vector(root)
print("Printing Demand Vector Dict:")
print(cpu_dem_vect_dict)

cpu_alloc_delta = cpu_delta/float(min(cpu_dem_dict.values()))
log(INFO,"CPU Allocation Delta: " + str(cpu_alloc_delta))

cpu_break = False
while c_cpu < t_cpu and not cpu_break:
    allocate_cpu(root)

get_lte_demand_vector(root)
print("Printing Demand Vector Dict:")
print(lte_dem_vect_dict)

lte_alloc_delta = lte_delta/float(min(lte_dem_dict.values()))
log(INFO,"LTE Allocation Delta: " + str(lte_alloc_delta))

lte_break = False
while c_lte < t_lte and not lte_break:
    allocate_lte(root)

print("All resources allocated")
print_leaf_node_details(root)


