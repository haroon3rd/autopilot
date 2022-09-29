import configparser
import logging
import sys
from collections import deque
import re

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
    print("Organizational Structure : ",Preorder)


def assign_resource_share2(root,resource_types):
    global parents
    global childs
    global demand_list
    global res_dem_dict
    print("Demand List : ", demand_list)
    for r in range(len(resource_types)):
        res = resource_types[r].strip()
        child_count = 0
        res_dict = {}
        for i in range (int(parents)):
            for child in range (int(childs[i])):
                current_list = demand_list[child_count]
                # print("Current_list : ", current_list)
                item = current_list[r]
                # print ("Item : ", item.strip())
                if int(item.strip()) !=0:
                    res_dict.update({root.children[i].children[child].name : int(item)})
                child_count += 1
                # print("Res Dict : ", res_dict)
            res_dem_dict.update({res:res_dict})
    log(INFO,"Resource Dem dict : " + str(res_dem_dict))


def update_delta_dict(delta_list, resource_types):
    global delta_list_dict
    if len(delta_list) != len(resource_types):
        log(ERR,"Delta List and Resource Types are not of same length")
        sys.exit(1)
    for i in range(len(resource_types)):
        delta_list_dict.update({resource_types[i].strip():delta_list[i]})
    log(DEBUG,"Delta List Dict:" +str(delta_list_dict))


def calculate_deltas2(resource_types):
    global res_dem_dict
    for res in resource_types:
        demand_dict = res_dem_dict.get(res.strip()) 
        res_alloc_delta = float(delta_list_dict.get(res.strip()))/float(min(demand_dict.values()))
        deltas.update({res.strip() : res_alloc_delta})
        log(INFO,res.strip().upper() + " Allocation Delta: " + str(res_alloc_delta))
    log(INFO,"Resource allocation deltas :" + str(deltas))


def get_total_demand2(resource_types):
    global total_demands_dict
    for res in resource_types:
        total_demands = sum(res_dem_dict.get(res.strip()).values())
        total_demands_dict.update({res.strip() : total_demands})
    log(INFO, "Total Demands Dict : " + str(total_demands_dict))


def get_demand_vector2(root, resource_types):
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
                    temp_dem_vect_dict.update({root.children[i].children[child].name : res_dem/float(total_demands_dict.get(res.strip()))*100})
                child_count += 1
        res_dem_vect_dict.update({res.strip() : temp_dem_vect_dict})
    log(INFO,"Resource Demand Vector Dict : " + str(res_dem_vect_dict))


# Will fix it later
###############################################
# def update_parent_vectors(root, resource):
#     global parents
#     global childs
#     if root:
#         for parent in root.children:
#             for child in parent.children:
#                 if isLeafNode(child):
#                     if resource == "cpu":
#                         parent.cpu_dem_vect += float(child.cpu_dem_vect)
#                     elif resource == "mem":
#                         parent.mem_dem_vect += float(child.mem_dem_vect)
#                     elif resource == "bw":
#                         parent.lte_dem_vect += float(child.lte_dem_vect)
                # update_parent_vectors(child, resource)

# Will fix it later
###############################################
# def update_parent_vector_dict(root, resource):
#     global parents
#     global childs
#     if root:
#         for i in range (int(parents)):
#             for child in root.children:
#                 if resource == "cpu":
#                     cpu_dem_vect_dict.update({root.name : root.cpu_dem_vect})
#                 elif resource == "mem":
#                     mem_dem_vect_dict.update({root.name : root.mem_dem_vect})
#                 elif resource == "bw":
#                     lte_dem_vect_dict.update({root.name : root.lte_dem_vect})
                # update_parent_vector_dict(child, resource)
    

def update_dom_resource_list2(resource_types):
    global res_dem_dict
    global resource_qty_dict
    global dom_resource_dict2

    for i in range(len(resource_types)):
        tot_res_dem = float(total_demands_dict.get(resource_types[i].strip()))
        dom_resource_dict2.update({resource_types[i].strip() : tot_res_dem/float(resource_qty_list[i])})
    log(INFO,"Dominant Resource Dict : " + str(dom_resource_dict2))
  


