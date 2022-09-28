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
        self.cpu_share = 0
        self.lte_share = 0
        self.mem_share = 0
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

def get_total_demand(resource):
    global total_cpu_demands
    global total_mem_demands
    global total_lte_demands
    if resource == "cpu":
        total_cpu_demands = sum(cpu_dem_dict.values())
        log(INFO,"Total CPU demands: " + str(total_cpu_demands))
    elif resource == "mem":
        total_mem_demands = sum(mem_dem_dict.values())
        log(INFO,"Total MEM demands: " + str(total_mem_demands))
    elif resource == "bw":
        total_lte_demands = sum(lte_dem_dict.values())
        log(INFO,"Total BW demands: " + str(total_lte_demands))


def get_demand_vector(root, resource):
    global parents
    global childs
    child_count = 0
    for i in range (int(parents)):
        for child in range (int(childs[i])):
            # current_list = demand_list[child_count]
            if resource == "cpu":
                cpu_dem = cpu_dem_dict.get(root.children[i].children[child].name)
                if cpu_dem != 0 and cpu_dem is not None:
                    root.children[i].children[child].cpu_dem_vect = cpu_dem/float(total_cpu_demands)*100
                    print(root.children[i].children[child].name + " cpu dem vector = " + str(root.children[i].children[child].cpu_dem_vect))
            elif resource == "mem":
                mem_dem = mem_dem_dict.get(root.children[i].children[child].name)
                if mem_dem != 0 and mem_dem is not None:
                    root.children[i].children[child].mem_dem_vect = mem_dem/float(total_mem_demands)*100
                    print(root.children[i].children[child].name + " mem dem vector = " + str(root.children[i].children[child].mem_dem_vect))
            elif resource == "bw":
                lte_dem = lte_dem_dict.get(root.children[i].children[child].name)
                if lte_dem != 0 and lte_dem is not None:
                    root.children[i].children[child].lte_dem_vect = lte_dem/float(total_lte_demands)*100
                    print(root.children[i].children[child].name + " bw dem vector = " + str(root.children[i].children[child].lte_dem_vect))
            child_count += 1

def update_parent_vectors(root, resource):
    global parents
    global childs
    if root:
        for parent in root.children:
            for child in parent.children:
                if isLeafNode(child):
                    if resource == "cpu":
                        parent.cpu_dem_vect += float(child.cpu_dem_vect)
                    elif resource == "mem":
                        parent.mem_dem_vect += float(child.mem_dem_vect)
                    elif resource == "bw":
                        parent.lte_dem_vect += float(child.lte_dem_vect)
                # update_parent_vectors(child, resource)

def update_parent_vector_dict(root, resource):
    global parents
    global childs
    if root:
        for i in range (int(parents)):
            for child in root.children:
                if resource == "cpu":
                    cpu_dem_vect_dict.update({root.name : root.cpu_dem_vect})
                elif resource == "mem":
                    mem_dem_vect_dict.update({root.name : root.mem_dem_vect})
                elif resource == "bw":
                    lte_dem_vect_dict.update({root.name : root.lte_dem_vect})
                # update_parent_vector_dict(child, resource)
    


def update_dom_resource_list(root, resource):
    global total_cpu_demands
    global total_mem_demands
    global total_lte_demands

    print("Resource qty list: " + str(resource_qty_list) + " CPU dem: " + str(total_cpu_demands) + " MEM dem: " + str(total_mem_demands) + " BW dem: " + str(total_lte_demands))

    if resource == "cpu":
        dom_resource_dict.update({resource : total_cpu_demands/float(resource_qty_list[0])})
    elif resource == "mem":
        dom_resource_dict.update({resource : total_mem_demands/float(resource_qty_list[1])})
    elif resource == "bw":
        dom_resource_dict.update({resource : total_lte_demands/float(resource_qty_list[2])})    


def update_res_alloc_order():
    global res_alloc_order
    res_alloc_order = sorted(dom_resource_dict, key=dom_resource_dict.get, reverse=True)
    print("Resource allocation order: " + str(res_alloc_order))

def update_resource_qty_dict():
    global resource_qty_dict
    global resource_qty_list
    global resource_types
    for i in range (len(resource_types)):
        resource_qty_dict.update({resource_types[i].strip() : resource_qty_list[i]})
    # print("Resource qty list: " + str(resource_qty_list))


