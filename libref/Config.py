import snowflake.connector
from lib.Logger import Logger
from lib.Variable import Variables


class Config:

    def __init__(self):
        self.v = Variables()
        self.v.get("USER")
        self.USER = self.v.get("USER")  ##or constants.USER
        self.PASSWORD = self.v.get("PASSWORD")  ##or constants.PASSWORD
        self.ACCOUNT = self.v.get("ACCOUNT")  ##or constants.ACCOUNT
        self.DATABASE = self.v.get("DATABASE")  ##or constants.DATABASE
        self.DATA_WAREHOUSE = self.v.get("WAREHOUSE")
        ctx = snowflake.connector.connect(
            user=self.USER,
            password=self.PASSWORD,
            account=self.ACCOUNT,
            database=self.DATABASE,
            warehouse=self.DATA_WAREHOUSE,
        )
        self.cs = ctx.cursor()


    def execute_query(self, query):
        try:
            self.cs.execute(query)
            print(self.cs.fetchall())
            # Logger.log_message(f"query executed: {query}")
        except Exception as e:
            print(e, query)
            Logger.log_message(f"query error: {query}")
            Logger.log_message(e)
        # finally:
        #     cs.close()
        # ctx.close()

    def executemany(self, query, params):
        try:
            self.cs.executemany(query, params)
            # print(cs.fetchall())
            Logger.log_message(f"query executed: {query}")
        except Exception as e:
            print(e, query)
            Logger.log_message(f"query error: {query}")
            Logger.log_message(e)
        # finally:
        #     cs.close()
        # ctx.close()


    def fetch_data(self, query):
        try:
            self.cs.execute(query)
            Logger.log_message(f"query executed: {query}")
            return self.cs.fetchall()
        except Exception as e:
            print(e, query)
            Logger.log_message(f"query error: {query}")
            Logger.log_message(e)