def update_res_alloc_order():
    global res_alloc_order
    res_alloc_order = sorted(dom_resource_dict2, key=dom_resource_dict2.get, reverse=True)
    print("Resource allocation order: " + str(res_alloc_order))

def update_resource_qty_dict():
    global resource_qty_dict
    global resource_qty_list
    global resource_types
    for i in range (len(resource_types)):
        resource_qty_dict.update({resource_types[i].strip() : resource_qty_list[i]})
    # print("Resource qty list: " + str(resource_qty_list))

def allocate_resource2(root, resource, total_resource):
    print("Allocating resource: " + resource,end="")
    log(INFO, "Allocating resource: " + resource)
    resource_remining = 0 
    resource_allocated = 0
    global allocated_res_dict
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
                            ress = res_dem_dict.get(resource)
                            resource_to_allocate = float(ress.get(child.name))*float(deltas.get(resource))
                            log(DEBUG,"Resource to allocate: " + str(resource_to_allocate))
                            log(DEBUG, "Trying to Allocate " + str(resource_to_allocate) + " " + resource + " to " + child.name)
                            if resource_to_allocate <= float(total_resource) - float(resource_allocated):
                                if allocated_dict.get(child.name) is not None: 
                                    allocated_dict.update({child.name : float(allocated_dict.get(child.name)) + float(resource_to_allocate)})
                                # new_allocation = float(allocated_dict.get(child.name)) + resource_to_allocate
                                # allocated_dict.update({child.name: new_allocation})
                                    resource_allocated += resource_to_allocate
                                else:
                                    allocated_dict.update({child.name : float(resource_to_allocate)})
                                    resource_allocated += resource_to_allocate
                                log(INFO, "Allocated " + resource + " to " + child.name + " = " + str(resource_allocated))
                            else:
                                resource_remining = float(total_resource) - float(resource_allocated)
                                log(INFO, "Not enough : " + resource + " remaining for further alocation.")
                                res_break = 1
                                break                
        log(DEBUG,"Allocated dict: " + str(allocated_dict))
        allocated_res_dict.update({resource : allocated_dict})
    print("....done")
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

res_dem_dict = {}
res_share_dict = {}
res_dem_vect_dict = {}


deltas = {}
delta_list_dict = {}
dom_resource_dict = {}
dom_resource_dict2 = {}
resource_qty_dict = {}
allocated_res_dict = {}

# All lists used in the program
res_alloc_order = []
childs = []
resource_types = []
demand_list = []
resource_qty_list = []
delta_list = []

# All global variables used in the program
parents = 0
total_demands_dict = {}
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
           sys.exit()

        ###
        delta_list =  parse_config_vector(config.get("RESOURCES", "delta"))
        print("Delta: \t\t" + ' '.join(delta_list))
        if(len(resource_types) != len(delta_list)):
           print("Number of resurces and list of deltas do not match")
           sys.exit()
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
                demand_list.append(list(mylist.split(",")))
        # print(demand_list)
        

           
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
    update_delta_dict(delta_list, resource_types)
    assign_resource_share2(root, resource_types)
    calculate_deltas2(resource_types)
    get_total_demand2(resource_types)
    get_demand_vector2(root, resource_types)
    update_dom_resource_list2(resource_types)
    update_res_alloc_order()
    update_resource_qty_dict()
    
    # log(INFO, "Resource quantity list: " + str(resource_qty_list))
    log(INFO, "Resource quantity dict: " + str(resource_qty_dict))
    log(INFO, "Resource allocation order: " + str(res_alloc_order))

    for resource in res_alloc_order:
        # log(INFO, "Allocating " + resource + " to nodes")
        # log(INFO, "Resource quantity dict: " + str(resource_qty_dict))
        total_resource = resource_qty_dict.get(str(resource.strip()))
        log(INFO, "Total " + resource + " available: " + str(total_resource))
        allocate_resource2(root, resource.strip(), total_resource)
        # allocate_resource(root, resource.strip(), total_resource)
    # print("Deltas : ",deltas)
    print("Final allocation :\n",allocated_res_dict)

sys.exit()

