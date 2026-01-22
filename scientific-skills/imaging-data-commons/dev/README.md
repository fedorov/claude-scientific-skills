# Prompt for starting new iteration

I'm developing a Claude skill for NCI Imaging Data Commons to be contributed to https://github.com/K-Dense-AI/claude-scientific-skills. The skill is in scientific-skills/imaging-data-commons/SKILL.md in the source tree.

**IMPORTANT**: Before analyzing the `claude-scientific-skills` repository from scratch, check if `scientific-skills/imaging-data-commons/dev/repo-analysis.md` exists in the source tree. If it does, read it and use that cached analysis instead of re-analyzing. If it does not, or if I ask you to refresh it, analyze the repository and save your findings to `scientific-skills/imaging-data-commons/dev/repo-analysis.md` for future reuse.

This skill relies critically on the idc-index python package. Whenever suggesting code snippets or SQL queries that are executed using idc-index, install idc-index in a test environment and confirm those examples work. Whenever idc-index version is different from what is mentioned in the skill, update the version used for development and testing in the "Installation and Setup" section.

When testing idc-index package make a python environment using the uv already installed on the system. Ask where it is if you cannot find it.  

Current status: I am reviewing the content and will be asking you to add features and revisit specific components. Whenever you notice that the definition of the skill does not follow the conventions in the repository, or best practices for developing a claude skill, alert me and suggest changes.

[Rest of your prompt...]

Next task: [specific refinement needed]