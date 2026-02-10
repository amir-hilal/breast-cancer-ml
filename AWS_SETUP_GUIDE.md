# AWS Setup Guide for CI/CD Pipeline

Complete guide to set up AWS infrastructure for automated deployment of the Breast Cancer ML API.

## 📋 Prerequisites

- AWS Account (create at https://aws.amazon.com if needed)
- Credit card for AWS billing (Free Tier available)
- GitHub repository created
- Trained model ready for deployment

---

## 🎯 Overview

You'll set up:
1. **IAM User** - For programmatic access
2. **ECR Repository** - To store Docker images
3. **ECS Cluster** - To run containers (recommended for production)
4. **GitHub Secrets** - For secure credentials

**Estimated Monthly Cost**: $50-70 (ECS Fargate) or $35-50 (Elastic Beanstalk)

---

## Step 1: Create IAM User with Permissions

### 1.1 Navigate to IAM Console
1. Sign in to AWS Console: https://console.aws.amazon.com
2. Search for "IAM" in the top search bar
3. Click **IAM** (Identity and Access Management)

### 1.2 Create New User
1. Click **Users** in left sidebar
2. Click **Create user** button
3. **User name**: `github-actions-deployer`
4. Click **Next**

### 1.3 Attach Policies
Select **Attach policies directly**, then attach these policies:

```
✅ AmazonEC2ContainerRegistryFullAccess
✅ AmazonECS_FullAccess
✅ AmazonElasticBeanstalkFullAccess (if using Beanstalk)
✅ CloudWatchLogsFullAccess
✅ IAMReadOnlyAccess
```

Click **Next** → **Create user**

### 1.4 Create Access Key
1. Click on the newly created user
2. Go to **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **Application running outside AWS**
6. Click **Next** → **Create access key**

**⚠️ IMPORTANT**: Save these credentials immediately!

```
AWS_ACCESS_KEY_ID: AKIA...
AWS_SECRET_ACCESS_KEY: wJalrXUtn...
```

You won't be able to see the secret key again!

---

## Step 2: Set Up Amazon ECR (Container Registry)

### 2.1 Navigate to ECR
1. Search for "ECR" in AWS Console
2. Click **Amazon Elastic Container Registry**

### 2.2 Create Repository
1. Click **Get Started** or **Create repository**
2. **Visibility**: Private
3. **Repository name**: `breast-cancer-ml-api`
4. **Tag immutability**: Enable (recommended)
5. **Scan on push**: Enable (for security)
6. Click **Create repository**

### 2.3 Note Repository URI
After creation, you'll see:
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml-api
```

**Save this URI** - you'll need it for GitHub secrets!

---

## Step 3: Set Up ECS Fargate (Recommended for Production)

### 3.1 Navigate to ECS
1. Search for "ECS" in AWS Console
2. Click **Amazon Elastic Container Service**

### 3.2 Create Cluster
1. Click **Clusters** in left sidebar
2. Click **Create cluster**
3. **Cluster name**: `ml-api-cluster`
4. **Infrastructure**: AWS Fargate (serverless)
5. Click **Create**

### 3.3 Create Task Definition
1. Click **Task Definitions** in left sidebar
2. Click **Create new task definition**
3. **Task definition family**: `breast-cancer-api-task`
4. **Launch type**: AWS Fargate
5. **Operating system**: Linux/X86_64
6. **CPU**: 0.5 vCPU (or 1 vCPU for better performance)
7. **Memory**: 1 GB (or 2 GB)
8. **Task role**: Create new role or use existing
9. **Task execution role**: Create new role (ecsTaskExecutionRole)

**Container details:**
- **Name**: `api-container`
- **Image URI**: `123456789012.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml-api:latest`
  (Use your ECR URI from Step 2.3)
- **Port**: 8000 (TCP)
- **Environment variables** (optional):
  - `MODEL_PATH` = `/app/models/latest/model`

10. Click **Create**

### 3.4 Create Service
1. Go back to your cluster: `ml-api-cluster`
2. Click **Services** tab
3. Click **Create**
4. **Compute options**: Launch type
5. **Launch type**: FARGATE
6. **Task Definition**: `breast-cancer-api-task` (select latest revision)
7. **Service name**: `breast-cancer-api-service`
8. **Desired tasks**: 1 (or 2 for high availability)

**Networking:**
- **VPC**: Select default VPC
- **Subnets**: Select all available
- **Security group**: Create new
  - **Name**: `ml-api-sg`
  - **Inbound rules**: Allow TCP port 8000 from anywhere (0.0.0.0/0)
- **Public IP**: ENABLED (important!)

**Load balancing** (optional but recommended):
- **Load balancer type**: Application Load Balancer
- **Create new load balancer**: Yes
- **Listener**: Port 80 → Target port 8000
- **Target group**: Create new
- **Health check path**: `/health`

9. Click **Create**

### 3.5 Note Service Details
After creation, save:
- **Cluster name**: `ml-api-cluster`
- **Service name**: `breast-cancer-api-service`
- **Task definition**: `breast-cancer-api-task`

---

## Step 4: Configure GitHub Secrets

### 4.1 Navigate to Repository Settings
1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**

### 4.2 Add Required Secrets
Click **New repository secret** for each:

#### AWS Credentials
```yaml
Name: AWS_ACCESS_KEY_ID
Secret: AKIA... (from Step 1.4)
```

```yaml
Name: AWS_SECRET_ACCESS_KEY
Secret: wJalrXUtn... (from Step 1.4)
```

```yaml
Name: AWS_REGION
Secret: us-east-1 (or your chosen region)
```

#### ECR Configuration
```yaml
Name: ECR_REPOSITORY
Secret: breast-cancer-ml-api (repository name from Step 2.2)
```

```yaml
Name: ECR_REGISTRY
Secret: 123456789012.dkr.ecr.us-east-1.amazonaws.com (from Step 2.3)
```

#### ECS Configuration
```yaml
Name: ECS_CLUSTER
Secret: ml-api-cluster
```

```yaml
Name: ECS_SERVICE
Secret: breast-cancer-api-service
```

```yaml
Name: ECS_TASK_DEFINITION
Secret: breast-cancer-api-task
```

#### Dataset Configuration (S3)
```yaml
Name: DATASET_S3_URI
Secret: s3://your-ml-datasets/datasets/breast-cancer.csv
```

**Note**: See [S3_DATASET_SETUP.md](S3_DATASET_SETUP.md) for detailed S3 setup instructions.

### 4.3 Verify All Secrets
You should have **9 secrets** total:
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ AWS_REGION
- ✅ ECR_REPOSITORY
- ✅ ECR_REGISTRY
- ✅ ECS_CLUSTER
- ✅ ECS_SERVICE
- ✅ ECS_TASK_DEFINITION
- ✅ DATASET_S3_URI

---

## Step 5: Update CD Pipeline Configuration

### 5.1 Check `.github/workflows/cd.yml`

Make sure your CD workflow uses the secrets correctly:

```yaml
env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REGISTRY: ${{ secrets.ECR_REGISTRY }}
  ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY }}
  ECS_SERVICE: ${{ secrets.ECS_SERVICE }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_TASK_DEFINITION: ${{ secrets.ECS_TASK_DEFINITION }}
```

### 5.2 Verify Deployment Steps

Your CD pipeline should include:
1. ✅ Train model and promote
2. ✅ Build Docker image
3. ✅ Push to ECR
4. ✅ Update ECS task definition
5. ✅ Deploy to ECS service

---

## Step 6: Test the Setup

### 6.1 Create a Release Tag

```powershell
# Commit all changes
git add .
git commit -m "Add production ML pipeline with AWS deployment"

# Push to GitHub
git push origin main

# Create release tag
git tag v1.0.0
git push origin v1.0.0
```

### 6.2 Monitor GitHub Actions
1. Go to your repo → **Actions** tab
2. You should see the CD workflow running
3. Monitor each step for errors

### 6.3 Check AWS Deployment
1. Go to ECS Console → Your cluster
2. Check **Services** tab
3. Click your service → **Tasks** tab
4. Verify task is **RUNNING**
5. Click on task → Note **Public IP**

### 6.4 Test the API
```powershell
# Replace with your ECS task's public IP
curl http://YOUR-TASK-PUBLIC-IP:8000/health

# Or if using Load Balancer
curl http://YOUR-ALB-DNS/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "model_path": "models/latest/model"
}
```

---

## 📊 Cost Breakdown

### ECS Fargate (Recommended)
- **0.5 vCPU, 1 GB Memory**: ~$15/month
- **1 vCPU, 2 GB Memory**: ~$30/month
- **Application Load Balancer**: ~$20/month
- **Data Transfer**: ~$5/month
- **Total**: $50-70/month

### Elastic Beanstalk (Simpler)
- **t3.small instance**: ~$15/month
- **Load Balancer**: ~$20/month
- **Total**: $35-50/month

### Free Tier (First 12 months)
- 750 hours/month of t2.micro instances (Beanstalk)
- 10 GB data transfer

---

## 🔒 Security Best Practices

### 1. Restrict IAM Permissions
After testing, minimize IAM user permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Use AWS Secrets Manager
Instead of hardcoding sensitive data:
```yaml
# In ECS task definition
"secrets": [
  {
    "name": "API_KEY",
    "valueFrom": "arn:aws:secretsmanager:region:account:secret:api-key"
  }
]
```

### 3. Enable CloudWatch Logging
In task definition:
```json
"logConfiguration": {
  "logDriver": "awslogs",
  "options": {
    "awslogs-group": "/ecs/breast-cancer-api",
    "awslogs-region": "us-east-1",
    "awslogs-stream-prefix": "ecs"
  }
}
```

### 4. Set Up Alarms
- CPU utilization > 80%
- Memory utilization > 80%
- Task failed health checks
- 5xx error rate

---

## 🐛 Troubleshooting

### Issue: ECR Push Failed
**Error**: "denied: Your authorization token has expired"

**Solution**:
```powershell
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### Issue: ECS Task Keeps Stopping
**Check**:
1. CloudWatch Logs for error messages
2. Task has enough memory/CPU
3. Docker image exists in ECR
4. Security group allows port 8000
5. Public IP is enabled

