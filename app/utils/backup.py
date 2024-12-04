"""
Database backup utility implementing the Physical Viewpoint requirement R9:
Daily backups of the database to prevent data loss.
"""
import os
import subprocess
from datetime import datetime
import logging
from azure.storage.blob import BlobServiceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self):
        self.db_server = os.getenv('DB_SERVER')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USERNAME')
        self.db_password = os.getenv('DB_PASSWORD')
        self.backup_container = "database-backups"

    def create_backup(self):
        """Create a backup of the database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_{self.db_name}_{timestamp}.bak"
            
            # Create backup using SQL Server syntax
            backup_query = f"""
            BACKUP DATABASE [{self.db_name}]
            TO DISK = N'{backup_file}'
            WITH FORMAT, COMPRESSION;
            """
            
            # Execute backup query using sqlcmd
            subprocess.run([
                'sqlcmd',
                '-S', self.db_server,
                '-U', self.db_user,
                '-P', self.db_password,
                '-Q', backup_query
            ], check=True)

            logger.info(f"Database backup created: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            raise

    def upload_to_azure(self, backup_file):
        """Upload backup file to Azure Blob Storage"""
        try:
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Get container client
            container_client = blob_service_client.get_container_client(self.backup_container)
            
            # Upload the backup file
            with open(backup_file, "rb") as data:
                blob_client = container_client.upload_blob(
                    name=backup_file,
                    data=data,
                    overwrite=True
                )
            
            logger.info(f"Backup uploaded to Azure: {backup_file}")
            
            # Remove local backup file after upload
            os.remove(backup_file)
            logger.info(f"Local backup file removed: {backup_file}")
        except Exception as e:
            logger.error(f"Backup upload failed: {str(e)}")
            raise

def run_daily_backup():
    """Execute daily backup procedure"""
    try:
        backup = DatabaseBackup()
        backup_file = backup.create_backup()
        backup.upload_to_azure(backup_file)
        logger.info("Daily backup completed successfully")
    except Exception as e:
        logger.error(f"Daily backup failed: {str(e)}")
        raise