def allocate_resource(root, resource, total_resource):
    log(DEBUG, "Allocating resource: " + resource)
    resource_remining = 0 
    resource_allocated = 0
    global parents
    global childs
    if root and total_resource is not None:
        for parent in root.children:
            for child in parent.children:
                if isLeafNode(child):
                    if resource == "cpu" and cpu_dem_dict.get(child.name) > 0:
                        resource_to_allocate = float(cpu_dem_dict.get(child.name))*float(deltas.get("cpu"))
                        log(DEBUG, "Trying to Allocate " + str(resource_to_allocate) + "CPU to " + child.name)
                        if resource_to_allocate <= float(total_resource) - float(resource_allocated):
                            child.cpu_share = float(child.cpu_share) + resource_to_allocate
                            resource_allocated += resource_to_allocate
                    elif resource == "mem" and mem_dem_dict.get(child.name) > 0:
                        resource_to_allocate = float(mem_dem_dict.get(child.name))*float(deltas.get("mem"))
                        log(DEBUG, "Trying to Allocate " + str(resource_to_allocate) + "MEM to " + child.name)
                        if resource_to_allocate <= float(total_resource) - float(resource_allocated):
                            child.lte_share = float(child.mem_share) + resource_to_allocate
                            resource_allocated += resource_to_allocate
                    elif resource == "BW" and lte_dem_dict.get(child.name) > 0:
                        resource_to_allocate = float(lte_dem_dict.get(child.name))*float(deltas.get("bw"))
                        log(DEBUG, "Trying to Allocate " + str(resource_to_allocate) + "BW to " + child.name)
                        if resource_to_allocate <= float(total_resource) - float(resource_allocated):
                            child.lte_share = float(child.lte_share) + resource_to_allocate
                            resource_allocated += resource_to_allocate
                    # log(DEBUG, "Allocated CPU to " + root.name + " : " + str(root.cpu_share))
                    # log(DEBUG, "Total CPU allocated : " + str(c_cpu))
                # allocate_resource(child, resource)


# Log helper function
def log(level, message):
    logging.log(level, message)

# # Write to config file
# def update_config_file():
#     with open('hdrf_config.conf', 'w') as configFile:
#         config.write(configFile)

# All dicts used in the program
cpu_dem_dict = {}
cpu_share_dict = {}
mem_dem_dict = {}
mem_share_dict = {}
lte_dem_dict = {}
lte_share_dict = {}

cpu_dem_vect_dict = {}
mem_dem_vect_dict = {}
lte_dem_vect_dict = {}

deltas = {}
dom_resource_dict = {}
resource_qty_dict = {}

# All lists used in the program
res_alloc_order = []
childs = []
resource_types = []
demand_list = []
resource_qty_list = []
delta_list = []

# All global variables used in the program
parents = 0
total_cpu_demands = 0
total_mem_demands = 0
total_lte_demands = 0


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
    global resource_qty_list
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
        resource_qty_list = parse_config_vector(config.get("RESOURCES", "resource-qty"))
        print("Resource qty: \t" + ' '.join(resource_qty_list))
        if(len(resource_types) != len(resource_qty_list)):
           print("Number of resurces and qty of resources do not match")

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
           sys.exit()
        else:
            for mylist in all_demand_list:
                demand_list.append(list(mylist.split(",")))
        print(demand_list)
        

           
    except Exception as e:
        print("Error (" + type(e).__name__ + ") with config file: " + str(e))
        sys.exit()




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
        get_total_demand(resource.strip())
        get_demand_vector(root, resource.strip())
        update_parent_vectors(root, resource.strip())
        update_parent_vector_dict(root, resource.strip())
        update_dom_resource_list(root, resource.strip())
    update_res_alloc_order()
    update_resource_qty_dict()
    
    # log(INFO, "Resource quantity list: " + str(resource_qty_list))
    log(INFO, "Resource quantity dict: " + str(resource_qty_dict))
    log(INFO, "Resource allocation order: " + str(res_alloc_order))

    for resource in res_alloc_order:
        log(INFO, "Allocating " + resource + " to nodes")
        log(INFO, "Resource quantity dict: " + str(resource_qty_dict))
        total_resource = resource_qty_dict.get(str(resource.strip()))
        log(INFO, "Total " + resource + " available: " + str(total_resource))
        allocate_resource(root, resource.strip(), total_resource)
    
    print("Dominant resource dict: ", str(dom_resource_dict))   
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

