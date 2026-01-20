# idc-index Python Package API Reference

## Installation

```bash
pip install --upgrade idc-index
```

## IDCClient Class

The main interface for working with IDC data.

### Initialization

```python
from idc_index import IDCClient

client = IDCClient()
```

No authentication required. The client wraps a mini-index of IDC data and the s5cmd download tool.

## Core Methods

### sql_query()

Query the IDC mini-index using SQL.

```python
query = """
SELECT 
  collection_id,
  Modality,
  COUNT(*) as count
FROM index
WHERE BodyPartExamined = 'LUNG'
GROUP BY collection_id, Modality
"""

results_df = client.sql_query(query)
```

**Returns:** pandas DataFrame with query results

**Available fields in mini-index:**
- collection_id
- PatientID
- StudyInstanceUID
- SeriesInstanceUID
- SOPInstanceUID
- Modality
- BodyPartExamined  
- StudyDescription
- SeriesDescription
- Manufacturer
- ManufacturerModelName
- SoftwareVersions
- PatientAge
- PatientSex
- StudyDate
- SeriesDate
- license_short_name
- license_long_name
- license_url
- cancer_type (curated field)

### download_from_selection()

Download DICOM files based on selection criteria.

```python
# Download by collection
client.download_from_selection(
    collection_id="rider_pilot",
    downloadDir="./data"
)

# Download by series UIDs
client.download_from_selection(
    seriesInstanceUID=["1.3.6.1.4.1...", "1.3.6.1.4.1..."],
    downloadDir="./data"
)

# Download by patient
client.download_from_selection(
    collection_id="tcga_luad",
    patientId=["TCGA-05-4244", "TCGA-05-4249"],
    downloadDir="./data"
)

# Custom directory hierarchy
client.download_from_selection(
    collection_id="rider_pilot",
    downloadDir="./data",
    dirTemplate="%collection_id/%PatientID/%Modality"
)
```

**Parameters:**
- `collection_id` (str or list): Filter by collection(s)
- `patientId` (str or list): Filter by patient ID(s)  
- `studyInstanceUID` (str or list): Filter by study UID(s)
- `seriesInstanceUID` (str or list): Filter by series UID(s)
- `downloadDir` (str): Target directory for downloads
- `dirTemplate` (str, optional): Custom directory hierarchy template
  - Default: `%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`
  - Available variables: %collection_id, %PatientID, %StudyInstanceUID, %Modality, %SeriesInstanceUID
  - Use "" for flat structure

**Directory templates:**
- Use % prefix for metadata variables
- Separators: / (subdirectory), - (hyphen), _ (underscore)
- Empty string ("") downloads all to root

### download_from_manifest()

Download files using a manifest (CSV file with download URLs).

```python
client.download_from_manifest(
    manifestFile="manifest.csv",
    downloadDir="./data"
)
```

### get_viewer_URL()

Get viewer URL for a series. Automatically selects appropriate viewer (OHIF for radiology, SLIM for pathology).

```python
# Auto-select viewer based on modality
url = client.get_viewer_URL(seriesInstanceUID="1.3.6.1.4.1...")

# Force specific viewer
url = client.get_viewer_URL(
    seriesInstanceUID="1.3.6.1.4.1...",
    viewer_selector='slim'  # 'ohif_v2', 'ohif_v3', or 'slim'
)

# View by study
url = client.get_viewer_URL(studyInstanceUID="1.3.6.1.4.1...")
```

**Parameters:**
- `seriesInstanceUID` (str): Series to view (StudyInstanceUID auto-resolved from index)
- `studyInstanceUID` (str): Alternative - view entire study
- `viewer_selector` (str, optional): Force viewer type ('ohif_v2', 'ohif_v3', 'slim')

**Returns:** Viewer URL string

### get_idc_version() (static)

Get the current IDC data version.

```python
version = IDCClient.get_idc_version()
print(f"IDC version: {version}")
```

### get_series_size()

Get cumulative size of DICOM instances in a series (in MB).

```python
size_mb = client.get_series_size(seriesInstanceUID="1.3.6.1.4.1...")
print(f"Series size: {size_mb:.2f} MB")
```

## Command Line Interface

idc-index also provides a CLI:

```bash
# Download collection
idc download collection_id=rider_pilot

# Download with custom output
idc download collection_id=rider_pilot --downloadDir ./mydata

# Query and display
idc query "SELECT * FROM index WHERE Modality='CT' LIMIT 5"
```

## Common Usage Patterns

### Pattern 1: Explore then download

```python
from idc_index import IDCClient

client = IDCClient()

# First, explore what's available
query = """
SELECT 
  collection_id,
  COUNT(DISTINCT PatientID) as patients,
  COUNT(DISTINCT SeriesInstanceUID) as series,
  license_short_name
FROM index
WHERE Modality = 'MR'
  AND BodyPartExamined LIKE '%BRAIN%'
GROUP BY collection_id, license_short_name
"""

available = client.sql_query(query)
print(available)

# Then download selected collections
for collection in available['collection_id'].values[:3]:
    client.download_from_selection(
        collection_id=collection,
        downloadDir=f"./data/{collection}"
    )
```

### Pattern 2: Filter and download specific series

```python
# Query for specific criteria
query = """
SELECT SeriesInstanceUID, collection_id
FROM index  
WHERE Modality = 'CT'
  AND cancer_type = 'Lung'
  AND ManufacturerModelName LIKE '%GE%'
LIMIT 50
"""

series_df = client.sql_query(query)

# Download only these series
client.download_from_selection(
    seriesInstanceUID=list(series_df['SeriesInstanceUID'].values),
    downloadDir="./ct_lung_ge"
)
```

### Pattern 3: License-aware downloads

```python
# Only download CC-BY licensed data
query = """
SELECT SeriesInstanceUID
FROM index
WHERE license_short_name = 'CC-BY'
  AND Modality = 'MR'
LIMIT 100
"""

cc_by_series = client.sql_query(query)

client.download_from_selection(
    seriesInstanceUID=list(cc_by_series['SeriesInstanceUID'].values),
    downloadDir="./cc_by_data"
)
```

## Data Organization

Downloaded files follow DICOM hierarchy:
- Collection → Patient → Study → Series → Instances

Default structure:
```
downloadDir/
  collection_id/
    PatientID/
      StudyInstanceUID/
        Modality_SeriesInstanceUID/
          instance1.dcm
          instance2.dcm
```

## Important Notes

- No Google Cloud account required
- No AWS credentials needed
- All IDC data is in public cloud buckets
- Downloads use s5cmd for efficiency
- Mini-index contains core metadata; use BigQuery for comprehensive queries
- All data is in DICOM format

## Troubleshooting

**Issue: Downloads fail with connection errors**
- Cause: Network issues or s5cmd problems
- Solution: Check network, retry download, or download in smaller batches

**Issue: SQL query syntax errors**
- Cause: Incorrect SQL syntax or field names
- Solution: Verify field names against mini-index schema, test with LIMIT 5 first

**Issue: Empty results from query**
- Cause: No data matches filters, or incorrect field values
- Solution: Broaden query criteria, check valid values for fields (e.g., Modality = 'CT' not 'ct')
