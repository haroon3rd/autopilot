import configparser
import logging
import sys
from collections import deque
import re
import time

# Get Execution time
start_time = time.time()

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
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
    
    def get_parent(self):
        return self.parent

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
    print("\nOrganizational Structure : ",Preorder)


def assign_resource_share(root,resource_types):
    global parents
    global childs
    global demand_list
    global res_dem_dict
    global nodewise_res_dem_dict
    print("Demand List : ", demand_list)
    for r in range(len(resource_types)):
        res = resource_types[r].strip()
        child_count = 0
        res_dict = {}
        for i in range (int(parents)):
            for child in range (int(childs[i])):
                current_list = demand_list[child_count]
                # print("Current_list : ", current_list)
                current_list[r] = int(current_list[r].strip())
                # print ("Item : ", item.strip())
                if int(current_list[r]) !=0:
                    res_dict.update({root.children[i].children[child].name : current_list[r]})
                child_count += 1
                # print("Res Dict : ", res_dict)
                nodewise_res_dem_dict.update({root.children[i].children[child].name : current_list})
            res_dem_dict.update({res:res_dict})
    log(INFO,"Resource Demand dict : " + str(res_dem_dict))
    log(INFO,"Node wise Resource Dem dict : " + str(nodewise_res_dem_dict))


# def update_delta_dict(delta_list, resource_types):
#     global delta_list_dict
#     if len(delta_list) != len(resource_types):
#         log(ERR,"Delta List and Resource Types are not of same length")
#         sys.exit(1)
#     for i in range(len(resource_types)):
#         delta_list_dict.update({resource_types[i].strip():delta_list[i]})
#     log(DEBUG,"Delta List Dict:" +str(delta_list_dict))


# Need to recalculated Delta for each node
def calculate_node_deltas(nodewise_res_dem_dict):
    global node_deltas_dict
    for node in nodewise_res_dem_dict:
        if max(nodewise_res_dem_dict.get(node)) is not None and max(nodewise_res_dem_dict.get(node)) != 0:
            node_delta = round(float(epsilon/max(nodewise_res_dem_dict.get(node))),2)
            node_deltas_dict.update({node : node_delta})
    log(INFO,"Node deltas dict :" + str(node_deltas_dict))



def get_total_demand(resource_types):
    global total_demands_dict
    for res in resource_types:
        total_demands = sum(res_dem_dict.get(res.strip()).values())
        if total_demands != 0:
            total_demands_dict.update({res.strip() : total_demands})
        else:
            log(WARN,"Total Demand for resource " + res.strip() + " is zero")
        
    log(INFO, "Total Demands Dict : " + str(total_demands_dict))


def get_demand_vector(root, resource_types):
    global parents
    global childs
    global res_dem_vect_dict
    global res_dem_dict
    child_count = 0
    for res in resource_types:
        temp_dem_vect_dict = {}
        res_dict = res_dem_dict.get(res.strip())
        log(DEBUG,"Res Dict : " + str(res_dict))
        for i in range (int(parents)):
            for child in range (int(childs[i])):
                res_dem = res_dict.get(root.children[i].children[child].name)
                if res_dem != 0 and res_dem is not None:
                    temp_dem_vect_dict.update({root.children[i].children[child].name : round(res_dem/float(total_demands_dict.get(res.strip()))*100,2)})
                child_count += 1
        res_dem_vect_dict.update({res.strip() : temp_dem_vect_dict})
    log(INFO,"Resource Demand Vector Dict : " + str(res_dem_vect_dict))


# Function to calculate the parent vectors by summing the child vectors in
# the anyTree class
def get_parent_vector(root, resource_types):
    global res_dem_vect_dict
    global res_par_vect_dict
    for res in resource_types:
        temp_par_vect_dict = {}
        res_dem_vect = res_dem_vect_dict.get(res.strip())
        # print("Res Dem Vect : ", res_dem_vect)
        for par in root.children:
            # print("Parent : ", par.name)
            tot_dem_vect = 0
            for child in par.children:
                # print("Child : ", child.name)
                if res_dem_vect.get(child.name) != 0 and res_dem_vect.get(child.name) is not None:
                    # print("Child : " + child.name + " dem vect : " + str(res_dem_vect.get(child.name)))
                    tot_dem_vect += round(res_dem_vect.get(child.name),2)
                    temp_par_vect_dict.update({par.name : round(tot_dem_vect,2)})
        res_par_vect_dict.update({res.strip() : temp_par_vect_dict})
    log(INFO,"Resource Parent Vector Dict : " + str(res_par_vect_dict)) 

