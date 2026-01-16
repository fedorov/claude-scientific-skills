# BigQuery Guide for IDC

## Prerequisites

**Important:** BigQuery requires:
1. Google account
2. Google Cloud project with billing enabled
3. This is a barrier for beginners - recommend `idc-index` first

For most use cases, `idc-index` is sufficient and requires no setup.

## When to Use BigQuery

Use BigQuery when you need:
- Complex metadata queries beyond mini-index capabilities
- Full DICOM metadata (all tags)
- Clinical data tables
- Advanced joins across multiple tables
- Large-scale data analysis

## Accessing IDC in BigQuery

### Dataset Structure

All IDC tables are in the `bigquery-public-data` project.

**Current version (recommended for exploration):**
- `bigquery-public-data.idc_current.*`
- `bigquery-public-data.idc_current_clinical.*`

**Versioned datasets (recommended for reproducibility):**
- `bigquery-public-data.idc_v16.*` (example for v16)
- `bigquery-public-data.idc_v16_clinical.*`

Always use versioned datasets for reproducible research!

## Key Tables

### dicom_all
Primary table combining DICOM metadata with auxiliary metadata.

```sql
SELECT 
  collection_id,
  PatientID,
  StudyInstanceUID, 
  SeriesInstanceUID,
  Modality,
  BodyPartExamined,
  SeriesDescription,
  gcs_url,
  license_short_name
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
LIMIT 10
```

### dicom_metadata
Complete DICOM metadata for all instances.

Contains ALL DICOM tags, including sequences and complex attributes.

```sql
SELECT 
  SOPInstanceUID,
  SeriesInstanceUID,
  Manufacturer,
  ManufacturerModelName,
  KVP,
  Exposure
FROM `bigquery-public-data.idc_current.dicom_metadata`
WHERE Modality = 'CT'
LIMIT 10
```

### auxiliary_metadata
Non-DICOM metadata about collections, versions, licenses, URLs.

```sql
SELECT
  collection_id,
  SOPInstanceUID,
  gcs_url,
  aws_url,
  license_short_name,
  license_url,
  instance_size
FROM `bigquery-public-data.idc_current.auxiliary_metadata`
WHERE collection_id = 'tcga_luad'
LIMIT 10
```

### Derived Tables

**segmentations** - DICOM Segmentation objects
```sql
SELECT *
FROM `bigquery-public-data.idc_current.segmentations`
LIMIT 10
```

**measurement_groups** - SR TID1500 measurement groups
**qualitative_measurements** - Coded evaluations
**quantitative_measurements** - Numeric measurements

### Collection Metadata

**original_collections_metadata** - Collection-level descriptions

```sql
SELECT 
  collection_id,
  CancerType,
  Subjects,
  ImageType,
  Description,
  DOI,
  license_short_name
FROM `bigquery-public-data.idc_current.original_collections_metadata`
WHERE CancerType LIKE '%Lung%'
```

## Common Query Patterns

### Find Collections by Criteria

```sql
SELECT 
  collection_id,
  COUNT(DISTINCT PatientID) as patient_count,
  COUNT(DISTINCT SeriesInstanceUID) as series_count,
  ARRAY_AGG(DISTINCT Modality) as modalities
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE BodyPartExamined LIKE '%BRAIN%'
GROUP BY collection_id
HAVING patient_count > 50
ORDER BY patient_count DESC
```

### Get Download URLs

```sql
SELECT
  SeriesInstanceUID,
  gcs_url
FROM `bigquery-public-data.idc_current.dicom_all`  
WHERE collection_id = 'rider_pilot'
  AND Modality = 'MR'
```

### Find Studies with Multiple Modalities

```sql
SELECT
  StudyInstanceUID,
  ARRAY_AGG(DISTINCT Modality) as modalities,
  COUNT(DISTINCT SeriesInstanceUID) as series_count
FROM `bigquery-public-data.idc_current.dicom_all`
GROUP BY StudyInstanceUID
HAVING ARRAY_LENGTH(ARRAY_AGG(DISTINCT Modality)) > 1
LIMIT 100
```

### License Filtering

