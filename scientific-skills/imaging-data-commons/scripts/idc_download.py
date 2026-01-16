"""
IDC Download Utilities - Advanced download helpers for IDC data

This script provides utilities for downloading IDC imaging data with
size estimation, batch processing, and progress tracking.

Usage:
    from scripts.idc_download import download_collection, get_download_size_estimate

    # Estimate size first
    size_gb = get_download_size_estimate(collection_id='rider_pilot')
    print(f"Download size: {size_gb:.2f} GB")

    # Download collection
    download_collection('rider_pilot', './data')
"""

from idc_index import IDCClient
from typing import Optional, List, Dict
import pandas as pd
import os


def get_download_size_estimate(
    collection_id: Optional[str] = None,
    series_uids: Optional[List[str]] = None
) -> float:
    """
    Estimate download size in GB for a collection or series list.

    Note: This is a rough estimate based on average DICOM instance sizes.
    Actual sizes may vary significantly.

    Args:
        collection_id: Collection to estimate (mutually exclusive with series_uids)
        series_uids: List of series UIDs to estimate

    Returns:
        Estimated size in GB

    Example:
        >>> size_gb = get_download_size_estimate(collection_id='rider_pilot')
        >>> print(f"Estimated size: {size_gb:.2f} GB")
    """
    client = IDCClient()

    if series_uids:
        # Estimate for specific series
        placeholders = "', '".join(series_uids)
        query = f"""
        SELECT COUNT(*) as instance_count
        FROM index
        WHERE SeriesInstanceUID IN ('{placeholders}')
        """
    elif collection_id:
        # Estimate for collection
        query = f"""
        SELECT COUNT(*) as instance_count
        FROM index
        WHERE collection_id = '{collection_id}'
        """
    else:
        raise ValueError("Must provide either collection_id or series_uids")

    try:
        result = client.sql_query(query)
        instance_count = result.iloc[0]['instance_count']

        # Average DICOM instance size estimate: ~0.5 MB
        # This varies widely (CT slices ~0.5MB, whole slide images ~100MB+)
        avg_mb_per_instance = 0.5
        estimated_gb = (instance_count * avg_mb_per_instance) / 1024

        print(f"Estimated {instance_count} instances → ~{estimated_gb:.2f} GB")
        return estimated_gb

    except Exception as e:
        print(f"Error estimating size: {e}")
        return 0.0


