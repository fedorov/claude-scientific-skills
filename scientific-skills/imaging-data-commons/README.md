# Imaging Data Commons

A Claude skill for working with the National Cancer Institute Imaging Data Commons (IDC).

## Description

Access NCI Imaging Data Commons for public cancer imaging data in DICOM format. Query by cancer type, modality, or anatomical site; download DICOM series; visualize in browser; check licenses — all using the `idc-index` Python package.

## Installation

```bash
# Core requirement
pip install --upgrade idc-index

# Optional (for data analysis)
pip install pandas numpy pydicom

# Optional (for BigQuery access - requires GCP project with billing)
# pip install google-cloud-bigquery db-dtypes
```

## Core Workflow

```python
from idc_index import IDCClient

client = IDCClient()

# 1. Query metadata
results = client.sql_query("""
    SELECT collection_id, PatientID, SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT' AND BodyPartExamined LIKE '%LUNG%'
    LIMIT 10
""")

# 2. Download DICOM files
client.download_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID']),
    downloadDir="./data"
)

# 3. Visualize in browser
import webbrowser
url = client.get_viewer_URL(seriesInstanceUID=results.iloc[0]['SeriesInstanceUID'])
webbrowser.open(url)
```

## What This Skill Provides

### Access Methods

| Method | Auth Required | Best For |
|--------|---------------|----------|
| `idc-index` | No | Most queries and downloads (recommended) |
| IDC Portal | No | Interactive exploration |
| BigQuery | Yes (GCP) | Complex metadata queries |

### Key Capabilities

1. **Data Discovery** - Find cancer imaging datasets by type, modality, body part
2. **SQL Querying** - Search using SQL against IDC mini-index
3. **Data Download** - Efficiently download DICOM files from public cloud storage
4. **Visualization** - View images in browser via `get_viewer_URL()` (auto-selects OHIF or SLIM)
5. **License Checking** - Query CC-BY vs CC-NC licensing before use

## Example Prompts

- "Find all breast cancer MRI scans in IDC"
- "Download lung CT images from the TCGA-LUAD collection"
- "Query IDC for prostate cancer cases with segmentations"
- "Show me what brain MR imaging data is available"
- "Visualize this series from IDC in the browser"

## Structure

```
imaging-data-commons/
├── SKILL.md                  # Main skill documentation with examples
├── README.md                 # This file
├── requirements.txt          # Python dependencies
└── references/               # Detailed reference documentation
    ├── idc_index_api.md      # idc-index API reference
    ├── bigquery_guide.md     # BigQuery usage guide
    ├── idc_portal_guide.md   # Portal and visualization options
    └── metadata_schema.md    # IDC data hierarchy and fields
```

## Resources

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **Documentation**: https://learn.canceridc.dev/
- **Tutorials**: https://github.com/ImagingDataCommons/IDC-Tutorials
- **User Forum**: https://discourse.canceridc.dev/
- **idc-index**: https://github.com/ImagingDataCommons/idc-index

## Citation

If you use IDC data, please cite:

> Fedorov, A., Longabaugh, W. J. R., Pot, D., Clunie, D. A., Pieper, S. D., Gibbs, D. L., Bridge, C., Herrmann, M. D., Homeyer, A., Lewis, R., Aerts, H. J. W., Krishnaswamy, D., Thiriveedhi, V. K., Ciausu, C., Schacherer, D. P., Bontempi, D., Pihl, T., Wagner, U., Farahani, K., Kim, E. & Kikinis, R. National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence. RadioGraphics (2023). https://doi.org/10.1148/rg.230180

## License

This skill is provided under the MIT License. IDC data itself has individual licensing (mostly CC-BY, some CC-NC) that must be respected when using the data.

## Contributing

For issues, suggestions, or contributions to this skill, please visit the repository where it's hosted or contact the skill maintainer.
