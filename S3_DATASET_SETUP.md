# AWS S3 Dataset Setup Guide

This guide shows you how to store the dataset in **AWS S3** for use in CI/CD pipelines and production deployments.

## 🎯 Why Use S3 for Datasets?

✅ **No Git bloat** - Keep CSV files out of your repository  
✅ **CI/CD friendly** - GitHub Actions can download from S3  
✅ **Production ready** - Same dataset source for training and deployment  
✅ **Versioning** - Use S3 versioning to track dataset changes  
✅ **Cost effective** - ~$0.023/GB/month for Standard storage  

---

## 📋 Prerequisites

- AWS Account
- Dataset file: `breast-cancer.csv` (download from [Kaggle](https://www.kaggle.com/datasets/yasserh/breast-cancer-dataset))
- AWS CLI installed (optional but recommended)

---

## Step 1: Download Dataset from Kaggle

### Option A: Manual Download
1. Visit https://www.kaggle.com/datasets/yasserh/breast-cancer-dataset
2. Click **Download** button
3. Extract `breast-cancer.csv` from the ZIP file

### Option B: Using Kaggle API
```powershell
# Install Kaggle CLI
pip install kaggle

# Configure credentials (get from kaggle.com/settings)
# Save to ~/.kaggle/kaggle.json (Linux/Mac) or C:\Users\<user>\.kaggle\kaggle.json (Windows)

# Download dataset
kaggle datasets download -d yasserh/breast-cancer-dataset
unzip breast-cancer-dataset.zip
```

---

## Step 2: Create S3 Bucket

### Using AWS Console

1. Go to **S3 Console**: https://console.aws.amazon.com/s3/
2. Click **Create bucket**
3. **Bucket name**: `your-ml-datasets` (must be globally unique)
4. **Region**: Choose same region as your ECS deployment (e.g., `us-east-1`)
5. **Block Public Access**: Keep all blocks enabled (bucket should be private)
6. **Bucket Versioning**: Enable (recommended for dataset versioning)
7. **Encryption**: Enable with SSE-S3 (default encryption)
8. Click **Create bucket**

### Using AWS CLI

```powershell
# Create bucket
aws s3 mb s3://your-ml-datasets --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket your-ml-datasets \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-ml-datasets \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'
```

---

## Step 3: Upload Dataset to S3

### Using AWS Console

1. Open your bucket: `your-ml-datasets`
2. Click **Create folder** → Name it `datasets`
3. Open the `datasets` folder
4. Click **Upload**
5. Drag and drop `breast-cancer.csv`
6. Click **Upload**

**Result**: Your file is now at `s3://your-ml-datasets/datasets/breast-cancer.csv`

### Using AWS CLI

```powershell
# Upload dataset
aws s3 cp breast-cancer.csv s3://your-ml-datasets/datasets/breast-cancer.csv

# Verify upload
aws s3 ls s3://your-ml-datasets/datasets/

# View file details
aws s3api head-object \
  --bucket your-ml-datasets \
  --key datasets/breast-cancer.csv
```

---

## Step 4: Set IAM Permissions

### For GitHub Actions Deployer

Update your `github-actions-deployer` IAM user policy to allow S3 access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-ml-datasets",
        "arn:aws:s3:::your-ml-datasets/datasets/*"
      ]
    }
  ]
}
```

### Steps:
1. Go to **IAM Console** → **Users** → `github-actions-deployer`
2. Click **Add permissions** → **Create inline policy**
3. Choose **JSON** tab
4. Paste the policy above (replace `your-ml-datasets` with your bucket name)
5. Name it: `S3DatasetReadAccess`
6. Click **Create policy**

---

## Step 5: Configure GitHub Secrets

Add the S3 URI to your GitHub repository secrets:

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   ```
   Name: DATASET_S3_URI
   Secret: s3://your-ml-datasets/datasets/breast-cancer.csv
   ```
4. Click **Add secret**

**Total Secrets**: You should now have **9 secrets** (8 from AWS setup + 1 for dataset)

---

## Step 6: Update Local Development (Optional)

### Option A: Use Environment Variable

```powershell
# Windows PowerShell
$env:DATASET_S3_URI = "s3://your-ml-datasets/datasets/breast-cancer.csv"
cd src
python train.py
```

### Option B: Use .env File

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env`:
   ```
   DATASET_S3_URI=s3://your-ml-datasets/datasets/breast-cancer.csv
   ```

3. Install python-dotenv:
   ```powershell
   pip install python-dotenv
   ```

4. Load in your script (already configured):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Step 7: Test It Works

### Test Locally

```powershell
# Set S3 URI
$env:DATASET_S3_URI = "s3://your-ml-datasets/datasets/breast-cancer.csv"

# Ensure AWS credentials are configured
aws s3 ls s3://your-ml-datasets/datasets/

# Run training
cd src
python train.py --smoke --k-folds 3
```

Expected output:
```
============================================================
LOADING DATA
============================================================
Loading from S3: s3://your-ml-datasets/datasets/breast-cancer.csv
Downloading from bucket 'your-ml-datasets', key 'datasets/breast-cancer.csv'...
✓ Downloaded to: C:\...\breast-cancer-ml\data\breast-cancer.csv
Dataset loaded successfully!
Shape: 569 rows, 31 columns
```

### Test in GitHub Actions

