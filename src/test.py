from lib.Config import Config

config = Config()

#test query execution 
config.execute_query("SELECT * from IOE.LANDING.SALES")
