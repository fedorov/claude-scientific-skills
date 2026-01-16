"""
IDC Viewer Utilities - Helpers for visualizing IDC data in browsers

This script provides utilities for generating viewer URLs and launching
IDC Portal viewers for DICOM series without downloading data.

Usage:
    from scripts.idc_viewer import generate_viewer_url, open_in_browser

    url = generate_viewer_url(series_uid)
    open_in_browser(url)
"""

import webbrowser
import re
from typing import Optional, Dict, List
from idc_index import IDCClient


# IDC viewer base URLs
VIEWER_BASE_URLS = {
    'ohif': 'https://viewer.imaging.datacommons.cancer.gov/viewer/',
    'volview': 'https://viewer.imaging.datacommons.cancer.gov/volview/',
    'slim': 'https://viewer.imaging.datacommons.cancer.gov/slim/',
}

PORTAL_BASE_URL = 'https://portal.imaging.datacommons.cancer.gov/explore/'


def validate_series_uid(series_uid: str) -> bool:
    """
    Validate that a string is a properly formatted DICOM Series UID.

    Args:
        series_uid: Series UID to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> uid = "1.3.6.1.4.1.14519.5.2.1.6279.6001.12345"
        >>> if validate_series_uid(uid):
        ...     print("Valid UID")
    """
    # DICOM UIDs are typically in format: digits.digits.digits...
    # Must start with numbers and contain only numbers and dots
    pattern = r'^\d+(\.\d+)+$'

    if not series_uid or not isinstance(series_uid, str):
        return False

    if not re.match(pattern, series_uid):
        print(f"Invalid Series UID format: {series_uid}")
        print("Expected format: digits.digits.digits (e.g., 1.2.840.xxxxx)")
        return False

    return True


def generate_viewer_url(
    series_uid: str,
    viewer_type: str = 'ohif'
) -> str:
    """
    Generate a viewer URL for a DICOM series.

    Args:
        series_uid: DICOM SeriesInstanceUID
        viewer_type: Type of viewer ('ohif', 'volview', 'slim')

    Returns:
        Full URL to viewer

    Example:
        >>> url = generate_viewer_url(
        ...     "1.3.6.1.4.1.14519.5.2.1.6279.6001.12345",
        ...     viewer_type='ohif'
        ... )
        >>> print(url)
    """
    if not validate_series_uid(series_uid):
        raise ValueError(f"Invalid Series UID: {series_uid}")

    if viewer_type not in VIEWER_BASE_URLS:
        raise ValueError(
            f"Unknown viewer type: {viewer_type}. "
            f"Valid options: {list(VIEWER_BASE_URLS.keys())}"
        )

    base_url = VIEWER_BASE_URLS[viewer_type]
    return f"{base_url}{series_uid}"


def generate_portal_search_url(filters: Optional[Dict[str, str]] = None) -> str:
    """
    Generate IDC Portal search URL with optional filters.

    Args:
        filters: Dictionary of filter parameters (collection_id, modality, etc.)

    Returns:
        IDC Portal URL with filters

    Example:
        >>> filters = {'collection_id': 'tcga_luad', 'Modality': 'CT'}
        >>> url = generate_portal_search_url(filters)
    """
    url = PORTAL_BASE_URL

    if filters:
        # Convert filters to URL parameters
        params = []
        for key, value in filters.items():
            params.append(f"{key}={value}")
        if params:
            url += "?" + "&".join(params)

    return url


def open_in_browser(url: str) -> bool:
    """
    Open URL in default web browser.

    Args:
        url: URL to open

    Returns:
        True if successful, False otherwise

    Example:
        >>> url = generate_viewer_url(series_uid)
        >>> open_in_browser(url)
    """
    try:
        webbrowser.open(url)
        print(f"Opened in browser: {url}")
        return True
    except Exception as e:
        print(f"Error opening browser: {e}")
        print(f"Manual URL: {url}")
        return False


def get_series_metadata(series_uid: str) -> Dict:
    """
    Retrieve metadata for a series from IDC mini-index.

    Args:
        series_uid: DICOM SeriesInstanceUID

    Returns:
        Dictionary with series metadata

    Example:
        >>> metadata = get_series_metadata(series_uid)
        >>> print(f"Modality: {metadata.get('Modality')}")
    """
    if not validate_series_uid(series_uid):
        return {}

    client = IDCClient()

    query = f"""
    SELECT
      collection_id,
      PatientID,
      StudyInstanceUID,
      SeriesInstanceUID,
      Modality,
      BodyPartExamined,
      SeriesDescription,
      Manufacturer,
      ManufacturerModelName,
      license_short_name
    FROM index
    WHERE SeriesInstanceUID = '{series_uid}'
    LIMIT 1
    """

    try:
        result = client.sql_query(query)

        if result.empty:
            print(f"No metadata found for Series UID: {series_uid}")
            return {}

        # Convert first row to dictionary
        metadata = result.iloc[0].to_dict()
        return metadata

    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return {}


