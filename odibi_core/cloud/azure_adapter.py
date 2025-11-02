"""
Azure Cloud Adapter (Phase 7)

Provides full integration with Azure cloud services:
- Azure Blob Storage / ADLS Gen2 (Data Lake Storage)
- Azure Key Vault (secrets management)
- Azure SQL Database (relational storage)

Authentication methods:
- Service Principal (client_id + client_secret)
- Managed Identity (for Azure-hosted applications)
- Account Key (for development)

Usage:
    # Using account key
    adapter = AzureAdapter(
        account_name="mystorageaccount",
        account_key="...",
        simulate=False
    )
    adapter.connect()

    # Read from ADLS
    df = adapter.read("container/path/data.parquet")

    # Write to ADLS
    adapter.write(df, "container/path/output.parquet")

    # Get secret from Key Vault
    secret = adapter.get_secret("keyvault-name", "secret-name")

    # Connect to Azure SQL
    conn = adapter.connect_sql("server", "database", "username", "password")
"""

import logging
import os
from typing import Any, Dict, List, Optional
import pandas as pd

from .cloud_adapter import CloudAdapterBase

logger = logging.getLogger(__name__)


class AzureAdapter(CloudAdapterBase):
    """
    Azure Blob Storage / ADLS Gen2 adapter with Key Vault and SQL support.

    Attributes:
        account_name: Azure storage account name
        account_key: Storage account key (optional if using managed identity)
        container: Default container name (optional)
        simulate: If True, simulates Azure operations without actual API calls
    """

    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        container: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        simulate: bool = False,
        **kwargs,
    ):
        """
        Initialize Azure adapter.

        Args:
            account_name: Storage account name (or from AZURE_STORAGE_ACCOUNT env var)
            account_key: Storage account key (or from AZURE_STORAGE_KEY env var)
            container: Default container name
            tenant_id: Azure AD tenant ID (for service principal auth)
            client_id: Service principal client ID
            client_secret: Service principal client secret
            simulate: If True, run in simulation mode
            **kwargs: Additional Azure-specific config
        """
        super().__init__(simulate=simulate, **kwargs)

        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_KEY")
        self.container = container
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")

        self.file_system_client = None
        self.service_client = None
        self.credential = None

        if not simulate and not self.account_name:
            raise ValueError(
                "account_name must be provided or set via AZURE_STORAGE_ACCOUNT env var"
            )

    def connect(self) -> bool:
        """
        Establish connection to Azure Blob Storage / ADLS Gen2.

        Returns:
            bool: True if connection successful
        """
        if self.simulate:
            logger.info("[SIMULATE] Connected to Azure ADLS Gen2")
            self.connected = True
            return True

        try:
            # Try importing Azure SDK
            from azure.storage.filedatalake import DataLakeServiceClient
            from azure.identity import DefaultAzureCredential, ClientSecretCredential

            # Determine authentication method
            if self.account_key:
                # Use account key
                account_url = f"https://{self.account_name}.dfs.core.windows.net"
                self.service_client = DataLakeServiceClient(
                    account_url=account_url, credential=self.account_key
                )
                logger.info(
                    f"Connected to Azure ADLS using account key: {self.account_name}"
                )

            elif self.client_id and self.client_secret and self.tenant_id:
                # Use service principal
                self.credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
                account_url = f"https://{self.account_name}.dfs.core.windows.net"
                self.service_client = DataLakeServiceClient(
                    account_url=account_url, credential=self.credential
                )
                logger.info(
                    f"Connected to Azure ADLS using service principal: {self.account_name}"
                )

            else:
                # Use managed identity / default credentials
                self.credential = DefaultAzureCredential()
                account_url = f"https://{self.account_name}.dfs.core.windows.net"
                self.service_client = DataLakeServiceClient(
                    account_url=account_url, credential=self.credential
                )
                logger.info(
                    f"Connected to Azure ADLS using managed identity: {self.account_name}"
                )

            self.connected = True
            return True

        except ImportError as e:
            logger.error(
                f"Azure SDK not installed. Install with: pip install azure-storage-file-datalake azure-identity\n"
                f"Error: {e}"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Azure ADLS: {e}")
            raise

    def read(self, path: str, format: str = "parquet", **kwargs) -> pd.DataFrame:
        """
        Read data from Azure Blob Storage / ADLS Gen2.

        Args:
            path: Path in format "container/folder/file.parquet" or "/container/folder/file.parquet"
            format: File format ("parquet", "csv", "json")
            **kwargs: Additional read options (e.g., columns for parquet)

        Returns:
            pd.DataFrame: Data read from Azure
        """
        if self.simulate:
            logger.info(f"[SIMULATE] Reading {format} from Azure: {path}")
            return pd.DataFrame({"simulated": [1, 2, 3], "data": ["a", "b", "c"]})

        if not self.connected:
            self.connect()

        # Parse container and file path
        container, file_path = self._parse_path(path)

        try:
            # Get file system client
            file_system_client = self.service_client.get_file_system_client(container)

            # Get file client
            file_client = file_system_client.get_file_client(file_path)

            # Download file
            download = file_client.download_file()
            data = download.readall()

            # Parse based on format
            import io

            if format == "parquet":
                return pd.read_parquet(io.BytesIO(data), **kwargs)
            elif format == "csv":
                return pd.read_csv(io.BytesIO(data), **kwargs)
            elif format == "json":
                return pd.read_json(io.BytesIO(data), **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to read from Azure path {path}: {e}")
            raise

    def write(
        self, data: pd.DataFrame, path: str, format: str = "parquet", **kwargs
    ) -> bool:
        """
        Write data to Azure Blob Storage / ADLS Gen2.

        Args:
            data: DataFrame to write
            path: Path in format "container/folder/file.parquet"
            format: File format ("parquet", "csv", "json")
            **kwargs: Additional write options

        Returns:
            bool: True if write successful
        """
        if self.simulate:
            logger.info(
                f"[SIMULATE] Writing {len(data)} rows as {format} to Azure: {path}"
            )
            return True

        if not self.connected:
            self.connect()

        # Parse container and file path
        container, file_path = self._parse_path(path)

        try:
            # Get file system client
            file_system_client = self.service_client.get_file_system_client(container)

            # Create container if it doesn't exist
            try:
                file_system_client.create_file_system()
                logger.info(f"Created container: {container}")
            except Exception:
                pass  # Container already exists

            # Get file client
            file_client = file_system_client.get_file_client(file_path)

            # Convert DataFrame to bytes
            import io

            buffer = io.BytesIO()

            if format == "parquet":
                data.to_parquet(buffer, **kwargs)
            elif format == "csv":
                data.to_csv(buffer, index=False, **kwargs)
            elif format == "json":
                data.to_json(buffer, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Upload
            buffer.seek(0)
            file_client.upload_data(buffer.read(), overwrite=True)

            logger.info(f"Wrote {len(data)} rows to Azure: {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to write to Azure path {path}: {e}")
            raise

    def exists(self, path: str) -> bool:
        """Check if path exists in Azure Blob Storage"""
        if self.simulate:
            logger.info(f"[SIMULATE] Checking existence: {path}")
            return True

        if not self.connected:
            self.connect()

        container, file_path = self._parse_path(path)

        try:
            file_system_client = self.service_client.get_file_system_client(container)
            file_client = file_system_client.get_file_client(file_path)
            return file_client.exists()
        except Exception:
            return False

    def list(self, path: str, pattern: Optional[str] = None) -> List[str]:
        """
        List files in Azure Blob Storage path.

        Args:
            path: Container or container/folder path
            pattern: Optional glob pattern (e.g., "*.parquet")

        Returns:
            List of file paths
        """
        if self.simulate:
            logger.info(f"[SIMULATE] Listing files in: {path}")
            return ["file1.parquet", "file2.parquet", "file3.csv"]

        if not self.connected:
            self.connect()

        container, folder_path = self._parse_path(path)

        try:
            file_system_client = self.service_client.get_file_system_client(container)
            paths = file_system_client.get_paths(path=folder_path or None)

            file_list = []
            for path_item in paths:
                if not path_item.is_directory:
                    file_name = path_item.name

                    # Apply pattern filter if provided
                    if pattern:
                        import fnmatch

                        if fnmatch.fnmatch(file_name, pattern):
                            file_list.append(file_name)
                    else:
                        file_list.append(file_name)

            return file_list

        except Exception as e:
            logger.error(f"Failed to list Azure path {path}: {e}")
            raise

    def delete(self, path: str) -> bool:
        """Delete file from Azure Blob Storage"""
        if self.simulate:
            logger.info(f"[SIMULATE] Deleting: {path}")
            return True

        if not self.connected:
            self.connect()

        container, file_path = self._parse_path(path)

        try:
            file_system_client = self.service_client.get_file_system_client(container)
            file_client = file_system_client.get_file_client(file_path)
            file_client.delete_file()
            logger.info(f"Deleted file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Azure path {path}: {e}")
            raise

    def get_secret(self, vault_name: str, secret_name: str) -> str:
        """
        Retrieve secret from Azure Key Vault.

        Args:
            vault_name: Key Vault name
            secret_name: Secret name

        Returns:
            str: Secret value
        """
        if self.simulate:
            logger.info(
                f"[SIMULATE] Getting secret {secret_name} from vault {vault_name}"
            )
            return "simulated-secret-value"

        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential, ClientSecretCredential

            # Use same credential as storage
            if not self.credential:
                if self.client_id and self.client_secret and self.tenant_id:
                    self.credential = ClientSecretCredential(
                        tenant_id=self.tenant_id,
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                    )
                else:
                    self.credential = DefaultAzureCredential()

            vault_url = f"https://{vault_name}.vault.azure.net"
            client = SecretClient(vault_url=vault_url, credential=self.credential)

            secret = client.get_secret(secret_name)
            logger.info(f"Retrieved secret {secret_name} from {vault_name}")
            return secret.value

        except ImportError as e:
            logger.error(
                "Azure Key Vault SDK not installed. Install with: pip install azure-keyvault-secrets"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name} from {vault_name}: {e}")
            raise

    def connect_sql(
        self,
        server: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "ODBC Driver 17 for SQL Server",
    ):
        """
        Connect to Azure SQL Database.

        Args:
            server: SQL server name (e.g., "myserver.database.windows.net")
            database: Database name
            username: SQL username (optional if using managed identity)
            password: SQL password
            driver: ODBC driver name

        Returns:
            pyodbc.Connection: Database connection
        """
        if self.simulate:
            logger.info(f"[SIMULATE] Connecting to Azure SQL: {server}/{database}")
            return None

        try:
            import pyodbc

            if username and password:
                # SQL authentication
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password}"
                )
            else:
                # Managed identity
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"Authentication=ActiveDirectoryMsi"
                )

            conn = pyodbc.connect(conn_str)
            logger.info(f"Connected to Azure SQL: {server}/{database}")
            return conn

        except ImportError:
            logger.error("pyodbc not installed. Install with: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Azure SQL {server}/{database}: {e}")
            raise

    def _parse_path(self, path: str) -> tuple:
        """
        Parse Azure path into container and file path.

        Args:
            path: Path like "container/folder/file.parquet" or "/container/folder/file.parquet"

        Returns:
            tuple: (container_name, file_path)
        """
        # Remove leading slash if present
        path = path.lstrip("/")

        # Split into container and file path
        parts = path.split("/", 1)

        if len(parts) == 1:
            # Just container name
            return parts[0], ""
        else:
            return parts[0], parts[1]
