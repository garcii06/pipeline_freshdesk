import sys
sys.path.insert(0, '/opt/airflow/pipeline')

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator 

from utils.logger import get_logger
from datetime import datetime, timedelta

# import your modules
from extract.tickets import TicketsExtractor
from extract.companies import CompaniesExtractor
from extract.contacts import ContactsExtractor
from load.snowflake_loader import SnowflakeLoader

logger = get_logger(__name__)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def extract_load_tickets():
    logger.info("Starting tickets extraction")
    loader = SnowflakeLoader()
    watermark = loader.get_watermark('freshdesk_tickets')
    tickets_extractor  = TicketsExtractor()
    
    if watermark is None:
        tickets = tickets_extractor.get_incremental_tickets('2010-01-01T00:00:00Z')
    else:
        tickets = tickets_extractor.get_incremental_tickets(watermark[0].strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    logger.info(f"Fetched {len(tickets)} tickets")
    if tickets:
        max_updated_at = max(datetime.fromisoformat(t['updated_at'].replace('Z', '+00:00'))for t in tickets)
        loader.insert_records('tickets', tickets, 'freshdesk_tickets')
        loader.set_watermark('freshdesk_tickets', max_updated_at)

    loader.close()
    logger.info("Tickets extraction completed")

def extract_load_companies():
    logger.info("Starting companies extraction")
    loader = SnowflakeLoader()
    watermark = loader.get_watermark('freshdesk_companies')
    companies_extractor = CompaniesExtractor()
    
    if watermark is None:
        companies = companies_extractor.get_incremental_companies('2010-01-01T00:00:00Z')
    else:
        companies = companies_extractor.get_incremental_companies(watermark[0].strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    logger.info(f"Fetched {len(companies)} companies")
    if companies:
        max_updated_at = max(datetime.fromisoformat(t['updated_at'].replace('Z', '+00:00'))for t in companies)
        loader.insert_records('companies', companies, 'freshdesk_companies')
        loader.set_watermark('freshdesk_companies', max_updated_at)

    loader.close()
    logger.info("Companies extraction completed")

def extract_load_contacts():
    logger.info("Starting contacts extraction")
    loader = SnowflakeLoader()
    watermark = loader.get_watermark('freshdesk_contacts')
    contacts_extractor  = ContactsExtractor()
    
    if watermark is None:
        contacts = contacts_extractor.get_incremental_contacts('2010-01-01T00:00:00Z')
    else:
        contacts = contacts_extractor.get_incremental_contacts(watermark[0].strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    logger.info(f"Fetched {len(contacts)} contacts")
    if contacts:
        max_updated_at = max(datetime.fromisoformat(t['updated_at'].replace('Z', '+00:00'))for t in contacts)
        loader.insert_records('contacts', contacts, 'freshdesk_contacts')
        loader.set_watermark('freshdesk_contacts', max_updated_at)

    loader.close()
    logger.info("Contacts extraction completed")

with DAG(
    dag_id='freshdesk_pipeline',
    default_args=default_args,
    schedule='0 4 * * *',
    start_date=datetime(2026, 4, 1),
    catchup=False,
    tags=['freshdesk']
) as dag:

    tickets_task = PythonOperator(
        task_id='extract_load_tickets',
        python_callable=extract_load_tickets
    )

    companies_task = PythonOperator(
        task_id='extract_load_companies',
        python_callable=extract_load_companies
    )

    contacts_task = PythonOperator(
        task_id='extract_load_contacts',
        python_callable=extract_load_contacts
    )
 
    dbt_task = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/pipeline/freshdesk_dbt && dbt run'
    )

    [tickets_task, companies_task, contacts_task] >> dbt_task