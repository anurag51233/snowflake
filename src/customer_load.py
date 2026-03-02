from lib.Config import Config
from lib.Logger import Logger
from lib.Variable import Variables

v = Variables()
v.set("SCRIPT_NAME", "CUSTOMER_LOAD")
v.set("LOG", Logger(v))
v.set("STG_VIEW", "STG_D_CUSTOMER")
v.set("TMP_TABLE", "TMP_D_CUSTOMER")
v.set("TGT_TABLE", "TGT_D_CUSTOMER")
sf = Config(v)

# Truncate the temporary table
truncate_query = f"TRUNCATE TABLE {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}"
sf.execute_query(truncate_query)

# Load to temporary table with HASH_KEY for change detection
temp_query = f"""
                INSERT INTO {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}
                (CUSTOMER_ID, CUSTOMER_NAME, SEGMENT, HASH_KEY)
                SELECT DISTINCT CUSTOMER_ID
                ,CUSTOMER_NAME
                ,SEGMENT
                ,MD5(COALESCE(CUSTOMER_NAME, '') || '~' || COALESCE(SEGMENT, ''))
                FROM {v.get('STG_SCHEMA')}.{v.get('STG_VIEW')}
            """
sf.execute_query(temp_query)

# SCD2 Step 1: Expire changed rows (set EFF_END_DATE and IS_CURRENT = FALSE)
expire_query = f"""
                UPDATE {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')} AS TGT
                SET TGT.EFF_END_DATE = CURRENT_DATE(),
                    TGT.IS_CURRENT = FALSE
                WHERE TGT.IS_CURRENT = TRUE
                AND EXISTS (
                    SELECT 1 FROM {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')} TMP
                    WHERE TMP.CUSTOMER_ID = TGT.CUSTOMER_ID
                    AND TMP.HASH_KEY != TGT.HASH_KEY
                );
            """
sf.execute_query(expire_query)

# SCD2 Step 2: Insert new rows and changed rows as new versions
insert_query = f"""
                INSERT INTO {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')}
                (CUSTOMER_ID, CUSTOMER_NAME, SEGMENT, HASH_KEY, EFF_START_DATE, EFF_END_DATE, IS_CURRENT)
                SELECT TMP.CUSTOMER_ID
                ,TMP.CUSTOMER_NAME
                ,TMP.SEGMENT
                ,TMP.HASH_KEY
                ,CURRENT_DATE()
                ,NULL
                ,TRUE
                FROM {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')} TMP
                WHERE NOT EXISTS (
                    SELECT 1 FROM {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')} TGT
                    WHERE TGT.CUSTOMER_ID = TMP.CUSTOMER_ID
                    AND TGT.IS_CURRENT = TRUE
                );
            """
sf.execute_query(insert_query)

v.get('LOG').close()