### Issue: Model Not Loading
**Check**:
1. Model was promoted during training
2. `models/latest/model/` exists in Docker image
3. MLflow artifacts included in build
4. Container has read permissions

### Issue: Health Check Failing
**Check**:
1. Path is `/health` (not `/`)
2. Port 8000 is exposed
3. Grace period is sufficient (60-120 seconds)
4. API starts successfully

---

## 🚀 Advanced: Using Application Load Balancer

### Benefits
- SSL/TLS termination (HTTPS)
- Custom domain name
- Auto-scaling support
- Better monitoring

### Setup
1. Create ALB in EC2 Console
2. Add listener: Port 80 → Port 8000
3. Configure target group
4. Update ECS service to use ALB
5. (Optional) Add Route 53 for custom domain

---

## 📝 Post-Deployment Checklist

- [ ] API responds to health checks
- [ ] `/predict` endpoint works
- [ ] Model loaded successfully
- [ ] CloudWatch logs enabled
- [ ] Cost alerts configured
- [ ] Auto-scaling configured (optional)
- [ ] SSL certificate added (optional)
- [ ] Custom domain configured (optional)
- [ ] Monitoring dashboards created
- [ ] Documentation updated with API URL

---

## 🔄 Updating the Deployment

To deploy new changes:

```powershell
# Make your changes
git add .
git commit -m "Update model or code"
git push

# Create new version tag
git tag v1.0.1
git push origin v1.0.1
```

The CD pipeline will automatically:
1. Train and promote new model
2. Build new Docker image
3. Push to ECR
4. Update ECS service with new image
5. Perform zero-downtime deployment

---

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **ECS Guide**: https://docs.aws.amazon.com/ecs/
- **ECR Guide**: https://docs.aws.amazon.com/ecr/
- **GitHub Actions**: https://docs.github.com/actions
- **AWS Free Tier**: https://aws.amazon.com/free/

---

## ✅ Quick Reference

### Useful AWS CLI Commands

```powershell
# List ECR repositories
aws ecr describe-repositories

# List ECS clusters
aws ecs list-clusters

# Describe service
aws ecs describe-services --cluster ml-api-cluster --services breast-cancer-api-service

# View logs
aws logs tail /ecs/breast-cancer-api --follow

# List running tasks
aws ecs list-tasks --cluster ml-api-cluster

# Force new deployment
aws ecs update-service --cluster ml-api-cluster --service breast-cancer-api-service --force-new-deployment
```

---

**Next Steps**: After setup, test your CD pipeline by creating a release tag (v1.0.0) and monitoring the deployment!

**Questions?** Check CloudWatch Logs and GitHub Actions logs for detailed error messages.