# Under development
def nodes_dem_vect_update(root, resource_types):
    global nodes_dom_vect_dict
    global par_dom_vect_dict
    global allocated_res_dict
    global resource_qty_dict
    for res in resource_types:
        # print("Running for Resource : ", res)
        tot_res = resource_qty_dict.get(res.strip())
        # print("Total Resource : ", tot_res)
        temp_one_dem_vect_dict = {}
        temp_par_dom_vect_dict = {}
        one_allocated_dict = allocated_res_dict.get(res.strip())
        if one_allocated_dict is not None:
            # print("One Allocated Dict : ", one_allocated_dict)
            if tot_res != 0 and tot_res is not None:
                for par in root.children:
                    par_share_vect = 0.0
                    for child in par.children:
                        # print("Child : ", child.name)
                        if one_allocated_dict.get(child.name) != 0 and one_allocated_dict.get(child.name) is not None:
                            # print("Child : " + child.name + " dem vect : " + str(res_dem_vect.get(child.name)))
                            dom_share_vect = round(float(one_allocated_dict.get(child.name))/float(tot_res)*100,2)
                            par_share_vect += dom_share_vect
                            # print("Dom Share Vect : ", dom_share_vect)
                            temp_one_dem_vect_dict.update({child.name : round(dom_share_vect,2)})
                            temp_par_dom_vect_dict.update({par.name : round(par_share_vect,2)})

            nodes_dom_vect_dict.update({res.strip() : temp_one_dem_vect_dict})
            par_dom_vect_dict.update({res.strip() : temp_par_dom_vect_dict})
    log(INFO,"Child nodes' Dominant Shares after allocation : " + str(nodes_dom_vect_dict))
    log(INFO,"Parents' Dominant Shares After allocation : " + str(par_dom_vect_dict))
    print("\nChild nodes' Dominant Shares after allocation : " + str(nodes_dom_vect_dict))
    print("Parents' Dominant Shares After allocation : " + str(par_dom_vect_dict))

def calculate_revised_dom_share(root, resource_types):
    global par_dom_vect_dict
    global resource_qty_dict
    global revised_par_dom_share_dict
    for par in root.children:
        max_res_share = 0.0
        max_res_type = ""
        for res in resource_types:
            res_dict = par_dom_vect_dict.get(res.strip())
            # print("Res Dict : ", res_dict)
            if res_dict != 0 and res_dict is not None:
                par_share = res_dict.get(par.name)
                # print("Parent : ", par.name, " Resource : ", res, " Share : ", par_share)
                if par_share != 0 and par_share is not None:
                    if  par_share > max_res_share:
                        max_res_share = par_share
                        max_res_type = res.strip()
        # print("Max Res Share : ", max_res_share)
        revised_par_dom_share_dict.update({par.name : round(max_res_share,2)})
    log(INFO, "Parents' updated Dominant Resource Share : " + str(revised_par_dom_share_dict))
    print("\nParents' updated Dominant Resource Share : \n" + str(revised_par_dom_share_dict))
            
    
def update_dom_resource_list(resource_types):
    global res_dem_dict
    global resource_qty_dict
    global total_demands_dict

    for i in range(len(resource_types)):
        tot_res_dem = total_demands_dict.get(resource_types[i].strip())
        if tot_res_dem != 0 and tot_res_dem is not None:
            tot_res_dem = float(tot_res_dem)
            total_demands_dict.update({resource_types[i].strip() : round(tot_res_dem/float(resource_qty_list[i]),2)})
    log(INFO,"Dominant Resource Dict : " + str(total_demands_dict))
  

def update_res_alloc_order():
    global res_alloc_order
    res_alloc_order = sorted(total_demands_dict, key=total_demands_dict.get, reverse=True)
    print("Resource allocation order: " + str(res_alloc_order))

def update_resource_qty_dict():
    global resource_qty_dict
    global resource_qty_list
    global resource_types
    for i in range (len(resource_types)):
        resource_qty_dict.update({resource_types[i].strip() : int(resource_qty_list[i])})
    # print("Resource qty list: " + str(resource_qty_list))

def allocate_resource(root, resource, total_resource):
    # print("Allocating resource: " + resource,end="")
    # log(INFO, "Allocating resource: " + resource)
    
    resource_allocated = 0
    global allocated_res_dict
    global node_deltas_dict
    global parents
    global childs
    allocated_dict = {}
    if root and total_resource is not None:
        res_break = 0
        while res_break == 0:
            for parent in root.children:
                for child in parent.children:
                    if isLeafNode(child):
                        temp_dict = res_dem_dict.get(resource)
                        log(DEBUG, "Temp dict for allocation : " + str(temp_dict))
                        if temp_dict.get(child.name) is not None and  float(temp_dict.get(child.name)) > 0:
                            # ress = res_dem_dict.get(resource)
                            # resource_to_allocate = float(ress.get(child.name))*float(deltas_dict.get(resource))
                            resource_to_allocate = round(temp_dict.get(child.name),2) # added for modified algorithm
                            log(DEBUG,"Resource to allocate: " + str(resource_to_allocate))
                            log(DEBUG, "Trying to Allocate " + str(resource_to_allocate) + " " + resource + " to " + child.name)
                            if resource_to_allocate <= round((float(total_resource) - float(resource_allocated)),2):
                                if allocated_dict.get(child.name) is not None: 
                                    allocated_dict.update({child.name : round(float(allocated_dict.get(child.name)) + float(resource_to_allocate),2)})
                                    resource_allocated += resource_to_allocate
                                else:
                                    allocated_dict.update({child.name : round(float(resource_to_allocate),2)})
                                    resource_allocated += (resource_to_allocate)
                                log(DEBUG, "Allocated " + resource + " to " + child.name + " = " + str(resource_allocated))
                            else:
                                resource_remining = float(total_resource) - float(resource_allocated)
                                log(DEBUG, "Not enough : " + resource + " remaining for further alocation.")
                                res_break = 1
                                break                
        log(DEBUG,"Allocated incremental dict: " + str(allocated_dict))
        allocated_res_dict.update({resource : allocated_dict})
    # print("....done")


