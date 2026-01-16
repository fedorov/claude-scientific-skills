---
name: imaging-data-commons
description: Access NCI Imaging Data Commons for cancer imaging (95TB+ DICOM). Query by cancer type/modality, download series, visualize in browser, check licenses via idc-index/BigQuery.
license: Unknown
metadata:
    skill-author: K-Dense Inc.
---

# Imaging Data Commons

## Overview

The National Cancer Institute Imaging Data Commons (IDC) is a cloud-based repository containing over 95TB of publicly available cancer imaging data in DICOM format. IDC aggregates radiology images (CT, MR, PET, etc.), digital pathology (whole slide microscopy), and image-derived data with accompanying clinical metadata from major cancer imaging collections including TCGA, NLST, QIN, and many others.

This skill provides guidance for discovering, querying, downloading, and visualizing cancer imaging datasets from IDC using multiple access methods: the idc-index Python package for beginners, the IDC Portal for web-based exploration, BigQuery for advanced metadata queries, and SlicerIDCBrowser for 3D visualization.

All IDC data is stored in public cloud buckets (AWS and Google Cloud) with no authentication required for access, though some tools like BigQuery require a Google Cloud account with billing configured.

## When to Use This Skill

This skill should be used when:
- Working with publicly available cancer imaging datasets from NCI
- Searching for DICOM medical images by cancer type, modality, or anatomical site
- Downloading radiology (CT, MR, PET, etc.) or pathology (slide microscopy) images for research
- Accessing large-scale imaging datasets with associated clinical metadata
- Querying imaging data by patient demographics, study dates, scanner parameters, or collection
- Understanding data licensing (CC-BY vs CC-NC) before use in research or commercial applications
- Visualizing medical images without installing local DICOM viewer software
- Building imaging analysis pipelines that require curated, standardized cancer imaging data

**Not for:**
- Private/institutional microscopy images (use omero-integration skill)
- Gene expression or molecular data (use geo-database skill)
- Protein structures (use pdb-database or alphafold-database skills)
- General scientific literature searches (use pubmed-database skill)

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

**Helper Scripts:**

This skill includes Python helper scripts in the `scripts/` directory:
- `idc_client.py` - Simplified client class for common query operations
- `idc_download.py` - Download utilities with progress tracking
- `idc_viewer.py` - Visualization URL generation and browser integration

See the "Helper Scripts" section below for usage examples.

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

Generate viewer URLs and visualize DICOM data without downloading:

**Option 1: IDC Portal viewer (no installation required):**
```python
# Construct viewer URL for any series
series_uid = "1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178"
viewer_url = f"https://viewer.imaging.datacommons.cancer.gov/viewer/{series_uid}"

print(f"View in browser: {viewer_url}")
# Open automatically in browser
import webbrowser
webbrowser.open(viewer_url)
```

**Option 2: Using helper script:**
```python
from scripts.idc_viewer import generate_viewer_url, open_in_browser

# Generate URL for specific viewer type
url = generate_viewer_url(series_uid, viewer_type='ohif')  # or 'volview', 'slim'

# Open directly
open_in_browser(url)
```

**Option 3: SlicerIDCBrowser extension:**

