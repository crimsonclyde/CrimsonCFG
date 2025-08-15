# MDM Manager Release Process

This document explains how to create releases for the MDM Manager project using GitLab CI/CD.

## Overview

The project uses automated CI/CD pipelines to create release packages when version tags are pushed to GitLab. The pipeline will:
1. Run tests
2. Create a zip package of the repository
3. Create a GitLab release with the package attached

## Prerequisites

- Git access to the repository
- GitLab CI/CD runner available (tags: ansible, hetzner, terraform)
- Version tag in format `vX.Y.Z` (e.g., `v0.2.2`)

## Release Process

### Step 1: Create a Version Tag

Create an annotated tag with your version number:

```bash
cd CrimsonCFG
git tag -a v0.2.2 -m "Release 0.2.2"
```

### Step 2: Push the Tag

Push the tag to trigger the CI/CD pipeline:

```bash
git push origin v0.2.2
```

### Step 3: Monitor the Pipeline

1. Go to your GitLab project page
2. Navigate to **"CI/CD" → "Pipelines"**
3. Watch the pipeline progress through three stages:
   - **test**: Runs Python tests
   - **package**: Creates the zip package
   - **release**: Creates the GitLab release

### Step 4: Access the Release

Once the pipeline completes successfully:

1. Go to **"Deploy" → "Releases"** in your GitLab project
2. Find your release (e.g., "Release v0.2.2")
3. Download the attached zip file: `CrimsonCFG-0.2.2.zip`

## Manual Pipeline Trigger

If you need to trigger the pipeline for an existing tag:

1. Go to **"CI/CD" → "Pipelines"**
2. Click **"Run Pipeline"**
3. In **"Run for branch name or tag"**, enter your tag (e.g., `v0.2.2`)
4. Click **"Run Pipeline"**

## Cleaning Up and Recreating Tags

If you need to recreate a tag (e.g., to test the pipeline):

### Delete Local Tag
```bash
git tag -d v0.2.2
```

### Delete Remote Tag
```bash
git push origin :refs/tags/v0.2.2
```

### Recreate and Push
```bash
git tag v0.2.2
git push origin v0.2.2
```

## Package Contents

The generated zip package contains:
- Entire repository contents
- Excludes `.git` directory
- Respects `.gitattributes` exclusions (files marked with `export-ignore`)
- Named format: `CrimsonCFG-X.Y.Z.zip`

## Troubleshooting

### Pipeline Not Starting
- Ensure the tag follows the format `vX.Y.Z`
- Check that the tag is pushed to the remote repository
- Verify GitLab CI/CD runner is available

### Release Not Created
- Check that all pipeline stages completed successfully
- Verify the `create_release` job ran without errors
- Look for any GitLab release permissions issues

### Artifacts Not Available
- Artifacts expire after 1 week
- Check the job artifacts in **"CI/CD" → "Jobs"**
- Download artifacts before they expire

## Version Numbering

Follow semantic versioning:
- **Major** (X): Breaking changes
- **Minor** (Y): New features, backward compatible
- **Patch** (Z): Bug fixes, backward compatible

Examples: `v1.0.0`, `v0.2.2`, `v2.1.3`
