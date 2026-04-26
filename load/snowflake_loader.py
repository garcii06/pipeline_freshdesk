import os
import json
import snowflake.connector
from dotenv import load_dotenv
from utils.logger import get_logger
from datetime import datetime, timezone

if os.path.exists('.env'):
    load_dotenv()

logger = get_logger(__name__)

class SnowflakeLoader:
    def __init__(self):
        self.con = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_PIPELINE_USER'),
            password=os.getenv('SNOWFLAKE_PIPELINE_PASSWORD'),
            role=os.getenv('SNOWFLAKE_ROLE'),
        )

        self.con.cursor().execute("USE ROLE freshdesk_pipeline_role;")
        self.con.cursor().execute("USE WAREHOUSE freshdesk_wh;")
        self.con.cursor().execute("USE DATABASE freshdesk_raw;")

    def get_watermark(self, source):
        last_load = self.con.cursor().execute(
            "SELECT last_loaded " 
            "FROM freshdesk_raw.raw._pipeline_watermarks "
            "WHERE source = %s", (source,)
        ).fetchone()
        return last_load

    def set_watermark(self, source, timestamp):
        self.con.cursor().execute(
            "MERGE INTO freshdesk_raw.raw._pipeline_watermarks AS target "
            "USING (SELECT %s AS source, %s AS last_loaded) AS source_data "
            "ON target.source = source_data.source "
            "WHEN MATCHED THEN UPDATE SET last_loaded = source_data.last_loaded "
            "WHEN NOT MATCHED THEN INSERT (source, last_loaded) "
            "VALUES (source_data.source, source_data.last_loaded)",
            (source, timestamp)
        )

    def insert_records(self, table_name, records, source):
        batch_id = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        cur = self.con.cursor()
        for record in records:
            cur.execute(
                f"INSERT INTO freshdesk_raw.raw.{table_name} "
                f"SELECT PARSE_JSON(%s), %s, %s, %s",
                (json.dumps(record), datetime.now(timezone.utc), source, batch_id)
            )
    
    def close(self):
        self.con.close()