1. Push changes to GitHub:
   ```powershell
   git add .
   git commit -m "Add S3 dataset support"
   git push origin main
   ```

2. Create release tag:
   ```powershell
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. Monitor GitHub Actions → CD workflow
4. Check training step logs for S3 download

---

## 📊 Cost Estimate

### S3 Storage Costs

**Dataset**: 125 KB (0.000122 GB)

- **Storage**: $0.023/GB/month × 0.000122 GB = **$0.000003/month** (negligible)
- **Requests**: 
  - PUT requests: ~1/month = $0.000005
  - GET requests: ~30/month (CI/CD) = $0.000012
- **Data transfer OUT to EC2/ECS**: FREE (same region)
- **Data transfer OUT to internet**: $0.09/GB (only for local dev, minimal)

**Total Monthly Cost**: **< $0.01** (essentially free!)

### Annual Cost Projection

- **First year**: ~$0.10
- **With versioning** (10 versions): ~$1.00/year

---

## 🔒 Security Best Practices

### 1. Use Bucket Policies

Restrict access to specific IAM users:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowGitHubActionsRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/github-actions-deployer"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-ml-datasets",
        "arn:aws:s3:::your-ml-datasets/datasets/*"
      ]
    }
  ]
}
```

### 2. Enable Access Logging

Track who accesses your dataset:

```powershell
# Create logging bucket
aws s3 mb s3://your-ml-datasets-logs

# Enable logging
aws s3api put-bucket-logging \
  --bucket your-ml-datasets \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "your-ml-datasets-logs",
      "TargetPrefix": "access-logs/"
    }
  }'
```

### 3. Use S3 Versioning

Keep history of dataset changes:

```powershell
# List versions
aws s3api list-object-versions \
  --bucket your-ml-datasets \
  --prefix datasets/breast-cancer.csv

# Download specific version
aws s3api get-object \
  --bucket your-ml-datasets \
  --key datasets/breast-cancer.csv \
  --version-id <VERSION_ID> \
  breast-cancer-v1.csv
```

---

## 🔄 Dataset Update Workflow

When you need to update the dataset:

1. **Upload new version**:
   ```powershell
   aws s3 cp breast-cancer-v2.csv s3://your-ml-datasets/datasets/breast-cancer.csv
   ```
   (S3 versioning keeps old version automatically)

2. **Trigger retraining**:
   ```powershell
   git tag v1.0.1
   git push origin v1.0.1
   ```

3. **View version history**:
   ```powershell
   aws s3api list-object-versions \
     --bucket your-ml-datasets \
     --prefix datasets/breast-cancer.csv
   ```

4. **Rollback if needed**:
   ```powershell
   # Get version ID from previous step
   aws s3api copy-object \
     --bucket your-ml-datasets \
     --copy-source your-ml-datasets/datasets/breast-cancer.csv?versionId=OLD_VERSION_ID \
     --key datasets/breast-cancer.csv
   ```

---

## 🐛 Troubleshooting

### Issue: "Access Denied" Error

**Causes**:
- IAM user doesn't have S3 permissions
- Bucket policy is too restrictive
- Wrong AWS credentials in GitHub secrets

**Solutions**:
1. Verify IAM policy includes `s3:GetObject` and `s3:ListBucket`
2. Check bucket name and region are correct
3. Test with AWS CLI:
   ```powershell
   aws s3 cp s3://your-ml-datasets/datasets/breast-cancer.csv test.csv
   ```

### Issue: "Bucket does not exist"

**Check**:
- Bucket name is correct (case-sensitive)
- Bucket is in the same AWS account
- Region is correctly configured

### Issue: "No credentials found"

**For Local Development**:
```powershell
# Configure AWS CLI
aws configure

# Or set environment variables
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."
$env:AWS_REGION = "us-east-1"
```

**For GitHub Actions**:
- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets are set
- Check CD workflow includes AWS credentials in training step

---

## ✅ Verification Checklist

After setup, verify:

- [ ] S3 bucket created: `your-ml-datasets`
- [ ] Dataset uploaded: `s3://your-ml-datasets/datasets/breast-cancer.csv`
- [ ] IAM permissions configured for `github-actions-deployer`
- [ ] GitHub secret `DATASET_S3_URI` added
- [ ] CD workflow updated with S3 environment variables
- [ ] Local testing works with S3 URI
- [ ] GitHub Actions training step downloads from S3
- [ ] Dataset not committed to Git repository

---

## 📝 Summary

### Priority Order for Dataset Loading:

1. 🥇 **S3 URI** (if `DATASET_S3_URI` env var is set)
2. 🥈 **Local file** (if file exists at `DATASET_PATH`)
3. 🥉 **Kaggle download** (fallback for local development)

### Recommended Setup:

- **Production/CI/CD**: Use S3 (`DATASET_S3_URI` in GitHub secrets)
- **Local Development**: Use local file or Kaggle auto-download
- **Cost**: ~$0.01/month for dataset storage

### Next Steps:

1. Create S3 bucket and upload dataset
2. Add `DATASET_S3_URI` to GitHub secrets
3. Test deployment with `git tag v1.0.0 && git push origin v1.0.0`
4. Monitor GitHub Actions for successful S3 download

---

**Questions?** Check CloudWatch Logs or GitHub Actions logs for detailed error messages.
