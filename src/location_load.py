from lib.Config import Config
from lib.Logger import Logger
from lib.Variable import Variables

v = Variables()
v.set("SCRIPT_NAME", "LOCATION_LOAD")
v.set("LOG", Logger(v))
v.set("STG_VIEW", "STG_D_LOCATION")
v.set("TMP_TABLE", "TMP_D_LOCATION")
v.set("TGT_TABLE", "TGT_D_LOCATION")
sf = Config(v)

# Truncate the temporary table
truncate_query = f"TRUNCATE TABLE {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}"
sf.execute_query(truncate_query)

# Load to temporary table with HASH_KEY for change detection
temp_query = f"""
                INSERT INTO {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')}
                (COUNTRY, REGION, STATE, CITY, POSTAL_CODE, HASH_KEY)
                SELECT DISTINCT COUNTRY
                ,REGION
                ,STATE
                ,CITY
                ,POSTAL_CODE
                ,MD5(COALESCE(COUNTRY, '') || '~' || COALESCE(REGION, '') || '~' || COALESCE(STATE, '') || '~' || COALESCE(CITY, ''))
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
                    WHERE TMP.POSTAL_CODE = TGT.POSTAL_CODE
                    AND TMP.HASH_KEY != TGT.HASH_KEY
                );
            """
sf.execute_query(expire_query)

# SCD2 Step 2: Insert new rows and changed rows as new versions
insert_query = f"""
                INSERT INTO {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')}
                (COUNTRY, REGION, STATE, CITY, POSTAL_CODE, HASH_KEY, EFF_START_DATE, EFF_END_DATE, IS_CURRENT)
                SELECT TMP.COUNTRY
                ,TMP.REGION
                ,TMP.STATE
                ,TMP.CITY
                ,TMP.POSTAL_CODE
                ,TMP.HASH_KEY
                ,CURRENT_DATE()
                ,NULL
                ,TRUE
                FROM {v.get('TMP_SCHEMA')}.{v.get('TMP_TABLE')} TMP
                WHERE NOT EXISTS (
                    SELECT 1 FROM {v.get('TGT_SCHEMA')}.{v.get('TGT_TABLE')} TGT
                    WHERE TGT.POSTAL_CODE = TMP.POSTAL_CODE
                    AND TGT.IS_CURRENT = TRUE
                );
            """
sf.execute_query(insert_query)

v.get('LOG').close()