```sql
SELECT
  collection_id,
  license_short_name,
  COUNT(*) as instance_count
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE license_short_name = 'CC-BY'
GROUP BY collection_id, license_short_name
```

### Find Segmentations with Source Images

```sql
SELECT
  seg.collection_id,
  seg.SeriesInstanceUID as seg_series,
  seg.segmentedPropertyTypeCodeMeaning,
  src.SeriesInstanceUID as source_series,
  src.Modality as source_modality
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.dicom_all` src
  ON seg.ReferencedSeriesInstanceUID = src.SeriesInstanceUID
WHERE seg.collection_id = 'qin_prostate_repeatability'
LIMIT 10
```

## Using Query Results with idc-index

Combine BigQuery queries with idc-index for downloads:

```python
from google.cloud import bigquery
from idc_index import IDCClient

# Query with BigQuery
bq_client = bigquery.Client()
query = """
SELECT SeriesInstanceUID
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE collection_id = 'tcga_luad'
  AND Modality = 'CT'
LIMIT 100
"""

df = bq_client.query(query).to_dataframe()

# Download with idc-index
idc_client = IDCClient()
idc_client.download_from_selection(
    seriesInstanceUID=list(df['SeriesInstanceUID'].values),
    downloadDir="./tcga_luad_ct"
)
```

## Cost Considerations

BigQuery charges for:
1. Data processed by queries (not data returned)
2. Storage (minimal for querying public datasets)

**Cost-saving tips:**
- Use `LIMIT` during development
- Select only needed columns
- Use table previews in BQ console (free)
- Filter early in queries
- Use `dicom_all` instead of `dicom_metadata` when possible (smaller table)

Typical query costs: $0.05-$1.00 for moderate queries

## Views vs Tables

IDC provides both views and materialized tables:
- `table_name_view` - BQ view (runs query each time)
- `table_name` - Materialized table (faster, lower cost)

Always use materialized tables unless you need to see the query logic.

## Clinical Data

Clinical data is in separate datasets:
```sql
SELECT *
FROM `bigquery-public-data.idc_current_clinical.*`
```

Not all collections have clinical data. Started in IDC v11.

## Important Notes

- Tables are read-only (public dataset)
- Schema changes between IDC versions
- Use versioned datasets for reproducibility
- Some DICOM sequences >15 levels deep are not extracted
- Very large sequences (>1MB) may be truncated
- Always check data license before use

## Query Optimization Tips

**Cost Optimization:**
- Use `SELECT` only the columns you need (not `SELECT *`)
- Filter early with `WHERE` clauses to reduce data scanned
- Use `LIMIT` when testing queries
- Check query cost before running: `client.query(query).total_bytes_processed`
- Use clustering and partitioning features when available

**Performance Optimization:**
- Use materialized tables instead of views
- Avoid complex JOIN operations when possible
- Pre-filter data before JOINs
- Use approximate aggregation functions when exact counts aren't needed

## Common Errors

**Issue: Billing must be enabled**
- Cause: BigQuery requires a billing-enabled GCP project
- Solution: Enable billing in Google Cloud Console or use idc-index mini-index instead

**Issue: Query exceeds resource limits**
- Cause: Query scans too much data or is too complex
- Solution: Add more specific WHERE filters, use LIMIT, break into smaller queries

**Issue: Column not found**
- Cause: Field name typo or not in selected table
- Solution: Check table schema first with `INFORMATION_SCHEMA.COLUMNS`

**Issue: Permission denied**
- Cause: Not authenticated to Google Cloud
- Solution: Run `gcloud auth application-default login` or set GOOGLE_APPLICATION_CREDENTIALS

## Cost Estimation

BigQuery charges for data scanned:
- First 1 TB per month: Free
- After that: $5 per TB scanned
- Storage: $0.02 per GB per month (unlikely to apply for read-only access)

**Example costs:**
- Simple query scanning 10 GB: Free (under 1 TB monthly limit)
- Complex query scanning 500 GB: Free (under 1 TB monthly limit)
- Multiple queries totaling 2 TB in a month: ~$5

**Tip:** Most users stay within free tier limits with careful query design.
