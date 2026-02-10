# API Versioning Guide

This project uses a simple file-based versioning system for the API.

## How It Works

1. **VERSION File**: The root of the repository contains a `VERSION` file with the current API version (e.g., `1.0.0`)

2. **Automatic Deployment**: When you push to the `main` branch:
   - The CD pipeline reads the version from the `VERSION` file
   - Trains and promotes the model (if it meets criteria)
   - Builds a Docker image tagged with `v{VERSION}` (e.g., `v1.0.0`)
   - Deploys to AWS ECS
   - Creates a GitHub release with the version tag

3. **Version Tracking**: The API exposes the version in all responses:
   - `GET /` - Shows API version and model version
   - `GET /health` - Shows API version and model info
   - `POST /predict` - Returns API version in prediction response
   - `GET /model/info` - Shows detailed version information

## Updating the Version

To release a new version:

1. **Update the VERSION file:**
   ```bash
   echo "1.0.1" > VERSION
   ```

2. **Commit and push to main:**
   ```bash
   git add VERSION
   git commit -m "Bump version to 1.0.1"
   git push origin main
   ```

3. **Deployment happens automatically:**
   - CD pipeline triggers on push to main
   - Reads version from VERSION file
   - Builds and deploys with new version

## Version Format

Use [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes (e.g., `2.0.0`)
- **MINOR** version: New features, backward compatible (e.g., `1.1.0`)
- **PATCH** version: Bug fixes, backward compatible (e.g., `1.0.1`)

## Examples

### Check Current API Version

```bash
curl http://localhost:8000/ | jq
```

Response:
```json
{
  "message": "Breast Cancer Detection API",
  "api_version": "v1.0.0",
  "model_version": "abc123def456",
  "model_promoted_at": "2026-02-10T18:30:00",
  "docs": "/docs",
  "health": "/health"
}
```

### Production Deployment Workflow

```bash
# 1. Make your code changes
git add .
git commit -m "Add new feature"

# 2. Update version (minor bump for new feature)
echo "1.1.0" > VERSION
git add VERSION
git commit -m "Bump version to 1.1.0"

# 3. Push to main (triggers deployment)
git push origin main

# 4. Monitor GitHub Actions for deployment status
# 5. Check deployed version
curl https://your-api.com/health | jq '.api_version'
```

## Version History

Track your versions in this section:

- **v1.0.0** (2026-02-10) - Initial production release
  - Logistic Regression model
  - Basic prediction endpoint
  - Health check and model info endpoints

## Notes

- The VERSION file contains only the version number (e.g., `1.0.0`), without the `v` prefix
- The CD pipeline automatically adds the `v` prefix when creating tags and Docker images
- Both API version and model version (MLflow run ID) are tracked separately
- API version = deployment/code version
- Model version = specific trained model instance

## Local Development

When running locally, the API will:
1. Read the version from the `VERSION` file
2. If file doesn't exist, default to `"development"`

```bash
# Start the API (reads from VERSION file)
uvicorn src.api.main:app --reload

# Version is automatically loaded from VERSION file
```
