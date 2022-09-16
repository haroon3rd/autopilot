import configparser
import logging
# from logging import log
import pickle

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERR = logging.ERROR
CRIT = logging.CRITICAL

parent_dict = {}
share_dem = {}
resource_left = {}
parent = []
cur_node = None

"""Tree Node Class"""
class Tree:
    def __init__(self, name, dom_s, alloc):
        self.children = []
        self.name = name
        self.dom_s = dom_s
        self.alloc = alloc

# left = Tree("left")
# middle = Tree("middle")
# right = Tree("right")
# root = Tree("root")
# root.children = [left, middle, right]

leaf_nodes = ["epc", "vs", "dl", "mstorm"]

N = Tree("N", 0, 0)
N.children = [Tree("N1", 0, 0), Tree("N2", 0, 0), None]
N.children[0].children = [Tree("N11", 0, 0), None, None]
N.children[1].children = [Tree("N21", 0, 0), Tree("N22", 0, 0), Tree("N23", 0, 0)]


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


"""Main Algorithm"""
# try:
config = configparser.ConfigParser()
config.read('hdrf_config.conf')

"""Logger configuration"""
logLevel = config.get("LOGGING", "level")
logFile = config.get("LOGGING", "filename")
logging.basicConfig(filename=logFile, filemode='a+', format='%(asctime)s | %(levelname)s : %(message)s', level=DEBUG)
log(INFO, "************************************")

r_cpu = config.get("TOTALRES", "cpu")
r_mem = config.get("TOTALRES", "mem")
r_lte = config.get("TOTALRES", "lte")
c_rcpu = 0
c_rmem = 0
c_rlte = 0

cur_node = N

while int(r_cpu) > 0:
    while cur_node.children != None:
        print(cur_node.name)
        parent.append(cur_node)
p_value = config.get("LOGGING", "level")
print(p_value)
c_value = config.get("LOGGING", "filename")
print(c_value)
d_value = config.get("LOGGING", "filemode")
print(d_value)


# except Exception as e:
#     print("Exception raised: ", e)

