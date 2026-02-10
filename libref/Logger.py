from lib.Variable import Variables
import datetime
from os import path

v=Variables()
v.set("SCRIPT_NAME","Nightly_Batch")

class Logger:
    def log_initialize():
        log_path = v.get("LOG_PATH")
        script_name = v.get("SCRIPT_NAME")
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_name = str(script_name) + "_" + current_time + ".log"
        log_file = path.join(log_path, log_file_name)
        log_file = open(log_file, 'w')
        v.set("LOG_FILE", log_file_name)
        v.set("LOG_PATH", log_file)
        v.set("LOG_CUR_DATETIME", current_time)

    def log_message(msg):
        now = datetime.datetime.now()
        log_file=v.get("LOG_PATH")
        msg = msg
        # print(msg)
        log_file.write(str(now))
        log_file.write(": ")
        log_file.write(msg)
        log_file.write("\n")
        log_file.flush()

    def close():
        log_file = v.get("LOG_PATH")
        log_file.close()