import configparser
import logging
# from logging import log
import pickle

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

"""Tree Node Class"""
class Tree:
    def __init__(self, name, dem_cpu, dem_lte, dom_vect):
        self.children = []
        self.name = name
        self.dem_cpu = dem_cpu
        self.dem_lte = dem_lte
        self.dom_vect = dom_vect
    
    def inorderTraversal(self, root):
        res = []
        if root:
            if root.children[0] is not None:
                res = self.inorderTraversal(root.children[0])
                res.append(root.name)
            if root.children[1] is not None:
                res = res + self.inorderTraversal(root.children[1])
        print(res)
        return res

# left = Tree("left")
# middle = Tree("middle")
# right = Tree("right")
# root = Tree("root")
# root.children = [left, middle, right]

leaf_nodes = ["epc", "vs", "dl", "mstorm"]

N = Tree("N", 0, 0, 0)
N.children = [Tree("N1", 0, 0, 0), Tree("N2", 0, 0, 0), None]
N.children[0].children = [Tree("N11", n11_cpu_dem, n11_lte_dem, 0), None, None]
N.children[1].children = [Tree("N21", n21_cpu_dem, n21_lte_dem, 0), Tree("N22", n22_cpu_dem, n22_lte_dem, 0), None]


# dummy = N.children[1].children[0]
# print(dummy.name + " " + str(dummy.demand) + " " + str(dummy.alloc))


share_dem.update({"epc": {"cpu": 0, "mem": 0, "lte": 0}})
share_dem.update({"vs": {"cpu": 0, "mem": 0, "lte": 0}})
share_dem.update({"dl": {"cpu": 0, "mem": 0, "lte": 0}})

resource_left.update({"cpu": 1000})
resource_left.update({"mem": 1000})
resource_left.update({"lte": 80})


"""Log helper function"""
def log(level, message):
    logging.log(level, message)

"""Write to config file"""
def update_config_file():
    with open('hdrf_config.conf', 'w') as configFile:
        config.write(configFile)


"""Initialize config file & parser"""
# config = configparser.ConfigParser()
# config.read('hdrf_config.conf')

"""Read config file"""
# r_cpu = config.get("TOTALRES", "cpu")
# r_mem = config.get("TOTALRES", "mem")

"""Write to config file"""
# config.set("AMRAN", "CarMake", "Honda")
# config.set("AMRAN", "CarModel", "Odyssey")
# update_config_file()


parent_dict = {}
parent_list = []


"""Main Algorithm"""
# try:
config = configparser.ConfigParser()
config.read('hdrf_config.conf')

"""Logger configuration"""
logLevel = config.get("LOGGING", "level")
logFile = config.get("LOGGING", "filename")
logging.basicConfig(filename=logFile, filemode='a+', format='%(asctime)s | %(levelname)s : %(message)s', level=DEBUG)
log(INFO, "************************************")

t_cpu = int(config.get("TOTALRES", "cpu"))
t_mem = int(config.get("TOTALRES", "mem"))
t_lte = int(config.get("TOTALRES", "lte"))
c_rcpu = 0
c_rmem = 0
c_rlte = 0

cur_node = N
lowest_node = None


print(N.inorderTraversal(N))
"""
while cur_node.children != None:
    for child in cur_node.children:
        if child != None:
            parent_list.append(child)
    lowest_node = parent_list[0]
    for node in parent_list:
        if node.dem_cpu < lowest_node.dem_cpu:
            lowest_node = node
    parent_list = []
    cur_node = lowest_node


while int(t_cpu) > 0 or t_lte > 0:
    while cur_node.children != None:
        print(cur_node.name)
        parent_list.append(cur_node)
    print("Parent List: " + parent_list)


        # for child in cur_node.children:
p_value = config.get("LOGGING", "level")
print(p_value)
c_value = config.get("LOGGING", "filename")
print(c_value)
d_value = config.get("LOGGING", "filemode")
print(d_value)

"""
# except Exception as e:
#     print("Exception raised: ", e)

