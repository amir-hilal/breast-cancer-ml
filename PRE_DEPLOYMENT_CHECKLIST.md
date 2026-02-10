# Pre-Deployment Checklist

Complete this checklist **before** pushing to GitHub to ensure smooth CI/CD deployment.

---

## ✅ Local Development Complete

- [ ] Dataset auto-downloads on first run (no manual download needed!)
- [ ] Model trained successfully with `python src/train.py --k-folds 10`
- [ ] Model promoted to `models/latest/model/` (check promotion logs)
- [ ] MLflow UI working (`mlflow ui` from project root)
- [ ] FastAPI working (`uvicorn src.api.main:app --reload`)
- [ ] `/health` endpoint returns `"status": "healthy"`
- [ ] `/predict` endpoint tested with sample data
- [ ] All tests passing (`pytest tests/` or `python run.py test`)

---
 
## ✅ Code Quality

- [ ] Code formatted with `black src/ tests/`
- [ ] Imports sorted with `isort src/ tests/`
- [ ] No linting errors (`flake8 src/ tests/`)
- [ ] All files committed to git
- [ ] `.gitignore` properly excludes:
  - `.venv/`
  - `__pycache__/`
  - `*.pyc`
  - `.pytest_cache/`
  - `mlruns/` (unless you want to commit)
  - `models/` (large files)

---

## ✅ Repository Setup

- [ ] GitHub repository created
- [ ] Local repo initialized: `git init`
- [ ] Remote added: `git remote add origin https://github.com/username/breast-cancer-ml.git`
- [ ] Main branch created and pushed:
  ```powershell
  git add .
  git commit -m "Initial commit: Production ML pipeline with CI/CD"
  git branch -M main
  git push -u origin main
  ```

---

## ✅ AWS Setup (See AWS_SETUP_GUIDE.md)

### IAM User
- [ ] IAM user created: `github-actions-deployer`
- [ ] Policies attached:
  - `AmazonEC2ContainerRegistryFullAccess`
  - `AmazonECS_FullAccess`
  - `CloudWatchLogsFullAccess`
