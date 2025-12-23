# IDC Navigator Skill - Summary

## What This Skill Does

The IDC Navigator skill helps users work with cancer imaging data from the National Cancer Institute Imaging Data Commons (IDC). It provides guidance on:

1. **Discovering data** - Finding relevant cancer imaging datasets
2. **Querying metadata** - Searching by cancer type, modality, body part, etc.
3. **Downloading data** - Efficiently getting DICOM files
4. **Visualizing images** - Using IDC's web viewers or 3D Slicer
5. **Understanding licenses** - CC-BY vs CC-NC licensing
6. **Tool selection** - Choosing between idc-index, Portal, BigQuery, or SlicerIDCBrowser

## Skill Organization (K-Dense Format)

This skill is organized as a standard folder structure following the K-Dense claude-scientific-skills repository format:

```
idc-navigator/
├── README.md                 # Skill overview and installation
├── SKILL.md                  # Main skill instructions (core file)
├── requirements.txt          # Python dependencies
└── references/               # Detailed reference documentation
    ├── idc_index_api.md         # idc-index Python API reference
    ├── bigquery_guide.md        # BigQuery usage guide
    └── metadata_schema.md       # IDC metadata organization
```

### Key Features of This Organization

1. **Human-readable** - All files are plain text (Markdown, Python)
2. **Standard structure** - Matches the K-Dense scientific-skills format
3. **No packaging** - Direct folder structure, not a .skill zip file
4. **Git-friendly** - Can be versioned and shared via GitHub
5. **README included** - Standard documentation for GitHub/GitLab

## SKILL.md Structure

The main SKILL.md contains:
- YAML frontmatter with name and description
- Tool selection guide (which tool for which task)
- Common workflows with code examples
- Quick reference for licenses
- Links to detailed reference documentation

Key design decisions:
- Emphasizes idc-index for beginners (no Google Cloud setup needed)
- Explains BigQuery is more powerful but requires billing
- Provides concrete code examples users can copy
- Short and focused (~160 lines)

## Reference Documentation

Three detailed reference documents in `references/`:

**idc_index_api.md** (~200 lines)
- Complete API reference for the idc-index Python package
- Installation and setup
- All methods with parameters and examples
- Common usage patterns
- Command-line interface

**bigquery_guide.md** (~180 lines)  
- When and why to use BigQuery
- Prerequisites (Google account, billing)
- Dataset and table structure
- Common query patterns
- Cost considerations
- Integration with idc-index

**metadata_schema.md** (~190 lines)
- IDC data hierarchy (Collection → Patient → Study → Series → Instance)
- Key metadata fields and their meanings
- Modality-specific fields (CT, MR, etc.)
- License and provenance fields
- Common metadata queries

## Usage in Claude

When installed in Claude Code or as an MCP skill, Claude will automatically:

1. **Detect IDC-related queries** based on the description in SKILL.md frontmatter
2. **Load SKILL.md** to understand core workflows and tool selection
3. **Access references/** files as needed for detailed API information
4. **Execute Python code** using idc-index to query and download data

### Example Triggers

The skill will activate when users ask:
- "Show me all breast cancer MRI scans in IDC"
- "How do I download lung CT images from Imaging Data Commons?"
- "Help me visualize DICOM files from IDC"
- "What collections in IDC have CC-BY licensed data?"
- "Query IDC for prostate cancer imaging with segmentations"

## Installation Methods

### For Claude Code Users

```bash
# Place in personal skills directory
cp -r idc-navigator ~/.claude/skills/

# Or in project-specific directory
cp -r idc-navigator .claude/skills/
```

### For MCP Server Integration

The folder can be served via an MCP server like claude-skills-mcp or hosted directly.

### For GitHub Distribution

The folder structure is ready to be:
- Pushed to a GitHub repository
- Cloned by users
- Forked and modified
- Contributed to scientific-skills collections

## Differences from Original .skill Format

**Original format** (Anthropic's packaging):
- Single `.skill` file (zip archive)
- Packaged using `package_skill.py`
- Binary format

**K-Dense format** (this version):
- Plain folder structure
- All human-readable text files
- Includes README.md and requirements.txt
- Git-friendly and easily browsable
- Matches scientific-skills repository pattern

## Next Steps for Enhancement

After users start working with this skill, consider adding:

1. **Example scripts** - Common workflows as Python scripts in `scripts/`
2. **SlicerIDCBrowser guide** - Reference doc for 3D Slicer integration
3. **Clinical data examples** - Patterns for querying clinical metadata
4. **Multi-modal workflows** - Examples combining different imaging modalities
5. **Collection-specific guides** - TCGA, NLST, QIN collection examples

The current version focuses on the core discovery, query, download, and visualize workflows.

## Contributing to K-Dense Repository

This skill can be submitted to the K-Dense claude-scientific-skills repository by:

1. Forking the repository
2. Adding `idc-navigator/` to `scientific-skills/`
3. Testing with Claude Code or MCP
4. Submitting a pull request

The skill follows all K-Dense best practices:
- Comprehensive SKILL.md with frontmatter
- Progressive disclosure (brief core + detailed references)
- Working code examples
- Clear use cases
- Proper documentation

