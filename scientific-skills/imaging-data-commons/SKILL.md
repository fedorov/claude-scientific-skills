---
name: imaging-data-commons
description: Publicly available cancer imaging, image-derived data (annotations, features) in DICOM format, and various tools to explore, subset, visualize and access the data. Images available are contributed by large data collection initiatives, such as TCGA, CPTAC, CCDI, GETex, and individual investigators. Use when you want to find data to train new image analysis tools, explore hypotheses correlating imaging data with other data types, test existing tools. Query using rich metadata, download, visualize in browser, check licenses.
license: Unknown
metadata:
    skill-author: Andrey Fedorov, @fedorov
---

# Imaging Data Commons

## Overview

Use the `idc-index` Python package to query and download public cancer imaging data from the NCI Imaging Data Commons (IDC). No authentication required for data access.

**Primary tool:** `idc-index` ([GitHub](https://github.com/imagingdatacommons/idc-index))

**Check current data scale:**
```python
from idc_index import IDCClient
client = IDCClient()
# Get collection count and total series
stats = client.sql_query("""
    SELECT
        COUNT(DISTINCT collection_id) as collections,
        COUNT(DISTINCT PatientID) as patients,
        COUNT(DISTINCT SeriesInstanceUID) as series
    FROM index
""")
print(stats)
```

**Core workflow:**
1. Query metadata → `client.sql_query()`
2. Download DICOM files → `client.download_from_selection()`
3. Visualize in browser → `client.get_viewer_URL(seriesInstanceUID=...)`

## When to Use This Skill

- Finding publicly available radiology (CT, MR, PET) or pathology (slide microscopy) images
- Selecting image subsets by cancer type, modality, anatomical site, or other metadata
- Downloading DICOM data from IDC
- Checking data licenses before use in research or commercial applications
- Visualizing medical images in a browser without local DICOM viewer software

## IDC Data Model

IDC adds two grouping levels above the standard DICOM hierarchy (Patient → Study → Series → Instance):

- **collection_id**: Groups patients by disease, modality, or research focus (e.g., `tcga_luad`, `nlst`). A patient belongs to exactly one collection.
- **analysis_result_id**: Identifies derived objects (segmentations, annotations, radiomics features) across one or more original collections.

Use `collection_id` to find original imaging data, may include annotations deposited along with the images; use `analysis_result_id` to find AI-generated or expert annotations.

**Key identifiers for queries:**
| Identifier | Scope | Use for |
|------------|-------|---------|
| `collection_id` | Dataset grouping | Filtering by project/study |
| `PatientID` | Patient | Grouping images by patient |
| `SeriesInstanceUID` | Image series | Downloads and visualization |

## Data Access Options

| Method | Auth Required | Best For |
|--------|---------------|----------|
| `idc-index` | No | Most queries and downloads (recommended) |
| IDC Portal | No | Interactive exploration, manual selection |
| BigQuery | Yes (GCP account) | Complex queries, full DICOM metadata |
| DICOMweb proxy | No | Tool integration via DICOMweb API |

**DICOMweb endpoint (public, no auth):**
`https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb`

## Installation and Setup

**Required (for basic access):**
```bash
pip install --upgrade idc-index
```

**Optional (for advanced BigQuery access):**
```bash
pip install google-cloud-bigquery db-dtypes
# Requires Google Cloud project with billing configured
```

**Optional (for data analysis):**
```bash
pip install pandas numpy pydicom
```

## Core Capabilities

### 1. Data Discovery and Exploration

Discover what imaging collections and data are available in IDC:

```python
from idc_index import IDCClient

client = IDCClient()

# Get summary of all collections
query = """
SELECT
  collection_id,
  COUNT(DISTINCT PatientID) as patients,
  COUNT(DISTINCT SeriesInstanceUID) as series,
  COUNT(*) as instances
FROM index
GROUP BY collection_id
ORDER BY patients DESC
"""

collections_summary = client.sql_query(query)
print(collections_summary)
```

**Example output:**
```
       collection_id  patients  series  instances
0     tcga_luad        515      2847     523891
1     nlst             2452     5104     1832419
...
```

### 2. Querying Metadata with SQL

Query the IDC mini-index using SQL to find specific datasets:

```python
from idc_index import IDCClient

client = IDCClient()

# Find breast cancer MRI scans
query = """
SELECT
  collection_id,
  PatientID,
  SeriesInstanceUID,
  Modality,
  SeriesDescription,
  license_short_name
FROM index
WHERE cancer_type = 'Breast'
  AND Modality = 'MR'
  AND BodyPartExamined LIKE '%BREAST%'
LIMIT 20
"""

results = client.sql_query(query)

# Access results as pandas DataFrame
for idx, row in results.iterrows():
    print(f"Patient: {row['PatientID']}, Series: {row['SeriesInstanceUID']}")
```

**Available metadata fields:**
- Identifiers: collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID
- Imaging: Modality, BodyPartExamined, Manufacturer, ManufacturerModelName
- Clinical: PatientAge, PatientSex, StudyDate, SeriesDate
- Descriptions: StudyDescription, SeriesDescription
- Licensing: license_short_name, license_long_name, license_url
- Curated: cancer_type (manually annotated field)

### 3. Downloading DICOM Files

Download imaging data efficiently from IDC's cloud storage:

**Download entire collection:**
```python
from idc_index import IDCClient

client = IDCClient()

# Download small collection (RIDER Pilot ~1GB)
client.download_from_selection(
    collection_id="rider_pilot",
    downloadDir="./data/rider"
)
```

**Download specific series:**
```python
# First, query for series UIDs
query = """
SELECT SeriesInstanceUID
FROM index
WHERE Modality = 'CT'
  AND BodyPartExamined = 'LUNG'
  AND collection_id = 'nlst'
LIMIT 5
"""

series_df = client.sql_query(query)

# Download only those series
client.download_from_selection(
    seriesInstanceUID=list(series_df['SeriesInstanceUID'].values),
    downloadDir="./data/lung_ct"
)
```

**Custom directory structure:**
```python
# Organize downloads by patient and modality
client.download_from_selection(
    collection_id="tcga_luad",
    downloadDir="./data/tcga",
    dirTemplate="%collection_id/%PatientID/%Modality_%SeriesInstanceUID"
)

# Results in: ./data/tcga/tcga_luad/TCGA-05-4244/CT_1.2.840.../
```

### 4. Visualizing Medical Images

View DICOM data in browser without downloading:

```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

# View single series
viewer_url = client.get_viewer_URL(seriesInstanceUID="1.3.6.1.4.1...")
webbrowser.open(viewer_url)

# View all series in a study (useful for multi-series exams like MRI protocols)
viewer_url = client.get_viewer_URL(studyInstanceUID="1.3.6.1.4.1...")
webbrowser.open(viewer_url)
```

The method automatically selects OHIF v3 for radiology or SLIM for slide microscopy. Viewing by study is useful when a DICOM Study contains multiple Series (e.g., T1, T2, DWI sequences from a single MRI session).

See `references/idc_portal_guide.md` for additional visualization options.

### 5. Understanding and Checking Licenses

Check data licensing before use (critical for commercial applications):

```python
from idc_index import IDCClient

client = IDCClient()

# Check licenses for all collections
query = """
SELECT DISTINCT
  collection_id,
  license_short_name,
  license_long_name,
  license_url,
  COUNT(DISTINCT SeriesInstanceUID) as series_count
FROM index
GROUP BY collection_id, license_short_name, license_long_name, license_url
ORDER BY collection_id
"""

licenses = client.sql_query(query)
print(licenses)
```

**License types in IDC:**
- **CC-BY-4.0** (>95% of data) - Allows commercial use with attribution
- **CC-BY-NC-4.0** - Non-commercial use only, requires attribution

**Important:** Always check the license before using IDC data in publications or commercial applications. Each DICOM file is tagged with its specific license in metadata.

### 6. Batch Processing and Filtering

Process large datasets efficiently with filtering:

```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Find all lung CT scans from GE scanners
query = """
SELECT
  SeriesInstanceUID,
  PatientID,
  collection_id,
  ManufacturerModelName
FROM index
WHERE Modality = 'CT'
  AND BodyPartExamined = 'LUNG'
  AND Manufacturer = 'GE MEDICAL SYSTEMS'
  AND license_short_name = 'CC-BY'
LIMIT 100
"""

results = client.sql_query(query)

# Save manifest for later
results.to_csv('lung_ct_manifest.csv', index=False)

# Download in batches to avoid timeout
batch_size = 10
for i in range(0, len(results), batch_size):
    batch = results.iloc[i:i+batch_size]
    client.download_from_selection(
        seriesInstanceUID=list(batch['SeriesInstanceUID'].values),
        downloadDir=f"./data/batch_{i//batch_size}"
    )
```

### 7. Advanced Queries with BigQuery

For queries requiring full DICOM metadata, complex JOINs, or clinical data tables, use Google BigQuery. Requires GCP account with billing enabled.

**Quick reference:**
- Dataset: `bigquery-public-data.idc_current.*`
- Main table: `dicom_all` (combined metadata)
- Full metadata: `dicom_metadata` (all DICOM tags)

See `references/bigquery_guide.md` for setup, table schemas, query patterns, and cost optimization.

### 8. Tool Selection Guide

| Task | Tool | Reference |
|------|------|-----------|
| Programmatic queries & downloads | `idc-index` | This document |
| Interactive exploration | IDC Portal | `references/idc_portal_guide.md` |
| Complex metadata queries | BigQuery | `references/bigquery_guide.md` |
| 3D visualization & analysis | SlicerIDCBrowser | `references/idc_portal_guide.md` |

**Default choice:** Use `idc-index` for most tasks (no auth, easy API, batch downloads).

### 9. Integration with Analysis Pipelines

Integrate IDC data into imaging analysis workflows:

**Read downloaded DICOM files:**
```python
import pydicom
import os

# Read DICOM files from downloaded series
series_dir = "./data/rider/rider_pilot/RIDER-1007893286/CT_1.3.6.1..."

dicom_files = [os.path.join(series_dir, f) for f in os.listdir(series_dir)
               if f.endswith('.dcm')]

# Load first image
ds = pydicom.dcmread(dicom_files[0])
print(f"Patient ID: {ds.PatientID}")
print(f"Modality: {ds.Modality}")
print(f"Image shape: {ds.pixel_array.shape}")
```

**Build 3D volume from CT series:**
```python
import pydicom
import numpy as np
from pathlib import Path

def load_ct_series(series_path):
    """Load CT series as 3D numpy array"""
    files = sorted(Path(series_path).glob('*.dcm'))
    slices = [pydicom.dcmread(str(f)) for f in files]

    # Sort by slice location
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    # Stack into 3D array
    volume = np.stack([s.pixel_array for s in slices])

    return volume, slices[0]  # Return volume and first slice for metadata

volume, metadata = load_ct_series("./data/lung_ct/series_dir")
print(f"Volume shape: {volume.shape}")  # (z, y, x)
```

**Integrate with SimpleITK:**
```python
import SimpleITK as sitk
from pathlib import Path

# Read DICOM series
series_path = "./data/ct_series"
reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames(series_path)
reader.SetFileNames(dicom_names)
image = reader.Execute()

# Apply processing
smoothed = sitk.CurvatureFlow(image1=image, timeStep=0.125, numberOfIterations=5)

# Save as NIfTI
sitk.WriteImage(smoothed, "processed_volume.nii.gz")
```

## Common Use Cases

### Use Case 1: Find and Download Lung CT Scans for Deep Learning

**Objective:** Build training dataset of lung CT scans from NLST collection

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# 1. Query for lung CT scans with specific criteria
query = """
SELECT
  PatientID,
  SeriesInstanceUID,
  SeriesDescription
FROM index
WHERE collection_id = 'nlst'
  AND Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
  AND license_short_name = 'CC-BY'
ORDER BY PatientID
LIMIT 100
"""

results = client.sql_query(query)
print(f"Found {len(results)} series from {results['PatientID'].nunique()} patients")

# 2. Download data organized by patient
client.download_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID'].values),
    downloadDir="./training_data",
    dirTemplate="%collection_id/%PatientID/%SeriesInstanceUID"
)

# 3. Save manifest for reproducibility
results.to_csv('training_manifest.csv', index=False)
```

### Use Case 2: Query Brain MRI by Manufacturer for Quality Study

**Objective:** Compare image quality across different MRI scanner manufacturers

**Steps:**
```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Query for brain MRI grouped by manufacturer
query = """
SELECT
  Manufacturer,
  ManufacturerModelName,
  COUNT(DISTINCT SeriesInstanceUID) as num_series,
  COUNT(DISTINCT PatientID) as num_patients
FROM index
WHERE Modality = 'MR'
  AND BodyPartExamined LIKE '%BRAIN%'
GROUP BY Manufacturer, ManufacturerModelName
HAVING num_series >= 10
ORDER BY num_series DESC
"""

manufacturers = client.sql_query(query)
print(manufacturers)

# Download sample from each manufacturer for comparison
for _, row in manufacturers.head(3).iterrows():
    mfr = row['Manufacturer']
    model = row['ManufacturerModelName']

    query = f"""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Manufacturer = '{mfr}'
      AND ManufacturerModelName = '{model}'
      AND Modality = 'MR'
      AND BodyPartExamined LIKE '%BRAIN%'
    LIMIT 5
    """

    series = client.sql_query(query)
    client.download_from_selection(
        seriesInstanceUID=list(series['SeriesInstanceUID'].values),
        downloadDir=f"./quality_study/{mfr.replace(' ', '_')}"
    )
```

### Use Case 3: Visualize Series Without Downloading

**Objective:** Preview imaging data before committing to download

```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

series_list = client.sql_query("""
    SELECT SeriesInstanceUID, PatientID, SeriesDescription
    FROM index
    WHERE collection_id = 'qin-headneck' AND Modality = 'PT'
    LIMIT 10
""")

# Preview each in browser
for _, row in series_list.iterrows():
    viewer_url = client.get_viewer_URL(seriesInstanceUID=row['SeriesInstanceUID'])
    print(f"Patient {row['PatientID']}: {row['SeriesDescription']}")
    print(f"  View at: {viewer_url}")
    # webbrowser.open(viewer_url)  # Uncomment to open automatically
```

See `references/idc_portal_guide.md` for additional visualization options.

### Use Case 4: License-Aware Batch Download for Commercial Use

**Objective:** Download only CC-BY licensed data suitable for commercial applications

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# Query ONLY for CC-BY licensed data
query = """
SELECT
  SeriesInstanceUID,
  collection_id,
  PatientID,
  Modality
FROM index
WHERE license_short_name = 'CC-BY'
  AND Modality IN ('CT', 'MR')
  AND BodyPartExamined IN ('CHEST', 'BRAIN', 'ABDOMEN')
LIMIT 200
"""

cc_by_data = client.sql_query(query)

print(f"Found {len(cc_by_data)} CC-BY licensed series")
print(f"Collections: {cc_by_data['collection_id'].unique()}")

# Download with license verification
client.download_from_selection(
    seriesInstanceUID=list(cc_by_data['SeriesInstanceUID'].values),
    downloadDir="./commercial_dataset",
    dirTemplate="%collection_id/%Modality/%PatientID/%SeriesInstanceUID"
)

# Save license information
cc_by_data.to_csv('commercial_dataset_manifest_CC-BY_ONLY.csv', index=False)
```

## Best Practices

- **Check licenses before use** - Always query the `license_short_name` field and respect licensing terms (CC-BY vs CC-NC)
- **Start with small queries** - Use `LIMIT` clause when exploring to avoid long downloads and understand data structure
- **Use mini-index for simple queries** - Only use BigQuery when you need comprehensive metadata or complex JOINs
- **Validate Series UIDs** - DICOM UIDs follow format `1.2.840.xxxxx...` - validate before attempting downloads
- **Organize downloads with dirTemplate** - Use meaningful directory structures like `%collection_id/%PatientID/%Modality`
- **Cache query results** - Save DataFrames to CSV files to avoid re-querying and ensure reproducibility
- **Handle network errors** - Implement retry logic for large downloads that may timeout
- **Estimate size first** - Check collection size before downloading - some collections are 100s of GBs
- **Save manifests** - Always save query results with Series UIDs for reproducibility and data provenance
- **Read documentation** - IDC data structure and metadata fields are documented at https://learn.canceridc.dev/

## Troubleshooting

**Issue: `ModuleNotFoundError: No module named 'idc_index'`**
- **Cause:** idc-index package not installed
- **Solution:** Install with `pip install --upgrade idc-index`

**Issue: Download fails with connection timeout**
- **Cause:** Network instability or large download size
- **Solution:**
  - Download smaller batches (e.g., 10-20 series at a time)
  - Check network connection
  - Use `dirTemplate` to organize downloads by batch
  - Implement retry logic with delays

**Issue: `BigQuery quota exceeded` or billing errors**
- **Cause:** BigQuery requires billing-enabled GCP project
- **Solution:** Use idc-index mini-index for simple queries (no billing required), or see `references/bigquery_guide.md` for cost optimization tips

**Issue: Series UID not found or no data returned**
- **Cause:** Typo in UID, data not in current IDC version, or wrong field name
- **Solution:**
  - Verify UID format: should start with `1.2.840.` or similar
  - Check if data is in current IDC version (some old data may be deprecated)
  - Use `LIMIT 5` to test query first
  - Check field names against metadata schema documentation

**Issue: Downloaded DICOM files won't open**
- **Cause:** Corrupted download or incompatible viewer
- **Solution:**
  - Verify file integrity (check file sizes)
  - Use pydicom to validate: `pydicom.dcmread(file, force=True)`
  - Try different DICOM viewer (3D Slicer, Horos, RadiAnt)
  - Re-download the series

## Common SQL Query Patterns

Use `client.sql_query()` with these patterns for common search tasks:

### Search by cancer type
```python
client.sql_query("""
    SELECT collection_id, PatientID, SeriesInstanceUID, Modality, SeriesDescription
    FROM index
    WHERE cancer_type = 'Breast' AND Modality = 'MR'
    LIMIT 100
""")
```

### Search by modality and body part
```python
client.sql_query("""
    SELECT collection_id, PatientID, SeriesInstanceUID, BodyPartExamined
    FROM index
    WHERE Modality = 'CT' AND BodyPartExamined LIKE '%LUNG%'
    LIMIT 100
""")
```

### Get collections summary
```python
client.sql_query("""
    SELECT collection_id,
           COUNT(DISTINCT PatientID) as num_patients,
           COUNT(DISTINCT SeriesInstanceUID) as num_series,
           license_short_name
    FROM index
    GROUP BY collection_id, license_short_name
    ORDER BY num_patients DESC
""")
```

### Check licenses for a collection
```python
client.sql_query("""
    SELECT DISTINCT collection_id, license_short_name, license_url
    FROM index
    WHERE collection_id = 'tcga_luad'
""")
```

### Estimate download size
```python
# Use get_series_size() for individual series
size_mb = client.get_series_size(seriesInstanceUID="1.3.6.1.4.1...")

# Or query for aggregate size across series
client.sql_query("""
    SELECT collection_id, SUM(series_size_MB) as total_mb
    FROM index
    WHERE collection_id = 'rider_pilot'
    GROUP BY collection_id
""")
```

## Resources

### Reference Documentation

- **idc_index_api.md** - Complete idc-index Python API reference with all methods and parameters
- **bigquery_guide.md** - Advanced BigQuery usage guide for complex metadata queries
- **idc_portal_guide.md** - IDC Portal, visualization options, and SlicerIDCBrowser
- **metadata_schema.md** - IDC data hierarchy and metadata field documentation

### External Links

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **Documentation**: https://learn.canceridc.dev/
- **Tutorials**: https://github.com/ImagingDataCommons/IDC-Tutorials
- **User Forum**: https://discourse.canceridc.dev/
- **idc-index GitHub**: https://github.com/ImagingDataCommons/idc-index
- **Citation**: Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." RadioGraphics 43.12 (2023). https://doi.org/10.1148/rg.230180
