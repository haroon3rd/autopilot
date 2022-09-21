import configparser
import logging
import sys
from collections import deque
import re
import json

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERR = logging.ERROR
CRIT = logging.CRITICAL


# share_dem = {}
# resource_left = {}

# cur_node = None
# cpu_delta = 50
# lte_delta = 5


# """ Make changes here to change the results """
# n11_cpu_dem = 200
# n21_cpu_dem = 250
# n22_cpu_dem = 250

# n11_lte_dem = 0
# n21_lte_dem = 25
# n22_lte_dem = 25

# leaf_nodes = ["N11", "N21", "N22"]

# A class that represents an individual node in a Tree
# AnyTree


class anyTree:
    def __init__(self, name):
        self.children = []
        self.parent = None
        self.name = name
        self.cpu_dem_vect = 0
        self.lte_dem_vect = 0
        self.mem_dem_vect = 0
        self.dom_share = 0
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self

def build_tree(parents, childs):
    global root
    root = anyTree("N")
    for i in range (int(parents)):
        root.add_child(anyTree("N"+str(i+1)))
        for child in range (int(childs[i])):
            root.children[i].add_child(anyTree("N"+str(i+1)+str(child+1)))
    # Lets print the tree for debugging
    preTravTree(root)

def isLeafNode(root):
    if len(root.children) == 0:
        return True
    else:
        return False


def preTravTree(root):
 
    Stack = deque([])
    # 'Preorder'-> contains all the visited nodes.
    Preorder =[] 
    Preorder.append(root.name)
    Stack.append(root)
    while len(Stack)>0:
        # 'Flag' checks whether all the child nodes have been visited.
        flag = 0
        # CASE 1- If Top of the stack is a leaf node then remove it from the stack:
        if len((Stack[len(Stack)-1]).children)== 0:
            X = Stack.pop()
            # CASE 2- If Top of the stack is Parent with children:
        else:
            Par = Stack[len(Stack)-1]
        # a)As soon as an unvisited child is found(left to right sequence),
        # Push it to Stack and Store it in Auxiliary List(Marked Visited)
        # Start Again from Case-1, to explore this newly visited child
        for i in range(0, len(Par.children)):
            if Par.children[i].name not in Preorder:
                flag = 1
                Stack.append(Par.children[i])
                Preorder.append(Par.children[i].name)
                break;
                # b)If all Child nodes from left to right of a Parent have been visited
                # then remove the parent from the stack.
        if flag == 0:
            Stack.pop()
    print(Preorder)

def assign_resource_share(root, resource):
    global parents
    global demand_list
    child_count = 0
    for i in range (int(parents)):
        for child in range (int(childs[i])):
            current_list = demand_list[child_count]
            if resource == "cpu":
                cpu = int(current_list[0])    
                if cpu != 0:
                    cpu_dem_dict.update({root.children[i].children[child].name : cpu})
            elif resource == "mem":
                mem = int(current_list[1])
                if mem != 0:
                    mem_dem_dict.update({root.children[i].children[child].name : mem})
            elif resource == "bw":
                lte = int(current_list[2])
                if lte != 0:
                    lte_dem_dict.update({root.children[i].children[child].name : lte})
            child_count += 1
    if resource == "cpu":
        print(cpu_dem_dict)
    elif resource == "mem":
        print(mem_dem_dict)
    elif resource == "bw":
        print(lte_dem_dict)

def calculate_deltas(delta_list, resource):
    global cpu_delta
    global lte_delta
    global mem_delta
    if resource == "cpu":
        cpu_alloc_delta = int(delta_list[0])/float(min(cpu_dem_dict.values()))
        deltas.update({"cpu" : cpu_alloc_delta})
        log(INFO,"CPU Allocation Delta: " + str(cpu_alloc_delta))
    elif resource == "mem":
        mem_alloc_delta = int(delta_list[1])/float(min(mem_dem_dict.values()))
        deltas.update({"mem" : mem_alloc_delta})
        log(INFO,"MEM Allocation Delta: " + str(mem_alloc_delta))
    elif resource == "bw":
        lte_alloc_delta = int(delta_list[2])/float(min(lte_dem_dict.values()))
        deltas.update({"bw" : lte_alloc_delta})
        log(INFO,"BW Allocation Delta: " + str(lte_alloc_delta))





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



# Log helper function
def log(level, message):
    logging.log(level, message)

# # Write to config file
# def update_config_file():
#     with open('hdrf_config.conf', 'w') as configFile:
#         config.write(configFile)


cpu_dem_dict = {}
cpu_share_dict = {}
lte_dem_dict = {}
lte_share_dict = {}
mem_dem_dict = {}
mem_share_dict = {}


# Logger configuration
def init_logger(filename):
    config.read(filename)
    logLevel = config.get("LOGGING", "level")
    logFile = config.get("LOGGING", "logFile")
    logging.basicConfig(filename=logFile, filemode='a+', format='%(asctime)s | %(levelname)s : %(message)s', level=logLevel)
    log(INFO, "**********************************************")


#Radu code

def parse_config_vector(s):
    # print("parsing: " + s)
    return re.split(r',', s[1:-1])

   

def init_from_config(iniFile):
    total_children = 0
    global parents
    global childs
    global resource_types
    global demand_list
    global initial_qty_list
    global delta_list
    try:
        config.read(iniFile)
        parents = config.get("NODES", "parents")
        print("Nodes:\t\t" + parents)

        ###
        children_list =  parse_config_vector(config.get("NODES", "children"))
        childs = children_list
        for i in children_list:
            total_children += int(i)
        print("Children:\t" + ' '.join(children_list), "=", total_children, "(total)")

        ###
        resource_types = parse_config_vector(config.get("RESOURCES", "types"))
        print("Resources: \t" + ' '.join(resource_types))

        ###
        initial_qty_list = parse_config_vector(config.get("RESOURCES", "initial-qty"))
        print("Initial qty: \t" + ' '.join(initial_qty_list))
        if(len(resource_types) != len(initial_qty_list)):
           print("Number of resurces and initial qty resources do not match")

        ###
        delta_list =  parse_config_vector(config.get("RESOURCES", "delta"))
        print("Delta: \t\t" + ' '.join(delta_list))
        if(len(resource_types) != len(delta_list)):
           print("Number of resurces and list of deltas do not match")
        else:
            print(delta_list)

        ###
        demand_list = []
        all_demand_list =  (config.get("RESOURCES", "demand")).split('&')
        if(total_children != len(all_demand_list)):
           print("Number of nodes and list of demands do not match:", total_children, ',', len(all_demand_list))
        else:
            for mylist in all_demand_list:
                demand_list.append(list(mylist.split(",")))
        print(demand_list)
        

           
    except Exception as e:
        print("Error (" + type(e).__name__ + ") with config file: " + str(e))
        sys.exit()


parents = 0
childs = []
deltas = {}
resource_types = []
demand_list = []
initial_qty_list = []
delta_list = []

#Main Function
config = configparser.ConfigParser()
if (len(sys.argv) != 2):
     print("Usage: python3 hdrf.py <config-file>")
     sys.exit()
else:
    init_logger("hdrf.conf")
    init_from_config(sys.argv[1])
    build_tree(parents,childs)
    for resource in resource_types:
        assign_resource_share(root, resource.strip())
        calculate_deltas(delta_list, resource.strip())
    
    print(deltas)

sys.exit()



"""

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

"""