- [ ] Access key created
- [ ] Access key ID saved
- [ ] Secret access key saved (⚠️ you can't retrieve it again!)

### ECR Repository
- [ ] ECR repository created: `breast-cancer-ml-api`
- [ ] Repository URI saved (e.g., `123456789012.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml-api`)
- [ ] Tag immutability enabled (optional but recommended)
- [ ] Scan on push enabled (optional but recommended)

### ECS Cluster & Service
- [ ] ECS cluster created: `ml-api-cluster`
- [ ] Task definition created: `breast-cancer-api-task`
  - [ ] Fargate launch type
  - [ ] 0.5-1 vCPU configured
  - [ ] 1-2 GB memory configured
  - [ ] Container port 8000 exposed
  - [ ] ECR image URI configured
- [ ] ECS service created: `breast-cancer-api-service`
  - [ ] Public IP enabled
  - [ ] Security group allows port 8000
  - [ ] Health check configured (`/health`)
- [ ] Service, cluster, and task definition names saved

---

## ✅ GitHub Secrets Configured

Navigate to: **Repository → Settings → Secrets and variables → Actions**

All secrets added:
- [ ] `AWS_ACCESS_KEY_ID` (from IAM user)
- [ ] `AWS_SECRET_ACCESS_KEY` (from IAM user)
- [ ] `AWS_REGION` (e.g., `us-east-1`)
- [ ] `ECR_REPOSITORY` (e.g., `breast-cancer-ml-api`)
- [ ] `ECR_REGISTRY` (e.g., `123456789012.dkr.ecr.us-east-1.amazonaws.com`)
- [ ] `ECS_CLUSTER` (e.g., `ml-api-cluster`)
- [ ] `ECS_SERVICE` (e.g., `breast-cancer-api-service`)
- [ ] `ECS_TASK_DEFINITION` (e.g., `breast-cancer-api-task`)

**Total: 8 secrets required**

---

## ✅ CI/CD Configuration

- [ ] `.github/workflows/ci.yml` exists
- [ ] `.github/workflows/cd.yml` exists
- [ ] CD workflow references correct secrets
- [ ] `deployment/Dockerfile` builds successfully locally:
  ```powershell
  docker build -t breast-cancer-api -f deployment/Dockerfile .
  docker run -p 8000:8000 breast-cancer-api
  # Test: curl http://localhost:8000/health
  ```
- [ ] All workflow files committed

---

## ✅ Documentation

- [ ] README.md updated with project info
- [ ] MLFLOW_GUIDE.md present
- [ ] AWS_SETUP_GUIDE.md present
- [ ] MODEL_SELECTION.md present
- [ ] All documentation committed

---

## ✅ Files to Review Before Push

### Must Have
```
✅ src/train.py              # MLflow training pipeline
✅ src/api/main.py           # FastAPI application
✅ src/utils/config.py       # Configuration
✅ requirements.txt          # All dependencies
✅ deployment/Dockerfile     # Docker build config
✅ docker-compose.yml        # Local development
✅ .github/workflows/ci.yml  # CI pipeline
✅ .github/workflows/cd.yml  # CD pipeline
✅ tests/test_training.py    # Unit tests
✅ tests/test_api.py         # API tests
✅ README.md                 # Main documentation
✅ AWS_SETUP_GUIDE.md        # AWS setup instructions
✅ .gitignore                # Ignore patterns
```

### Should Have
```
✅ MLFLOW_GUIDE.md           # MLflow usage guide
✅ MODEL_SELECTION.md        # Model analysis
✅ pyproject.toml            # Tool configs (black, pytest, etc.)
✅ run.py                    # Quick start script
```

---

## 🚀 Ready to Deploy!

Once all checkboxes are complete:

### Step 1: Push to GitHub
```powershell
# Ensure everything is committed
git status

# If there are unstaged changes
git add .
git commit -m "Ready for deployment"

# Push to main branch
git push origin main
```

### Step 2: Create Release Tag (Triggers CD Pipeline)
```powershell
# Tag version 1.0.0
git tag v1.0.0

# Push tag (this triggers CD workflow)
git push origin v1.0.0
```

### Step 3: Monitor Deployment
1. Go to GitHub → **Your Repo** → **Actions** tab
2. Watch the CD workflow execute
3. Check each step for errors:
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Run training pipeline
   - ✅ Check model promotion
   - ✅ Build Docker image
   - ✅ Push to ECR
   - ✅ Deploy to ECS

### Step 4: Verify Deployment
1. Go to AWS Console → ECS → Your cluster
2. Check service is running
3. Find task's public IP
4. Test API:
   ```powershell
   curl http://TASK-PUBLIC-IP:8000/health
   curl http://TASK-PUBLIC-IP:8000/
   ```

### Step 5: Test Prediction Endpoint
```powershell
curl -X POST http://TASK-PUBLIC-IP:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      17.99, 10.38, 122.8, 1001, 0.1184, 0.2776, 0.3001, 0.1471,
      0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904,
      0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019,
      0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
    ]
  }'
```

Expected response:
```json
{
  "prediction": 1,
  "prediction_label": "Malignant",
  "probability": 0.98,
  "confidence": "high"
}
```

---

## 🐛 If Deployment Fails

### Check GitHub Actions Logs
1. Go to Actions tab
2. Click on failed workflow
3. Expand failed step
4. Read error message

### Common Issues

**Model not promoted**:
- Check training logs for promotion criteria
- Verify `models/latest/model/` exists
- Re-run training: `python src/train.py --k-folds 10`

**Docker build failed**:
- Test locally: `docker build -t test -f deployment/Dockerfile .`
- Check Dockerfile paths
- Verify all dependencies in requirements.txt

**AWS authentication failed**:
- Verify GitHub secrets are correct
- Check IAM user has required permissions
- Verify AWS region matches

**ECS deployment failed**:
- Check ECR image exists
- Verify ECS task definition is valid
- Check security group allows port 8000
- Verify public IP is enabled

---

## 📊 Cost Monitoring

After deployment, set up cost alerts:
1. AWS Console → Billing Dashboard
2. Create budget alert
3. Set threshold: $100/month
4. Add email notification

---

## 🎉 Success!

If all checks passed and deployment succeeded:
- ✅ CI/CD pipeline is operational
- ✅ Model automatically deployed on new releases
- ✅ API is publicly accessible
- ✅ Ready for production use

### Next Steps
- Add custom domain (Route 53)
- Set up SSL/TLS (ACM + ALB)
- Configure auto-scaling
- Add monitoring dashboards
- Set up log aggregation (CloudWatch Insights)

---

**Need Help?** Check:
- [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) - Detailed AWS setup
- [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md) - Deployment options
- GitHub Actions logs - Detailed error messages
- CloudWatch Logs - Runtime errors

**Ready to deploy?** Follow the steps above and good luck! 🚀
