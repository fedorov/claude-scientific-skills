---
name: idc-navigator
description: Helps users discover, query, visualize, download, and use cancer imaging data from NCI Imaging Data Commons (IDC). Use when users ask to search IDC data, find imaging datasets by cancer type or modality, download DICOM files from IDC, visualize medical images from IDC, query IDC metadata, understand IDC licensing, or work with IDC tools (idc-index, Portal, BigQuery, SlicerIDCBrowser).
---

# IDC Navigator

## Overview

This skill helps users work with the National Cancer Institute Imaging Data Commons (IDC), a cloud-based repository of >95TB of publicly available cancer imaging data in DICOM format. IDC provides radiology, slide microscopy, and image-derived data with accompanying clinical metadata.

## Tool Selection Guide

Choose the right IDC tool based on the task:

**For quick exploration and discovery:**
- IDC Portal (https://portal.imaging.datacommons.cancer.gov/explore/) - web-based browsing, filtering, and zero-footprint visualization

**For programmatic access (recommended for beginners):**
- idc-index Python package - query and download without Google Cloud account or billing
- Installation: `pip install --upgrade idc-index`
- No authentication required

**For visualization:**
- IDC Portal viewers (easiest) - in-browser OHIF, VolView, and Slim viewers
- SlicerIDCBrowser - 3D Slicer extension for advanced visualization

**For complex metadata queries (requires Google Cloud setup):**
- BigQuery - requires Google account and project with billing configured
- Access tables at `bigquery-public-data.idc_current.*`

## Common Workflows

### Discover Available Data

```python
from idc_index import IDCClient

client = IDCClient()

# SQL query against mini-index
query = """
SELECT DISTINCT
  collection_id,
  Modality,
  COUNT(*) as series_count
FROM index
WHERE cancer_type = 'Breast'
GROUP BY collection_id, Modality
"""

results = client.sql_query(query)
```

### Download Data by Collection

```python
from idc_index import IDCClient

client = IDCClient()

# Download entire collection (small example)
client.download_from_selection(
    collection_id="rider_pilot",
    downloadDir="./my_data"
)
```

### Download Filtered Data

```python
from idc_index import IDCClient

client = IDCClient()

# Query for specific criteria
query = """
SELECT SeriesInstanceUID
FROM index
WHERE Modality = 'MR'
  AND BodyPartExamined = 'BRAIN'
LIMIT 10
"""

selection = client.sql_query(query)

# Download selected series
client.download_from_selection(
    seriesInstanceUID=list(selection["SeriesInstanceUID"].values),
    downloadDir="./brain_mr"
)

```

### Visualize Data

**Option 1: IDC Portal (easiest)**
1. Use idc-index or BigQuery to find SeriesInstanceUID
2. Navigate to Portal viewer:
   `https://viewer.imaging.datacommons.cancer.gov/viewer/{SeriesInstanceUID}`

**Option 2: Direct URL construction**
```python
series_uid = "1.3.6.1.4.1.14519..."
viewer_url = f"https://viewer.imaging.datacommons.cancer.gov/viewer/{series_uid}"
print(f"View in browser: {viewer_url}")
```

### Query Metadata

The idc-index package provides a mini-index with key metadata fields. For comprehensive metadata queries, see references/bigquery_guide.md.

Available metadata fields in mini-index:
- collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID
- Modality, BodyPartExamined
- cancer_type, Manufacturer
- license information

## Understanding Licenses

All IDC data includes license information. Check before use:

```python
# Query to check licenses
query = """
SELECT DISTINCT
  collection_id,
  license_short_name,
  license_url
FROM index
GROUP BY collection_id, license_short_name, license_url
"""

licenses = client.sql_query(query)
```

**License types:**
- CC-BY (>95% of data) - allows commercial use with attribution
- CC-NC - non-commercial use only

Each file is tagged with its specific license.

## Resources

### references/

- **bigquery_guide.md** - Detailed guide for using BigQuery to query IDC metadata (for advanced users with GCP setup)
- **idc_index_api.md** - Complete API reference for idc-index Python package
- **metadata_schema.md** - IDC metadata organization and available fields

### Important Links

- IDC Portal: https://portal.imaging.datacommons.cancer.gov/explore/
- Documentation: https://learn.canceridc.dev/
- Tutorials: https://github.com/ImagingDataCommons/IDC-Tutorials
- User Forum: https://discourse.canceridc.dev/
- Citation: Fedorov et al., RadioGraphics (2023). https://doi.org/10.1148/rg.230180
