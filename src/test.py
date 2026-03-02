from lib.Config import Config
from lib.Variable import Variables
from lib.Logger import Logger

v = Variables()
v.set("SCRIPT_NAME", "TEST")
v.set("LOG", Logger(v))
config = Config(v)

#test query execution 

config.execute_query("SELECT * from IOEE.LANDING.SALES")