def preview_series(series_uid: str, viewer_type: str = 'ohif') -> None:
    """
    Preview a series: show metadata and open in viewer.

    Args:
        series_uid: DICOM SeriesInstanceUID
        viewer_type: Type of viewer to use

    Example:
        >>> preview_series("1.3.6.1.4.1.14519.5.2.1.6279.6001.12345")
    """
    print(f"\nPreviewing Series: {series_uid}")
    print("=" * 70)

    # Get and display metadata
    metadata = get_series_metadata(series_uid)

    if not metadata:
        print("Could not retrieve metadata")
        return

    print("\nMetadata:")
    print(f"  Collection: {metadata.get('collection_id', 'N/A')}")
    print(f"  Patient ID: {metadata.get('PatientID', 'N/A')}")
    print(f"  Modality: {metadata.get('Modality', 'N/A')}")
    print(f"  Body Part: {metadata.get('BodyPartExamined', 'N/A')}")
    print(f"  Description: {metadata.get('SeriesDescription', 'N/A')}")
    print(f"  Scanner: {metadata.get('Manufacturer', 'N/A')} "
          f"{metadata.get('ManufacturerModelName', '')}")
    print(f"  License: {metadata.get('license_short_name', 'N/A')}")

    # Generate and open viewer URL
    print(f"\nOpening in {viewer_type.upper()} viewer...")
    url = generate_viewer_url(series_uid, viewer_type)
    open_in_browser(url)

    print("=" * 70)


def preview_collection_sample(
    collection_id: str,
    modality: Optional[str] = None,
    limit: int = 5
) -> None:
    """
    Preview sample series from a collection.

    Args:
        collection_id: Collection to preview
        modality: Optional modality filter
        limit: Number of series to preview

    Example:
        >>> preview_collection_sample('rider_pilot', modality='CT', limit=3)
    """
    client = IDCClient()

    modality_filter = f"AND Modality = '{modality}'" if modality else ""

    query = f"""
    SELECT
      SeriesInstanceUID,
      PatientID,
      Modality,
      SeriesDescription
    FROM index
    WHERE collection_id = '{collection_id}'
      {modality_filter}
    LIMIT {limit}
    """

    try:
        results = client.sql_query(query)

        if results.empty:
            print(f"No series found in collection: {collection_id}")
            return

        print(f"\nFound {len(results)} sample series from {collection_id}:")
        print("=" * 70)

        for idx, row in results.iterrows():
            series_uid = row['SeriesInstanceUID']
            viewer_url = generate_viewer_url(series_uid)

            print(f"\n{idx + 1}. Patient: {row['PatientID']}")
            print(f"   Modality: {row['Modality']}")
            print(f"   Description: {row.get('SeriesDescription', 'N/A')}")
            print(f"   Viewer URL: {viewer_url}")

        print("\n" + "=" * 70)
        print("Copy any URL above to view in browser")

    except Exception as e:
        print(f"Error previewing collection: {e}")


if __name__ == "__main__":
    # Example usage and testing
    print("IDC Viewer Utilities - Example Usage")
    print("=" * 70)

    # Example 1: Validate Series UID
    print("\n1. Validating Series UIDs...")
    valid_uid = "1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178"
    invalid_uid = "not-a-valid-uid"

    print(f"   Valid UID: {validate_series_uid(valid_uid)}")
    print(f"   Invalid UID: {validate_series_uid(invalid_uid)}")

    # Example 2: Generate viewer URLs
    print("\n2. Generating viewer URLs...")
    if validate_series_uid(valid_uid):
        ohif_url = generate_viewer_url(valid_uid, viewer_type='ohif')
        print(f"   OHIF: {ohif_url}")

    # Example 3: Preview collection sample
    print("\n3. Previewing collection sample...")
    print("   (Querying rider_pilot collection)")
    preview_collection_sample('rider_pilot', modality='CT', limit=3)

    print("\n" + "=" * 70)
    print("Example complete!")
    print("\nTo open in browser, use:")
    print("  url = generate_viewer_url(series_uid)")
    print("  open_in_browser(url)")