# Log helper function
def log(level, message):
    logging.log(level, message)

# # Write to config file
# def update_config_file():
#     with open('hdrf_config.conf', 'w') as configFile:
#         config.write(configFile)

# All dicts used in the program

res_dem_dict = {}
nodewise_res_dem_dict = {}
res_share_dict = {}
res_dem_vect_dict = {}
res_par_vect_dict = {}
nodes_dom_vect_dict = {}
par_dom_vect_dict = {}
revised_par_dom_share_dict = {}


# deltas_dict = {}
# node_deltas_dict = {}
# delta_list_dict = {}
dom_resource_dict = {}
resource_qty_dict = {}
allocated_res_dict = {}
total_demands_dict = {}

# All lists used in the program
res_alloc_order = []
childs = []
resource_types = []
demand_list = []
resource_qty_list = []
delta_list = []

# All global variables used in the program
parents = 0
childs = 0
epsilon = 0.0



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
    global epsilon
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
           sys.exit()

        ###
        # delta_list =  parse_config_vector(config.get("RESOURCES", "delta"))
        # print("Delta: \t\t" + ' '.join(delta_list))
        # if(len(resource_types) != len(delta_list)):
        #    print("Number of resurces and list of deltas do not match")
        #    sys.exit()
        
        epsilon = float(config.get("RESOURCES", "epsilon"))
        if epsilon is None:
            epsilon = 100.0
        
        # else:
        #     print("Delta List : ",delta_list)

        ###
        demand_list = []
        all_demand_list =  (config.get("RESOURCES", "demand")).split('&')
        if(total_children != len(all_demand_list)):
           print("Number of nodes and list of demands do not match:", total_children, ',', len(all_demand_list))
           sys.exit()
        else:
            for mylist in all_demand_list:
                # print("Mylist type = " + str(type(mylist)))
                demand_list.append(list(mylist.split(",")))
        # print(demand_list)
    except Exception as e:
        print("Error (" + type(e).__name__ + ") with config file: " + str(e))
        sys.exit()


# Main Function
config = configparser.ConfigParser()
if (len(sys.argv) != 2):
     print("Usage: python3 hdrf.py <config-file>")
     sys.exit()

# Logger initialization
init_logger(sys.argv[1])

# Get the config file name from the command line and parse it
init_from_config(sys.argv[1])

# Create the organization of the nodes
build_tree(parents,childs)

# Update resource delta in a new dict
# update_delta_dict(delta_list, resource_types)

# Update resource demand in a new dict
assign_resource_share(root, resource_types)

# Calculate individual resource deltas and save in a new dict
# calculate_deltas(resource_types)
# calculate_node_deltas(nodewise_res_dem_dict)

# Calculate the total demand for each resource
get_total_demand(resource_types)

# Calculate the demand vectors for each resource
get_demand_vector(root, resource_types)

# Update the parent's demand vectors for each resource
get_parent_vector(root, resource_types)

# Calculate the dominant resource for each node
update_dom_resource_list(resource_types)

# Calculate the resource allocation order from dominant resources
update_res_alloc_order()

# Update resources quantity dict for use in allocation
update_resource_qty_dict()

# log(INFO, "Resource quantity list: " + str(resource_qty_list))
log(INFO, "Resource quantity dict: " + str(resource_qty_dict))
log(INFO, "Resource allocation order: " + str(res_alloc_order))

# Allocate resources one by one until exhaustion
for resource in res_alloc_order:
    total_resource = resource_qty_dict.get(str(resource.strip()))
    log(INFO, "Total " + resource + " available: " + str(total_resource))
    allocate_resource(root, resource.strip(), total_resource)
log(INFO, "Final allocation : " + str(allocated_res_dict))
print("\nFinal allocation : ",allocated_res_dict)

# Update individual child nodes' dominant share vector
nodes_dem_vect_update(root, resource_types)

# log(INFO,"Allocated dict: " + str(allocated_res_dict))
# print("Allocated dict: " + str(allocated_res_dict))

# Calculated revised parent's dominant share vector after primary allocation
calculate_revised_dom_share(root, resource_types)

log(INFO, "Total run time is %s seconds!" % (time.time() - start_time))
sys.exit()

