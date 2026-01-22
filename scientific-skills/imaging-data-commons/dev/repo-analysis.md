# Claude Scientific Skills Repository Analysis

**Last updated:** 2025-01-22

This document captures repository patterns and conventions to accelerate future skill development sessions.

## Repository Overview

**Repository:** K-Dense-AI/claude-scientific-skills
**Purpose:** 140+ scientific skills for Claude, enabling AI-assisted research across biology, chemistry, medicine, and more
**Plugin system:** Claude Code plugins via `.claude-plugin/marketplace.json`

## Repository Structure

```
claude-scientific-skills/
├── .claude/                          # Claude settings
├── .claude-plugin/
│   └── marketplace.json              # Plugin manifest listing all skills
├── .github/                          # GitHub workflows
├── docs/
│   ├── scientific-skills.md          # Master list with descriptions
│   ├── examples.md                   # Workflow examples
│   └── open-source-sponsors.md       # Attribution for dependencies
├── scientific-skills/                # 141 skill directories
│   ├── [skill-name]/
│   │   ├── SKILL.md                  # Required: main skill definition
│   │   ├── references/               # Optional: supplementary docs
│   │   ├── scripts/                  # Optional: helper scripts
│   │   ├── assets/                   # Optional: images, data files
│   │   └── dev/                      # Optional: development files
│   └── ...
├── README.md                         # Repository documentation
└── LICENSE.md                        # MIT license
```

## SKILL.md Format (Agent Skills Specification)

All skills must follow the [Agent Skills Specification](https://agentskills.io/specification).

### Required Frontmatter

```yaml
---
name: skill-name                      # Lowercase, hyphenated
description: Brief description...     # 1-2 sentences, what & when to use
license: License type                 # e.g., "BSD-3-Clause license", "MIT", "Unknown"
metadata:
    skill-author: Author Name         # K-Dense Inc. or contributor name
---
```

### Common Section Structure

1. **Overview** - What the tool/database does, core workflow
2. **When to Use This Skill** - Bulleted use cases
3. **Quick Start / Installation** - Basic setup and imports
4. **Core Capabilities** - Numbered subsections with code examples
5. **Common Use Cases** - Detailed workflow examples
6. **Best Practices** - Guidelines and recommendations
7. **Troubleshooting** - Common issues and solutions
8. **Resources** - External links, references

### Code Examples

- Use Python with proper imports
- Include comments explaining non-obvious code
- Show realistic examples with actual data/collections
- Test all examples before including
- Include output comments where helpful

### Documentation Conventions

- Use markdown tables for structured data
- Include "**Note:**" callouts for important caveats
- Reference other skills when relevant (e.g., "For X, see skill-name")
- Link to official documentation with full URLs

## Skill Categories (from docs/scientific-skills.md)

- **Scientific Databases** - API access to PubMed, ChEMBL, UniProt, etc.
- **Scientific Integrations** - LIMS, cloud platforms, lab automation
- **Scientific Packages** - Python libraries (Scanpy, RDKit, etc.)
- **Healthcare AI** - Clinical ML, medical imaging
- **Communication** - Writing, visualization, documentation

## Plugin Registration

Skills must be listed in `.claude-plugin/marketplace.json`:

```json
{
  "skills": [
    "./scientific-skills/skill-name",
    ...
  ]
}
```

## Conventions Observed

### Naming
- Skill directories: lowercase with hyphens (`imaging-data-commons`)
- Database skills often suffixed with `-database` (`chembl-database`)
- Integration skills suffixed with `-integration` (`benchling-integration`)

### References Directory
Used for supplementary documentation:
- API references
- Advanced guides (e.g., BigQuery, DICOMweb)
- Schema documentation
- Portal/UI guides

### Scripts Directory
Contains executable helper scripts:
- Data processing utilities
- Setup/installation scripts
- Example pipelines

### Version Tracking
- Note tested versions in "Installation and Setup" section
- Format: "**Tested with:** package-name X.Y.Z"

## Quality Checklist for Skills

- [ ] Valid SKILL.md frontmatter (name, description, license, metadata)
- [ ] Clear "When to Use" section
- [ ] Installation instructions with package names
- [ ] All code examples tested and working
- [ ] Version noted for version-sensitive packages
- [ ] Common troubleshooting scenarios covered
- [ ] Links to official documentation
- [ ] Skill added to marketplace.json

## IDC Skill-Specific Notes

### Tested Configuration
- idc-index 0.11.5 (IDC data version v23)
- Python environment via uv

### Key Technical Details

**Index Tables:**
- `index` - Primary table, auto-loaded
- `sm_index` - Slide microscopy, requires JOIN with index for collection_id
- `collections_index` - Has CancerTypes (not in primary index)
- `analysis_results_index` - Curated derived datasets

**Important Caveats:**
- Not all annotations in analysis_results - use DICOM Modality (SEG, RTSTRUCT) to find all
- sm_index lacks collection_id column
- Schema discovery via `client.indices_overview`

### Reference Files
- `references/idc_index_api.md` - Python API reference
- `references/bigquery_guide.md` - Advanced queries
- `references/dicomweb_guide.md` - DICOMweb endpoints
- `references/idc_portal_guide.md` - Portal and visualization
- `references/metadata_schema.md` - Data hierarchy

## Development Workflow

1. Check for cached analysis (`dev/repo-analysis.md`)
2. Create/update Python venv with uv for testing
3. Verify all code examples execute successfully
4. Update version tracking if package updated
5. Follow repository patterns for new content
6. Update this analysis file with new learnings
