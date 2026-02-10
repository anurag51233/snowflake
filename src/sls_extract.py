from lib.Config import Config
from lib.Logger import Logger
from lib.Variable import Variables

v = Variables()
v.set("SCRIPT_NAME", "SLS_EXTRACT")
v.set("LOG", Logger(v))
v.set("LND_TABLE", "SALES")
sf = Config(v)

# Truncate the landing table
truncate_query = f"TRUNCATE TABLE {v.get('LND_SCHEMA')}.{v.get('LND_TABLE')}"
sf.execute_query(truncate_query)

# Copy stage file(s3/storage) to landing table
cpy_query = f"""
            COPY INTO {v.get('LND_SCHEMA')}.{v.get('LND_TABLE')}
            FROM @{v.get('LND_SCHEMA')}.{v.get('FILE_STAGE')}
            FILE_FORMAT = (
              TYPE = 'CSV'
              FIELD_DELIMITER = ','
              SKIP_HEADER = 1
              FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            )
            ON_ERROR = 'ABORT_STATEMENT';
            """
sf.execute_query(cpy_query)

v.get('LOG').close()