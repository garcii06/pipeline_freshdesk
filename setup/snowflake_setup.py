import os
import snowflake.connector
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

def connect_as_admin():
    con = snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_ADMIN_USER'),
        password=os.getenv('SNOWFLAKE_ADMIN_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ADMIN_ROLE'),
    )

    return con

def connect_as_user():
    con = snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_PIPELINE_USER'),
        password=os.getenv('SNOWFLAKE_PIPELINE_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ROLE'),
    )

    return con   

def create_infrastructure(con):
    cur = con.cursor()
    cur.execute("CREATE WAREHOUSE IF NOT EXISTS freshdesk_wh " \
    "WAREHOUSE_SIZE='X-SMALL' " \
    "AUTO_SUSPEND = 60 " \
    "AUTO_RESUME = TRUE;")
    cur.execute("CREATE DATABASE IF NOT EXISTS freshdesk_raw;")
    cur.execute("CREATE SCHEMA IF NOT EXISTS freshdesk_raw.raw;")
    cur.execute("CREATE SCHEMA IF NOT EXISTS freshdesk_raw.bronze;")
    cur.execute("CREATE SCHEMA IF NOT EXISTS freshdesk_raw.silver;")
    cur.execute("CREATE SCHEMA IF NOT EXISTS freshdesk_raw.gold;")
    cur.execute("CREATE ROLE IF NOT EXISTS freshdesk_pipeline_role;")
    cur.execute(
        "CREATE USER IF NOT EXISTS pipeline_user "
        "PASSWORD=%s "
        "DEFAULT_ROLE=%s", (os.getenv('SNOWFLAKE_PIPELINE_PASSWORD'), 'freshdesk_pipeline_role')
    )
    cur.execute("GRANT ROLE freshdesk_pipeline_role TO USER pipeline_user;")
    cur.execute("GRANT USAGE ON WAREHOUSE freshdesk_wh TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT USAGE ON DATABASE freshdesk_raw TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON SCHEMA freshdesk_raw.raw TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON SCHEMA freshdesk_raw.bronze TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON SCHEMA freshdesk_raw.silver TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON SCHEMA freshdesk_raw.gold TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA freshdesk_raw.raw TO ROLE freshdesk_pipeline_role;")
    cur.execute("GRANT ALL ON FUTURE TABLES IN SCHEMA freshdesk_raw.raw TO ROLE freshdesk_pipeline_role;")

def create_raw_table_if_not_exist(cur, table_name):
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS freshdesk_raw.raw.{table_name}(" 
        "_raw       VARIANT,"
        "_loaded_at TIMESTAMP,"
        "_source    VARCHAR,"
        "_batch_id  VARCHAR"
        ")"
    )

def create_watermarks_table_if_not_exist(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS freshdesk_raw.raw._pipeline_watermarks("
        "source      VARCHAR PRIMARY KEY,"
        "last_loaded TIMESTAMP_TZ"
        ")"
    )

def verify_pipeline_user(con):
    cur = con.cursor()
    current_user = cur.execute("SELECT CURRENT_USER();").fetchone()
    print(current_user)

def main():
    con = connect_as_admin()
    cur = con.cursor()
    create_infrastructure(con)
    create_raw_table_if_not_exist(cur, "tickets")
    create_raw_table_if_not_exist(cur, "companies")
    create_raw_table_if_not_exist(cur, "contacts")
    create_watermarks_table_if_not_exist(cur)
    con.close()
    con = connect_as_user()
    verify_pipeline_user(con)
    con.close()

if __name__ == '__main__':
    main()