For advanced 3D visualization and analysis:
1. Install 3D Slicer (https://www.slicer.org/)
2. Install SlicerIDCBrowser extension via Extension Manager
3. Browse and download data directly within Slicer

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

Use BigQuery for complex metadata queries beyond the mini-index capabilities:

**When to use BigQuery:**
- Need comprehensive metadata not in mini-index (frame-level data, detailed DICOM tags)
- Complex JOIN operations across multiple tables
- Querying segmentations, annotations, or image-derived features
- Large-scale cohort selection with complex criteria

**Setup:**
1. Create Google Cloud account and project
2. Enable BigQuery API and configure billing
3. Access IDC public datasets at `bigquery-public-data.idc_current.*`

**Example BigQuery query:**
```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
  series.SeriesInstanceUID,
  series.Modality,
  series.BodyPartExamined,
  COUNT(DISTINCT instance.SOPInstanceUID) as num_instances
FROM `bigquery-public-data.idc_current.dicom_all` as instance
JOIN `bigquery-public-data.idc_current.dicom_metadata` as series
  ON instance.SeriesInstanceUID = series.SeriesInstanceUID
WHERE series.Modality = 'MR'
  AND series.collection_id = 'tcga_brca'
GROUP BY series.SeriesInstanceUID, series.Modality, series.BodyPartExamined
LIMIT 100
"""

results = client.query(query).to_dataframe()
```

See `references/bigquery_guide.md` for comprehensive BigQuery documentation.

### 8. Tool Selection Guide

Choose the right IDC tool based on your task:

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **idc-index** | Beginners, simple queries, batch downloads | No auth required, easy Python API, free | Limited metadata fields |
| **IDC Portal** | Quick exploration, visualization, manual selection | Web-based, no install, interactive viewers | Manual process, not scriptable |
| **BigQuery** | Complex queries, comprehensive metadata, large cohorts | Full DICOM metadata, powerful SQL | Requires GCP account and billing |
| **SlicerIDCBrowser** | 3D visualization, segmentation, advanced analysis | Full Slicer capabilities, integrated workflow | Requires Slicer installation |

**Recommended workflow:**
1. Start with **IDC Portal** to explore collections and understand data structure
2. Use **idc-index** for programmatic queries and downloads
3. Graduate to **BigQuery** only when you need comprehensive metadata or complex queries
4. Use **SlicerIDCBrowser** for advanced visualization and analysis workflows

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

**Steps:**
```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

# Find interesting cases
query = """
SELECT
  SeriesInstanceUID,
  PatientID,
  SeriesDescription
FROM index
WHERE collection_id = 'qin-headneck'
  AND Modality = 'PT'
LIMIT 10
"""

series_list = client.sql_query(query)

# Preview each in browser
for idx, row in series_list.iterrows():
    series_uid = row['SeriesInstanceUID']
    viewer_url = f"https://viewer.imaging.datacommons.cancer.gov/viewer/{series_uid}"

    print(f"Patient {row['PatientID']}: {row['SeriesDescription']}")
    print(f"  View at: {viewer_url}")

    # Optional: open in browser
    # webbrowser.open(viewer_url)
```

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
- **Solution:**
  - Use idc-index mini-index for simple queries (no billing required)
  - Enable billing in Google Cloud Console
  - Check query cost before running (`client.query(query).total_bytes_processed`)
  - Consider query optimization

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

## Helper Scripts

This skill provides Python helper scripts for common operations. Scripts are located in `scripts/` directory.

### scripts/idc_client.py - Simplified Client Class

Wrapper around idc-index with convenience methods:

```python
from scripts.idc_client import IDCClient

client = IDCClient()

# Search by cancer type
breast_mr = client.search_by_cancer_type('Breast', modality='MR')

# Search by modality
all_pet = client.search_by_modality('PT', body_part='CHEST')

# Get collections summary
summary = client.get_collections_summary()

# Check licenses
licenses = client.check_licenses(collection_id='tcga_luad')
```

### scripts/idc_download.py - Download Utilities

Advanced download functions with progress tracking:

```python
from scripts.idc_download import download_collection, get_download_size_estimate

# Estimate size before downloading
size_gb = get_download_size_estimate(collection_id='rider_pilot')
print(f"Estimated download size: {size_gb:.2f} GB")

# Download with custom options
download_collection(
    collection_id='rider_pilot',
    output_dir='./data',
    dir_template='%PatientID/%Modality'
)
```

### scripts/idc_viewer.py - Visualization Helpers

Generate viewer URLs and launch browsers:

```python
from scripts.idc_viewer import generate_viewer_url, open_in_browser

# Generate URL for specific viewer
url = generate_viewer_url(series_uid, viewer_type='ohif')

# Open in default browser
open_in_browser(url)

# Validate Series UID format
from scripts.idc_viewer import validate_series_uid
if validate_series_uid(series_uid):
    print("Valid UID format")
```

## Resources

### Reference Documentation

- **idc_index_api.md** - Complete idc-index Python API reference with all methods and parameters
- **bigquery_guide.md** - Advanced BigQuery usage guide for complex metadata queries
- **metadata_schema.md** - IDC data hierarchy and metadata field documentation

### External Links

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **Documentation**: https://learn.canceridc.dev/
- **Tutorials**: https://github.com/ImagingDataCommons/IDC-Tutorials
- **User Forum**: https://discourse.canceridc.dev/
- **idc-index GitHub**: https://github.com/ImagingDataCommons/idc-index
- **Citation**: Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." RadioGraphics 43.12 (2023). https://doi.org/10.1148/rg.230180