def download_collection(
    collection_id: str,
    output_dir: str,
    dir_template: Optional[str] = None,
    modality: Optional[str] = None,
    limit: Optional[int] = None
) -> None:
    """
    Download an entire collection or filtered subset.

    Args:
        collection_id: Collection identifier
        output_dir: Output directory for downloads
        dir_template: Optional directory organization template
        modality: Optional modality filter
        limit: Optional limit on number of series

    Example:
        >>> download_collection(
        ...     'rider_pilot',
        ...     './data',
        ...     dir_template='%PatientID/%Modality'
        ... )
    """
    client = IDCClient()

    # Build query to get series UIDs
    modality_filter = f"AND Modality = '{modality}'" if modality else ""
    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
    SELECT DISTINCT SeriesInstanceUID
    FROM index
    WHERE collection_id = '{collection_id}'
      {modality_filter}
    {limit_clause}
    """

    try:
        print(f"Querying {collection_id}...")
        series_df = client.sql_query(query)
        series_count = len(series_df)
        print(f"Found {series_count} series to download")

        if series_count == 0:
            print("No series found matching criteria")
            return

        # Estimate size
        size_gb = get_download_size_estimate(
            series_uids=list(series_df['SeriesInstanceUID'].values)
        )

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Download
        print(f"Downloading to {output_dir}...")
        kwargs = {'downloadDir': output_dir}
        if dir_template:
            kwargs['dirTemplate'] = dir_template

        client.download_from_selection(
            seriesInstanceUID=list(series_df['SeriesInstanceUID'].values),
            **kwargs
        )

        print(f"Download complete!")

    except Exception as e:
        print(f"Error downloading collection: {e}")


def download_by_query(
    sql_query: str,
    output_dir: str,
    dir_template: Optional[str] = None,
    save_manifest: bool = True
) -> None:
    """
    Download series matching a custom SQL query.

    Args:
        sql_query: SQL query returning SeriesInstanceUID column
        output_dir: Output directory
        dir_template: Optional directory template
        save_manifest: Whether to save query results as CSV manifest

    Example:
        >>> query = '''
        ... SELECT SeriesInstanceUID
        ... FROM index
        ... WHERE Modality = 'CT' AND BodyPartExamined = 'LUNG'
        ... LIMIT 10
        ... '''
        >>> download_by_query(query, './lung_ct')
    """
    client = IDCClient()

    try:
        print("Running query...")
        results = client.sql_query(sql_query)

        if 'SeriesInstanceUID' not in results.columns:
            raise ValueError("Query must return 'SeriesInstanceUID' column")

        series_count = len(results)
        print(f"Found {series_count} series")

        if series_count == 0:
            print("No series found")
            return

        # Save manifest
        if save_manifest:
            manifest_path = os.path.join(output_dir, 'download_manifest.csv')
            os.makedirs(output_dir, exist_ok=True)
            results.to_csv(manifest_path, index=False)
            print(f"Saved manifest to {manifest_path}")

        # Download
        kwargs = {'downloadDir': output_dir}
        if dir_template:
            kwargs['dirTemplate'] = dir_template

        client.download_from_selection(
            seriesInstanceUID=list(results['SeriesInstanceUID'].values),
            **kwargs
        )

        print("Download complete!")

    except Exception as e:
        print(f"Error in download_by_query: {e}")


def download_filtered(
    filters: Dict[str, str],
    output_dir: str,
    dir_template: Optional[str] = None,
    limit: int = 100
) -> None:
    """
    Download series using simple filter dictionary.

    Args:
        filters: Dictionary of field:value filters
                (e.g., {'Modality': 'CT', 'BodyPartExamined': 'LUNG'})
        output_dir: Output directory
        dir_template: Optional directory template
        limit: Maximum series to download

    Example:
        >>> filters = {
        ...     'Modality': 'MR',
        ...     'BodyPartExamined': 'BRAIN',
        ...     'collection_id': 'tcga_brca'
        ... }
        >>> download_filtered(filters, './brain_mr')
    """
    # Build WHERE clause from filters
    conditions = [f"{field} = '{value}'" for field, value in filters.items()]
    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
      SeriesInstanceUID,
      collection_id,
      PatientID,
      Modality
    FROM index
    WHERE {where_clause}
    LIMIT {limit}
    """

    download_by_query(query, output_dir, dir_template=dir_template)


def resume_download(
    manifest_file: str,
    output_dir: str,
    dir_template: Optional[str] = None
) -> None:
    """
    Resume download from a previously saved manifest CSV.

    Args:
        manifest_file: Path to CSV manifest with SeriesInstanceUID column
        output_dir: Output directory
        dir_template: Optional directory template

    Example:
        >>> resume_download('download_manifest.csv', './data')
    """
    try:
        print(f"Loading manifest from {manifest_file}...")
        manifest = pd.read_csv(manifest_file)

        if 'SeriesInstanceUID' not in manifest.columns:
            raise ValueError("Manifest must contain 'SeriesInstanceUID' column")

        series_uids = list(manifest['SeriesInstanceUID'].values)
        print(f"Found {len(series_uids)} series in manifest")

        client = IDCClient()
        kwargs = {'downloadDir': output_dir}
        if dir_template:
            kwargs['dirTemplate'] = dir_template

        client.download_from_selection(
            seriesInstanceUID=series_uids,
            **kwargs
        )

        print("Download resumed and complete!")

    except Exception as e:
        print(f"Error resuming download: {e}")


if __name__ == "__main__":
    # Example usage and testing
    print("IDC Download Utilities - Example Usage")
    print("=" * 50)

    # Example 1: Estimate collection size
    print("\n1. Estimating collection size...")
    size = get_download_size_estimate(collection_id='rider_pilot')
    print(f"   rider_pilot collection: ~{size:.2f} GB")

    # Example 2: Download with filters
    print("\n2. Example: Download filtered data")
    print("   (Not executing - remove comments to run)")
    print("""
    filters = {
        'Modality': 'CT',
        'BodyPartExamined': 'LUNG',
        'license_short_name': 'CC-BY'
    }
    download_filtered(filters, './lung_ct', limit=5)
    """)

    # Example 3: Custom query
    print("\n3. Example: Download by custom query")
    print("   (Not executing - remove comments to run)")
    print("""
    query = '''
    SELECT SeriesInstanceUID, PatientID, Modality
    FROM index
    WHERE collection_id = 'rider_pilot'
    LIMIT 5
    '''
    download_by_query(query, './rider_sample')
    """)

    print("\n" + "=" * 50)
    print("Examples complete. Uncomment code above to test downloads.")
