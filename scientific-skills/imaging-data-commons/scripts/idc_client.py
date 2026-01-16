"""
IDC Client - Simplified wrapper around idc-index for common operations

This script provides convenience methods for common IDC queries and operations,
making it easier to search for imaging data by cancer type, modality, collection, etc.

Usage:
    from scripts.idc_client import IDCClient

    client = IDCClient()
    results = client.search_by_cancer_type('Breast', modality='MR')
"""

from idc_index import IDCClient as BaseIDCClient
from typing import Optional, List, Dict
import pandas as pd


class IDCClient:
    """Simplified wrapper around idc-index.IDCClient with convenience methods"""

    def __init__(self):
        """Initialize the IDC client"""
        self.client = BaseIDCClient()

    def search_by_cancer_type(
        self,
        cancer_type: str,
        modality: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Search for imaging series by cancer type.

        Args:
            cancer_type: Cancer type (e.g., 'Breast', 'Lung', 'Brain')
            modality: Optional imaging modality filter (e.g., 'CT', 'MR', 'PT')
            limit: Maximum number of results to return

        Returns:
            pandas DataFrame with series information

        Example:
            >>> client = IDCClient()
            >>> breast_mr = client.search_by_cancer_type('Breast', modality='MR')
            >>> print(f"Found {len(breast_mr)} breast MRI series")
        """
        modality_filter = f"AND Modality = '{modality}'" if modality else ""

        query = f"""
        SELECT
          collection_id,
          PatientID,
          SeriesInstanceUID,
          Modality,
          BodyPartExamined,
          SeriesDescription,
          license_short_name
        FROM index
        WHERE cancer_type = '{cancer_type}'
          {modality_filter}
        LIMIT {limit}
        """

        try:
            return self.client.sql_query(query)
        except Exception as e:
            print(f"Error searching by cancer type: {e}")
            return pd.DataFrame()

    def search_by_modality(
        self,
        modality: str,
        body_part: Optional[str] = None,
        collection_id: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Search for imaging series by modality.

        Args:
            modality: Imaging modality (e.g., 'CT', 'MR', 'PT', 'CR', 'DX')
            body_part: Optional body part filter (e.g., 'CHEST', 'BRAIN', 'ABDOMEN')
            collection_id: Optional collection filter
            limit: Maximum number of results to return

        Returns:
            pandas DataFrame with series information

        Example:
            >>> client = IDCClient()
            >>> lung_ct = client.search_by_modality('CT', body_part='LUNG')
        """
        body_filter = f"AND BodyPartExamined LIKE '%{body_part}%'" if body_part else ""
        collection_filter = f"AND collection_id = '{collection_id}'" if collection_id else ""

        query = f"""
        SELECT
          collection_id,
          PatientID,
          SeriesInstanceUID,
          Modality,
          BodyPartExamined,
          Manufacturer,
          license_short_name
        FROM index
        WHERE Modality = '{modality}'
          {body_filter}
          {collection_filter}
        LIMIT {limit}
        """

        try:
            return self.client.sql_query(query)
        except Exception as e:
            print(f"Error searching by modality: {e}")
            return pd.DataFrame()

    def search_by_collection(
        self,
        collection_id: str,
        modality: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Search for imaging series within a specific collection.

        Args:
            collection_id: Collection identifier (e.g., 'tcga_luad', 'nlst')
            modality: Optional modality filter
            limit: Maximum number of results

        Returns:
            pandas DataFrame with series information

        Example:
            >>> client = IDCClient()
            >>> tcga_series = client.search_by_collection('tcga_luad', modality='CT')
        """
        modality_filter = f"AND Modality = '{modality}'" if modality else ""

        query = f"""
        SELECT
          PatientID,
          SeriesInstanceUID,
          Modality,
          BodyPartExamined,
          SeriesDescription,
          StudyDate
        FROM index
        WHERE collection_id = '{collection_id}'
          {modality_filter}
        LIMIT {limit}
        """

        try:
            return self.client.sql_query(query)
        except Exception as e:
            print(f"Error searching collection: {e}")
            return pd.DataFrame()

    def get_collections_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for all IDC collections.

        Returns:
            pandas DataFrame with collection summaries

        Example:
            >>> client = IDCClient()
            >>> summary = client.get_collections_summary()
            >>> print(summary)
        """
        query = """
        SELECT
          collection_id,
          COUNT(DISTINCT PatientID) as num_patients,
          COUNT(DISTINCT SeriesInstanceUID) as num_series,
          COUNT(*) as num_instances,
          license_short_name
        FROM index
        GROUP BY collection_id, license_short_name
        ORDER BY num_patients DESC
        """

        try:
            return self.client.sql_query(query)
        except Exception as e:
            print(f"Error getting collections summary: {e}")
            return pd.DataFrame()

    def check_licenses(
        self,
        collection_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Check licensing information for collections.

        Args:
            collection_id: Optional collection to check (if None, checks all)

        Returns:
            pandas DataFrame with license information

        Example:
            >>> client = IDCClient()
            >>> licenses = client.check_licenses(collection_id='tcga_luad')
            >>> print(licenses)
        """
        collection_filter = f"WHERE collection_id = '{collection_id}'" if collection_id else ""

        query = f"""
        SELECT DISTINCT
          collection_id,
          license_short_name,
          license_long_name,
          license_url,
          COUNT(DISTINCT SeriesInstanceUID) as num_series
        FROM index
        {collection_filter}
        GROUP BY collection_id, license_short_name, license_long_name, license_url
        ORDER BY collection_id
        """

        try:
            return self.client.sql_query(query)
        except Exception as e:
            print(f"Error checking licenses: {e}")
            return pd.DataFrame()

    def download_series(
        self,
        series_uids: List[str],
        download_dir: str,
        dir_template: Optional[str] = None
    ) -> None:
        """
        Download specific imaging series by UID.

        Args:
            series_uids: List of SeriesInstanceUID values to download
            download_dir: Target directory for downloads
            dir_template: Optional directory template for organizing files

        Example:
            >>> client = IDCClient()
            >>> series = ['1.3.6.1.4.1...', '1.3.6.1.4.1...']
            >>> client.download_series(series, './data')
        """
        try:
            kwargs = {'downloadDir': download_dir}
            if dir_template:
                kwargs['dirTemplate'] = dir_template

            self.client.download_from_selection(
                seriesInstanceUID=series_uids,
                **kwargs
            )
            print(f"Successfully initiated download of {len(series_uids)} series to {download_dir}")
        except Exception as e:
            print(f"Error downloading series: {e}")


if __name__ == "__main__":
    # Example usage and testing
    print("IDC Client - Example Usage")
    print("=" * 50)

    client = IDCClient()

    # Example 1: Search by cancer type
    print("\n1. Searching for breast cancer MRI scans...")
    breast_mr = client.search_by_cancer_type('Breast', modality='MR', limit=5)
    print(f"   Found {len(breast_mr)} series")
    if not breast_mr.empty:
        print(f"   First series: {breast_mr.iloc[0]['SeriesInstanceUID']}")

    # Example 2: Get collections summary
    print("\n2. Getting collections summary...")
    summary = client.get_collections_summary()
    print(f"   Total collections: {len(summary)}")
    if not summary.empty:
        top_collection = summary.iloc[0]
        print(f"   Largest collection: {top_collection['collection_id']} "
              f"({top_collection['num_patients']} patients)")

    # Example 3: Check licenses
    print("\n3. Checking license information...")
    licenses = client.check_licenses()
    cc_by_count = len(licenses[licenses['license_short_name'] == 'CC-BY'])
    print(f"   CC-BY licensed collections: {cc_by_count}")

    print("\n" + "=" * 50)
    print("Example complete. Use this client in your scripts!")
