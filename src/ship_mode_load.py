from lib.Config import Config
from lib.Logger import Logger
from lib.Variable import Variables

v = Variables()
v.set("SCRIPT_NAME", "SHIP_MODE_LOAD")
v.set("LOG", Logger(v))
v.set("STG_VIEW", "STG_D_SHIP_MODE")
v.set("TMP_TABLE", "TMP_D_SHIP_MODE")
v.set("TGT_TABLE", "TGT_D_SHIP_MODE")
sf = Config(v)

# Truncate the temporary table
truncate_query = f"TRUNCATE TABLE {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}"
sf.execute_query(truncate_query)

# Load to temporary table with HASH_KEY for change detection
temp_query = f"""
                INSERT INTO {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}
                (SHIP_MODE, HASH_KEY)
                SELECT DISTINCT SHIP_MODE
                ,MD5(COALESCE(SHIP_MODE, ''))
                FROM {v.get('STG_SCHEMA')}.{v.get('STG_VIEW')}
            """
sf.execute_query(temp_query)

# SCD2 Step 1: Expire changed rows (set EFF_END_DATE and IS_CURRENT = FALSE)
# Note: Since SHIP_MODE is the only attribute and also the business key,
# this step will rarely trigger — only if a ship mode value itself changes.
expire_query = f"""
                UPDATE {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')} AS TGT
                SET TGT.EFF_END_DATE = CURRENT_DATE(),
                    TGT.IS_CURRENT = FALSE
                WHERE TGT.IS_CURRENT = TRUE
                AND EXISTS (
                    SELECT 1 FROM {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')} TMP
                    WHERE TMP.SHIP_MODE = TGT.SHIP_MODE
                    AND TMP.HASH_KEY != TGT.HASH_KEY
                );
            """
sf.execute_query(expire_query)

# SCD2 Step 2: Insert new rows as new versions
insert_query = f"""
                INSERT INTO {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')}
                (SHIP_MODE, HASH_KEY, EFF_START_DATE, EFF_END_DATE, IS_CURRENT)
                SELECT TMP.SHIP_MODE
                ,TMP.HASH_KEY
                ,CURRENT_DATE()
                ,NULL
                ,TRUE
                FROM {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')} TMP
                WHERE NOT EXISTS (
                    SELECT 1 FROM {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')} TGT
                    WHERE TGT.SHIP_MODE = TMP.SHIP_MODE
                    AND TGT.IS_CURRENT = TRUE
                );
            """
sf.execute_query(insert_query)

v.get('LOG').close()