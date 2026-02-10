# Get API Endpoint URL After Deployment

After your GitHub Actions CD pipeline deploys to AWS ECS, use these methods to get your API endpoint URL.

---

## 🎯 Method 1: AWS Console (Easiest)

### For ECS with Public IP:
1. Go to **AWS Console** → **ECS** (https://console.aws.amazon.com/ecs)
2. Click your cluster name (check `ECS_CLUSTER` in GitHub secrets)
3. Click **Services** tab → Click your service name
4. Go to **Tasks** tab
5. Click on the **RUNNING** task
6. Scroll to **Network** section
7. Copy the **Public IP address**

**Your API endpoint:**
```
http://YOUR-PUBLIC-IP:8000
```

### For Application Load Balancer (if configured):
1. Go to **AWS Console** → **EC2** → **Load Balancers**
2. Find your load balancer (usually named after your service)
3. Copy the **DNS name** (e.g., `breast-cancer-alb-123456.us-east-1.elb.amazonaws.com`)

**Your API endpoint:**
```
http://YOUR-ALB-DNS
```

---

## 🖥️ Method 2: AWS CLI (Fastest)

### Get ECS Task Public IP

```powershell
# Set your cluster and service names (from GitHub secrets)
$CLUSTER_NAME = "ml-api-cluster"  # Your ECS_CLUSTER value
$SERVICE_NAME = "breast-cancer-api-service"  # Your ECS_SERVICE value

# Get running task ARN
$TASK_ARN = aws ecs list-tasks `
  --cluster $CLUSTER_NAME `
  --service-name $SERVICE_NAME `
  --desired-status RUNNING `
  --query 'taskArns[0]' `
  --output text

# Get task details with public IP
aws ecs describe-tasks `
  --cluster $CLUSTER_NAME `
  --tasks $TASK_ARN `
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' `
  --output text | ForEach-Object {
    $ENI_ID = $_
    aws ec2 describe-network-interfaces `
      --network-interface-ids $ENI_ID `
      --query 'NetworkInterfaces[0].Association.PublicIp' `
      --output text
  }
```

### Get Load Balancer DNS (if using ALB)

```powershell
# List all load balancers and find yours
aws elbv2 describe-load-balancers `
  --query 'LoadBalancers[*].[LoadBalancerName,DNSName]' `
  --output table

# Or get specific ALB by name
aws elbv2 describe-load-balancers `
  --names breast-cancer-alb `
  --query 'LoadBalancers[0].DNSName' `
  --output text
```

---

## 🔍 Method 3: From GitHub Actions Output

### Add to CD Workflow

Add this step to your `.github/workflows/cd.yml` after the ECS deployment:

```yaml
      - name: Get and display API endpoint
        if: steps.check_promotion.outputs.promoted == 'true'
        run: |
          echo "🔍 Retrieving API endpoint..."

          # Wait for service to stabilize
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE }}

          # Get task ARN
          TASK_ARN=$(aws ecs list-tasks \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service-name ${{ env.ECS_SERVICE }} \
            --desired-status RUNNING \
            --query 'taskArns[0]' \
            --output text)

          # Get ENI ID
          ENI_ID=$(aws ecs describe-tasks \
            --cluster ${{ env.ECS_CLUSTER }} \
            --tasks $TASK_ARN \
            --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
            --output text)

          # Get public IP
          PUBLIC_IP=$(aws ec2 describe-network-interfaces \
            --network-interface-ids $ENI_ID \
            --query 'NetworkInterfaces[0].Association.PublicIp' \
            --output text)

          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "🚀 API ENDPOINT URL"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "http://${PUBLIC_IP}:8000"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo ""
          echo "📝 Test endpoints:"
          echo "Health: http://${PUBLIC_IP}:8000/health"
          echo "Predict: http://${PUBLIC_IP}:8000/predict"
          echo "Docs: http://${PUBLIC_IP}:8000/docs"
```

---

## ✅ Test Your Endpoint

Once you have the URL, test it:

### Test Health Endpoint
```powershell
# Replace with your actual IP or DNS
$API_URL = "http://YOUR-IP-OR-DNS:8000"

# Health check
curl "$API_URL/health"

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### Test Prediction Endpoint
```powershell
# Test prediction
curl -X POST "$API_URL/predict" `
  -H "Content-Type: application/json" `
  -d '{
    "features": {
      "mean_radius": 17.99,
      "mean_texture": 10.38,
      "mean_perimeter": 122.8,
      "mean_area": 1001.0,
      "mean_smoothness": 0.1184,
      "mean_compactness": 0.2776,
      "mean_concavity": 0.3001,
      "mean_concave_points": 0.1471,
      "mean_symmetry": 0.2419,
      "mean_fractal_dimension": 0.07871
    }
  }'
```

### Open API Documentation
```powershell
# Open in browser
Start-Process "$API_URL/docs"
```

---

## 🔐 Security Note

**⚠️ Important**: Your API is currently open to the internet!

### Secure Your API:

1. **Add Authentication** (JWT tokens, API keys)
2. **Configure Security Groups** (limit IP ranges)
3. **Use HTTPS** (add Load Balancer with SSL certificate)
4. **Set up AWS WAF** (Web Application Firewall)

### Quick Security Group Fix:
```powershell
# Find your security group
aws ec2 describe-security-groups `
  --filters "Name=group-name,Values=*ecs*" `
  --query 'SecurityGroups[*].[GroupId,GroupName]' `
  --output table

# Restrict to your IP only (for testing)
$YOUR_IP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content
aws ec2 authorize-security-group-ingress `
  --group-id YOUR-SECURITY-GROUP-ID `
  --protocol tcp `
  --port 8000 `
  --cidr "$YOUR_IP/32"
```

---

## 📊 Monitoring

### Check CloudWatch Logs
```powershell
# View recent logs
aws logs tail /ecs/breast-cancer-api --follow
```

### Monitor ECS Service
```powershell
# Get service status
aws ecs describe-services `
  --cluster $CLUSTER_NAME `
  --services $SERVICE_NAME `
  --query 'services[0].[serviceName,status,runningCount,desiredCount]' `
  --output table
```

---

## 🛠️ Troubleshooting

### Issue: Can't connect to endpoint
- ✅ Check security group allows inbound on port 8000
- ✅ Verify task is RUNNING (not PENDING/STOPPED)
- ✅ Confirm public IP is assigned
- ✅ Check CloudWatch logs for errors

### Issue: Health check fails
- ✅ Wait 60-120 seconds after deployment
- ✅ Verify container started successfully
- ✅ Check `/health` endpoint path is correct
- ✅ Review application logs in CloudWatch

### Issue: Getting 502/503 errors
- ✅ Application failed to start - check logs
- ✅ Container crashed - check memory/CPU limits
- ✅ Model files missing - verify Docker build
- ✅ Port mismatch - must expose 8000

---

## 🎯 Next Steps

1. **Save your endpoint URL** for future use
2. **Test all API endpoints** (health, predict, docs)
3. **Set up custom domain** (optional, using Route 53)
4. **Configure HTTPS** (using ACM + ALB)
5. **Add monitoring alerts** (CloudWatch alarms)
6. **Implement authentication** (API Gateway + Cognito)
