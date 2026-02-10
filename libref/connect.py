##import constants

import snowflake.connector
import json
import logging
from lib.Variable import Variables
from lib.Logger import Logger
v=Variables()

v.get("USER")
USER = v.get("USER") ##or constants.USER
PASSWORD = v.get("PASSWORD") ##or constants.PASSWORD
ACCOUNT = v.get("ACCOUNT")    ##or constants.ACCOUNT
DATABASE =  v.get("DATABASE")   ##or constants.DATABASE
SCHEMA = v.get("SCHEMA") ##or constants.SCHEMA
DATA_WAREHOUSE= v.get("DATA_WAREHOUSE")


ctx = snowflake.connector.connect(
    user= USER,
    password=PASSWORD,
    account=ACCOUNT,
    database=DATABASE,
    schema=SCHEMA
    )

cs = ctx.cursor()



def execute_query(query):
    try:
        cs.execute(f"USE WAREHOUSE {DATA_WAREHOUSE}")
        cs.execute(query)
        print(cs.fetchall())
        Logger.log_message(f"query executed: {query}")
    except Exception as e:
        print(e, query)
        Logger.log_message(f"query error: {query}")
        Logger.log_message(e)
    # finally:
    #     cs.close()
    # ctx.close()

def executemany(query, params):
    try:
        cs.execute(f"USE WAREHOUSE {DATA_WAREHOUSE}")
        cs.executemany(query, params)
        # print(cs.fetchall())
        Logger.log_message(f"query executed: {query}")
    except Exception as e:
        print(e, query)
        Logger.log_message(f"query error: {query}")
        Logger.log_message(e)
    # finally:
    #     cs.close()
    # ctx.close()


def fetch_data(query):
    try:
        cs.execute(f"USE WAREHOUSE {DATA_WAREHOUSE}")
        cs.execute(query)
        Logger.log_message(f"query executed: {query}")
        return cs.fetchall()
    except Exception as e:
        print(e, query)
        Logger.log_message(f"query error: {query}")
        Logger.log_message(e)
