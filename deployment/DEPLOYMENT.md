# AWS Deployment Guide

Complete guide for deploying the Breast Cancer Detection API to AWS.

---

## 🎯 Deployment Options Comparison

| Option | Complexity | Cost | Scalability | Best For |
|--------|-----------|------|-------------|----------|
| **Elastic Beanstalk** | ⭐ Low | $ | Auto | Quick deployments, prototypes |
| **ECS Fargate** | ⭐⭐ Medium | $$ | Full control | Production workloads |
| **Lambda** | ⭐⭐⭐ High | ¢ | Automatic | Sporadic traffic |

**Recommendation**: Start with Elastic Beanstalk, migrate to ECS for production.

---

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with billing enabled
- IAM user with programmatic access
- AWS CLI installed and configured

### 2. Install AWS CLI
```bash
# Windows (PowerShell)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
```

### 3. Configure AWS Credentials
```bash
aws configure
# AWS Access Key ID: [Enter your key]
# AWS Secret Access Key: [Enter your secret]
# Default region: us-east-1
# Default output format: json
```

### 4. Create IAM Role for GitHub Actions

```bash
# Create trust policy for GitHub Actions
cat > github-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/YOUR_REPO:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name GitHubActionsRole \
  --assume-role-policy-document file://github-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess
```

---

## 🐳 Option 1: Elastic Beanstalk (Recommended for Beginners)

### Step 1: Create ECR Repository
```bash
aws ecr create-repository \
  --repository-name breast-cancer-ml \
  --region us-east-1
```

### Step 2: Build and Push Docker Image
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t breast-cancer-ml -f deployment/Dockerfile .

# Tag image
docker tag breast-cancer-ml:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml:latest
```

### Step 3: Configure Elastic Beanstalk

1. **Update `deployment/Dockerrun.aws.json`:**
   ```json
   {
     "AWSEBDockerrunVersion": "1",
     "Image": {
       "Name": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml:latest",
       "Update": "true"
     },
     "Ports": [
       {
         "ContainerPort": 8000,
         "HostPort": 80
       }
     ],
     "Logging": "/var/log/breast-cancer-api"
   }
   ```

2. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

3. **Initialize Beanstalk Application:**
   ```bash
   eb init -p docker breast-cancer-api --region us-east-1
   ```

4. **Create Environment:**
   ```bash
   eb create breast-cancer-api-prod \
     --instance-type t3.small \
     --envvars ENVIRONMENT=production
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

6. **Open Application:**
   ```bash
   eb open
   ```

### Step 4: Set Up Auto-Scaling
```bash
# Configure auto-scaling
eb config

# Edit the configuration to add:
# aws:autoscaling:asg:
#   MinSize: 1
#   MaxSize: 4
# aws:autoscaling:trigger:
#   MeasureName: CPUUtilization
#   Statistic: Average
#   Unit: Percent
#   UpperThreshold: 70
#   LowerThreshold: 20
```

---

## 🚀 Option 2: ECS Fargate (Recommended for Production)

### Step 1: Create ECS Cluster
```bash
aws ecs create-cluster \
  --cluster-name ml-cluster \
  --region us-east-1
```

### Step 2: Create Task Definition
```bash
# Create task-definition.json
cat > task-definition.json << EOF
{
  "family": "breast-cancer-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "breast-cancer-api",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-ml:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/breast-cancer-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole"
}
EOF

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

### Step 3: Create Application Load Balancer
```bash
# Create security group for ALB
aws ec2 create-security-group \
  --group-name breast-cancer-alb-sg \
  --description "Security group for breast cancer API ALB" \
  --vpc-id YOUR_VPC_ID

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
  --group-id YOUR_ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Create ALB
aws elbv2 create-load-balancer \
  --name breast-cancer-alb \
  --subnets YOUR_SUBNET_1 YOUR_SUBNET_2 \
  --security-groups YOUR_ALB_SG_ID

