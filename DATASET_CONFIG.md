# Dataset Configuration Guide

This project uses the **Wisconsin Breast Cancer Dataset** from Kaggle. The dataset loading is **flexible and supports multiple sources**!

## 🎯 Supported Data Sources

1. **AWS S3** (⭐ Recommended for CI/CD) - Store dataset in S3 bucket
2. **Local File** - Use file from your computer
3. **Kaggle Auto-Download** - Automatic fallback for local development

---

## 📁 Option 1: AWS S3 (Recommended for Production/CI/CD)

**Best for**: GitHub Actions, Docker, AWS deployments

### Why S3?
✅ No CSV files in Git repository
✅ Fast downloads in CI/CD
✅ Version control for datasets
✅ Same source for training and deployment
✅ Cost: ~$0.01/month

### Quick Setup

See **[S3_DATASET_SETUP.md](S3_DATASET_SETUP.md)** for complete guide.

**Summary**:
1. Create S3 bucket: `your-ml-datasets`
2. Upload dataset: `s3://your-ml-datasets/datasets/breast-cancer.csv`
3. Add GitHub secret: `DATASET_S3_URI`
4. Done! CI/CD will use S3 automatically

### Usage

**In GitHub Actions** (automatic):
```yaml
env:
  DATASET_S3_URI: ${{ secrets.DATASET_S3_URI }}
```

**Local development**:
```powershell
$env:DATASET_S3_URI = "s3://your-ml-datasets/datasets/breast-cancer.csv"
cd src
python train.py
```

---

## 📁 Option 2: Automatic Download (Local Development)

Just run the training - the dataset will download automatically:

```powershell
cd src
python train.py
```

On first run, you'll see:
```
⚠️ Dataset not found at C:\Users\...
Attempting to download from Kaggle: yasserh/breast-cancer-dataset
✓ Dataset downloaded to: C:\Users\...\.cache\kagglehub\...
```

**Requirements:**
- `kagglehub` package (already in requirements.txt)
- Internet connection on first run

---

## 📁 Option 2: Use Custom Path

If you already have the dataset downloaded, set the path via environment variable:

### Windows PowerShell:
```powershell
$env:DATASET_PATH = "C:\path\to\your\breast-cancer.csv"
cd src
python train.py
```

### Linux/Mac:
```bash
export DATASET_PATH="/path/to/your/breast-cancer.csv"
cd src
python train.py
```

### Using .env file (Persistent):
1. Copy `.env.example` to `.env`
2. Edit `.env`:
   ```
   DATASET_PATH=C:\path\to\your\breast-cancer.csv
   ```
3. Install python-dotenv: `pip install python-dotenv`
4. Load in your script:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## 🐳 Docker / CI/CD

The dataset will auto-download during:
- Docker build (if needed)
- GitHub Actions CI/CD
- AWS deployment

**No manual intervention required!**

### CI/CD Considerations

The CD pipeline will download the dataset automatically during the training step:

```yaml
- name: Run full training pipeline
  run: |
    cd src
    python train.py --k-folds 10
```

**Note**: First-time download adds ~1-2 minutes to CI/CD pipeline. Subsequent runs use cached data in GitHub Actions runners (~30-60 seconds).

### Docker Optimization

To avoid re-downloading in every Docker build, the dataset is downloaded at **runtime** (not build time):

```dockerfile
# Dataset downloads on container start
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔍 Manual Download (Optional)

If automatic download doesn't work, download manually:

1. **Visit Kaggle**: https://www.kaggle.com/datasets/yasserh/breast-cancer-dataset
2. **Login** (create free account if needed)
3. **Download** the CSV file
4. **Update config.py** or set `DATASET_PATH` environment variable

---

## 📊 Dataset Information

- **Source**: Kaggle - Wisconsin Breast Cancer Dataset
- **Samples**: 569 patients
- **Features**: 30 numerical features
- **Target**: Diagnosis (Malignant/Benign)
- **Format**: CSV file (~125 KB)
- **License**: Public domain

### Feature Categories:
1. **Mean** (10 features): radius_mean, texture_mean, perimeter_mean, etc.
2. **Standard Error** (10 features): radius_se, texture_se, etc.
3. **Worst** (10 features): radius_worst, texture_worst, etc.

---

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'kagglehub'"

**Solution**:
```powershell
pip install kagglehub
```

### Issue: "Unable to download dataset from Kaggle"

**Causes**:
- No internet connection
- Kaggle API issues
- Corporate firewall blocking download

**Solutions**:
1. Check internet connection
2. Download manually and set `DATASET_PATH`
3. Configure proxy if behind firewall:
   ```powershell
   $env:HTTP_PROXY = "http://proxy.company.com:8080"
   $env:HTTPS_PROXY = "http://proxy.company.com:8080"
   ```

### Issue: "FileNotFoundError" in CI/CD

**Check**:
1. GitHub Actions runner has internet access
2. kagglehub is in requirements.txt
3. Training step runs `cd src && python train.py` (correct working directory)

---

## 🎯 Configuration Summary

### Default Behavior (No Config Needed):
```python
# config.py
DATASET_PATH = os.environ.get('DATASET_PATH', '<your-local-cache>')
KAGGLE_DATASET = 'yasserh/breast-cancer-dataset'
```

### Priority Order:
1. 🥇 Environment variable `DATASET_PATH` (if set)
2. 🥈 Local cache path (if file exists)
3. 🥉 Auto-download from Kaggle

---

## ✅ Best Practices

1. **Development**: Let it auto-download on first run
2. **CI/CD**: Auto-download is fine (adds ~1 min to pipeline)
3. **Production**: Consider bundling dataset in Docker image if you want faster startup
4. **Team**: Share `.env.example` but never commit `.env` (it's gitignored)

---

## 📝 Example Usage

### Simple Training:
```powershell
# No configuration needed!
cd src
python train.py
```

### With Custom Path:
```powershell
$env:DATASET_PATH = "D:\datasets\breast-cancer.csv"
cd src
python train.py
```

### In Python Script:
```python
import os
os.environ['DATASET_PATH'] = '/custom/path/data.csv'

from utils.load_data import load_data
df = load_data()  # Uses your custom path
```

---

## 🔗 Related Files

- `src/utils/config.py` - Dataset configuration
- `src/utils/load_data.py` - Loading logic with auto-download
- `.env.example` - Environment variable template
- `.gitignore` - Ensures `.env` is not committed

---

**Questions?** The dataset will auto-download automatically. Just run the training! 🚀
