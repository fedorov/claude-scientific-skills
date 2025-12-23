# IDC Metadata Schema and Organization

## Data Model Hierarchy

IDC organizes data following DICOM hierarchy:

```
Collection
└── Patient (Case)
    └── Study
        └── Series  
            └── Instance (DICOM file)
```

### Collection
Top-level grouping of related imaging data.
- Example: TCGA-LUAD, RIDER Pilot, QIN Prostate Repeatability
- Each collection has associated metadata (DOI, description, license)

### Patient (Case)
Individual subject in a study.
- Identified by PatientID (submitter-assigned)
- IDC also assigns idc_case_id (UUID) for global uniqueness

### Study
Single imaging study/exam for a patient.
- Identified by StudyInstanceUID (DICOM UID)
- May contain multiple series with different modalities

### Series
Set of related images acquired as a unit.
- Identified by SeriesInstanceUID (DICOM UID)
- Homogeneous modality within series
- Core unit for most IDC operations

### Instance
Individual DICOM file.
- Identified by SOPInstanceUID (DICOM UID)
- Actual image or derived object

## Key Metadata Fields

### Identifiers

**Collection Level:**
- `collection_id` - IDC collection identifier
- `tcia_api_collection_id` - TCIA API identifier (when applicable)

**Patient Level:**
- `PatientID` - Submitter-assigned patient identifier
- `idc_case_id` - IDC-generated UUID (globally unique)

**Study Level:**
- `StudyInstanceUID` - DICOM study UID

**Series Level:**
- `SeriesInstanceUID` - DICOM series UID
- `series_uuid` - IDC-assigned version identifier

**Instance Level:**
- `SOPInstanceUID` - DICOM instance UID
- `instance_uuid` - IDC-assigned version identifier

### Clinical/Descriptive

- `PatientAge` - Age at study time
- `PatientSex` - M/F/O
- `BodyPartExamined` - Anatomical region
- `StudyDescription` - Study-level description
- `SeriesDescription` - Series-level description

### Technical

**Image Acquisition:**
- `Modality` - CT, MR, PT, DX, MG, SM, SR, SEG, etc.
- `Manufacturer` - Equipment manufacturer
- `ManufacturerModelName` - Specific device model
- `SoftwareVersions` - Software version

**CT-specific:**
- `KVP` - Peak kilovoltage
- `Exposure` - Exposure in mAs
- `SliceThickness` - Slice thickness in mm
- `ConvolutionKernel` - Reconstruction kernel

**MR-specific:**
- `MagneticFieldStrength` - Field strength in Tesla
- `EchoTime` - TE in ms
- `RepetitionTime` - TR in ms
- `FlipAngle` - Flip angle in degrees

**Image Properties:**
- `Rows` - Image height in pixels
- `Columns` - Image width in pixels
- `NumberOfFrames` - Number of frames (for multi-frame)

### Temporal

- `StudyDate` - Date of study (YYYYMMDD)
- `StudyTime` - Time of study (HHMMSS)
- `SeriesDate` - Date of series
- `SeriesTime` - Time of series
- `AcquisitionDate` - Acquisition date
- `ContentDate` - Content creation date

### Licensing and Access

- `license_short_name` - CC-BY, CC-NC, etc.
- `license_long_name` - Full license name
- `license_url` - URL to license text
- `access` - "Public" or "Limited"

### Storage and Download

- `gcs_url` - Google Cloud Storage URL
- `aws_url` - Amazon Web Services URL  
- `instance_size` - File size in bytes

### Provenance

- `source_doi` - DOI of source collection/analysis
- `source_url` - URL describing source
- `collection_timestamp` - Last collection update
- `instance_init_idc_version` - First IDC version with instance
- `instance_revised_idc_version` - IDC version of current instance version

## Derived Object Metadata

### DICOM Segmentations

Available in `segmentations` table:

- `segmentedPropertyTypeCodeMeaning` - What was segmented (e.g., "Liver", "Tumor")
- `segmentedPropertyCategoryCodeMeaning` - Category (e.g., "Tissue", "Anatomical Structure")
- `SegmentAlgorithmType` - MANUAL, SEMIAUTOMATIC, AUTOMATIC
- `SegmentAlgorithmName` - Algorithm/tool name
- `ReferencedSeriesInstanceUID` - Source image series

### Structured Reports (SR)

Measurement data extracted into:

**measurement_groups** - TID1500 measurement groups
- `measurementGroupUID` - Group identifier  
- `TrackingIdentifier` - Measurement tracking ID
- `FindingSiteCodeMeaning` - Anatomical location

**quantitative_measurements** - Numeric measurements
- `value` - Measurement value
- `units` - Measurement units
- `ConceptCodeMeaning` - What was measured (e.g., "Volume", "Length")

**qualitative_measurements** - Coded evaluations
- `CodeMeaning` - Evaluation result
- `ConceptCodeMeaning` - What was evaluated

## Curated Fields

IDC provides curated metadata fields:

**cancer_type** (curated)
- Derived from collection metadata
- Values: Lung, Breast, Prostate, Brain, etc.

**Modality** (standardized)
- Cleaned and standardized modality codes

## Metadata Availability

### In idc-index mini-index:
Core fields for filtering and discovery:
- collection_id, PatientID, Study/Series/SOPInstanceUID
- Modality, BodyPartExamined
- Basic descriptors
- License information
- cancer_type (curated)

### In BigQuery dicom_all:
Extended set including:
- All mini-index fields
- Additional clinical data
- Technical parameters
- Storage URLs
- Provenance information

### In BigQuery dicom_metadata:
Complete DICOM metadata:
- ALL DICOM tags
- Sequence attributes (up to 15 levels)
- Device-specific parameters
- Complete technical details

## Common Metadata Queries

### Find all modalities in collection:
```python
query = """
SELECT DISTINCT Modality
FROM index
WHERE collection_id = 'tcga_luad'
"""
```

### Filter by body part:
```python
query = """
SELECT SeriesInstanceUID
FROM index  
WHERE BodyPartExamined IN ('CHEST', 'LUNG')
```

### Filter by acquisition parameters (BigQuery):
```sql
SELECT SeriesInstanceUID
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE Modality = 'CT'
  AND SliceThickness <= 2.5
  AND ConvolutionKernel LIKE '%BONE%'
```

### Find multimodality studies (BigQuery):
```sql
SELECT 
  StudyInstanceUID,
  ARRAY_AGG(DISTINCT Modality) as modalities
FROM `bigquery-public-data.idc_current.dicom_all`
GROUP BY StudyInstanceUID
HAVING COUNT(DISTINCT Modality) > 1
```

## Important Notes

- Not all fields are populated for all instances
- Field availability depends on modality and acquisition
- DICOM standard allows optional fields
- Some collections have richer metadata than others
- Always check for NULL values in queries
- SliceThickness, KVP, etc. may not be present in all CT scans
- Clinical fields (PatientAge, PatientSex) may be missing or anonymized
