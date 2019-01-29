import time
import sys
import csv

""" ################ """
""" general settings """
""" ################ """

# Windows Home
sys.path.insert(0, "C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/RasPi/SmartHome/led/")
PATH = 'C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/RasPi/SmartHome/led/programs/'

# Windows Work
#sys.path.insert(0, "C:/Users/mstan/GIT/Python_Projects/RasPi/SmartHome/led")
#PATH = 'C:/Users/mstan/GIT/Python_Projects/RasPi/SmartHome/led/programs/'

# RasPi:
#sys.path.insert(0, "/home/pi/Python/SmartHome/led")
#PATH = '/home/pi/Python/SmartHome/led/programs/'

from LED_control import CONNECT_BRIDGE


""" ############ """
""" CSV settings """
""" ############ """

def NEW_CSV(name):
    csv_name = PATH + name + ".csv"
    with open(csv_name, 'w') as newFile:
        newFile.close()