# Create target group
aws elbv2 create-target-group \
  --name breast-cancer-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id YOUR_VPC_ID \
  --target-type ip \
  --health-check-path /health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn YOUR_ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=YOUR_TG_ARN
```

### Step 4: Create ECS Service
```bash
# Create service
aws ecs create-service \
  --cluster ml-cluster \
  --service-name breast-cancer-api \
  --task-definition breast-cancer-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[YOUR_SUBNET_1,YOUR_SUBNET_2],securityGroups=[YOUR_SG_ID],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=YOUR_TG_ARN,containerName=breast-cancer-api,containerPort=8000"
```

### Step 5: Configure Auto-Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/ml-cluster/breast-cancer-api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/ml-cluster/breast-cancer-api \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## ⚡ Option 3: AWS Lambda (Advanced)

### Step 1: Install Serverless Framework
```bash
npm install -g serverless
```

### Step 2: Create `serverless.yml`
```yaml
service: breast-cancer-api

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 1024
  timeout: 30

functions:
  predict:
    handler: lambda_handler.handler
    events:
      - http:
          path: /predict
          method: post
    layers:
      - arn:aws:lambda:us-east-1:ACCOUNT_ID:layer:sklearn-numpy:1

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
```

### Step 3: Create Lambda Handler
```python
# lambda_handler.py
import json
from api.main import predict

def handler(event, context):
    body = json.loads(event['body'])
    result = predict(body)

    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
```

### Step 4: Deploy
```bash
serverless deploy
```

---

## 🔐 Security Best Practices

### 1. Use Secrets Manager for Sensitive Data
```bash
aws secretsmanager create-secret \
  --name breast-cancer-api/database \
  --secret-string '{"username":"admin","password":"secure_password"}'
```

### 2. Enable VPC Endpoints for ECR
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id YOUR_VPC_ID \
  --service-name com.amazonaws.us-east-1.ecr.dkr \
  --route-table-ids YOUR_ROUTE_TABLE_ID
```

### 3. Use IAM Roles (Never Hard-Code Credentials)

### 4. Enable CloudWatch Logging
```bash
aws logs create-log-group --log-group-name /ecs/breast-cancer-api
```

---

## 📊 Monitoring & Observability

### CloudWatch Dashboard
```bash
aws cloudwatch put-dashboard \
  --dashboard-name BreastCancerAPI \
  --dashboard-body file://dashboard.json
```

### Set Up Alarms
```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name breast-cancer-api-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# 5xx errors alarm
aws cloudwatch put-metric-alarm \
  --alarm-name breast-cancer-api-5xx-errors \
  --alarm-description "Alert on 5xx errors" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 💰 Cost Estimation

### Elastic Beanstalk
- t3.small instance: ~$15/month
- Load Balancer: ~$20/month
- Total: **~$35-50/month**

### ECS Fargate
- 2 tasks (0.5 vCPU, 1GB RAM): ~$30/month
- ALB: ~$20/month
- Total: **~$50-70/month**

### Lambda
- 1M requests/month: ~$0.20
- Minimal when idle: **~$5-20/month**

---

## 🧪 Testing Deployment

### Test Health Endpoint
```bash
curl https://your-api.region.elasticbeanstalk.com/health
```

### Test Prediction Endpoint
```bash
curl -X POST "https://your-api.region.elasticbeanstalk.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471,
                 0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904,
                 0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0,
                 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189]
  }'
```

---

## 🔄 GitHub Actions Secrets

Add these secrets to your GitHub repository:

1. **AWS_ACCESS_KEY_ID**
2. **AWS_SECRET_ACCESS_KEY**
3. **AWS_REGION** (e.g., us-east-1)
4. **ECR_REPOSITORY** (e.g., breast-cancer-ml)

---

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Elastic Beanstalk Guide](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [GitHub Actions AWS Integration](https://github.com/aws-actions)

---

**Need Help?** Open an issue on GitHub or consult AWS documentation.
