# IDC Navigator

A Claude skill for working with the National Cancer Institute Imaging Data Commons (IDC).

## Description

Helps users discover, query, visualize, download, and use cancer imaging data from NCI Imaging Data Commons (IDC). Use when users ask to search IDC data, find imaging datasets by cancer type or modality, download DICOM files from IDC, visualize medical images from IDC, query IDC metadata, understand IDC licensing, or work with IDC tools (idc-index, Portal, BigQuery, SlicerIDCBrowser).

## Installation

This skill requires the `idc-index` Python package for basic functionality:

```bash
pip install --upgrade idc-index
```

For advanced BigQuery functionality, you'll need Google Cloud SDK and a project with billing configured.

## What This Skill Provides

### Quick Access Tools

- **idc-index Python package** - Recommended for beginners (no Google Cloud setup required)
- **IDC Portal** - Web-based exploration and visualization
- **BigQuery** - Advanced metadata queries (requires GCP setup)
- **SlicerIDCBrowser** - 3D Slicer extension for visualization

### Key Capabilities

1. **Data Discovery** - Find cancer imaging datasets by type, modality, body part
2. **Metadata Querying** - Search using SQL against IDC mini-index or BigQuery
3. **Data Download** - Efficiently download DICOM files from cloud storage
4. **Visualization** - Generate viewer URLs or use integrated viewers
5. **License Management** - Understand CC-BY vs CC-NC licensing

## Example Usage

Ask Claude questions like:

- "Find all breast cancer MRI scans in IDC"
- "Download lung CT images from the TCGA-LUAD collection"
- "Query IDC for prostate cancer cases with segmentations"
- "Show me what brain MR imaging data is available"
- "Help me visualize this series from IDC"

Claude will automatically use this skill to help you work with IDC data.

## Structure

```
idc-navigator/
├── SKILL.md              # Main skill instructions
└── references/           # Detailed reference documentation
    ├── idc_index_api.md      # idc-index Python API reference
    ├── bigquery_guide.md     # BigQuery usage guide
    └── metadata_schema.md    # IDC metadata organization
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
