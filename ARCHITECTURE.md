# Project Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Data Layer"
        DS[(Kaggle Dataset<br/>Wisconsin Breast Cancer)]
        DV[Data Version<br/>SHA256 Hash]
    end

    subgraph "Training Pipeline"
        LD[Load Data]
        PP[Preprocess]
        CV[10-Fold<br/>Cross-Validation]
        TR[Train Final Model]
        EV[Evaluate on Test Set]
    end

    subgraph "MLflow Tracking"
        ML[MLflow Server]
        PAR[Parameters]
        MET[Metrics]
        ART[Artifacts]
    end

    subgraph "Model Promotion"
        CHK{Check<br/>Thresholds}
        PROMO[Promote to<br/>models/latest/]
        REJECT[Log Only]
    end

    subgraph "API Layer"
        API[FastAPI Server]
        PRED[/predict Endpoint]
        HEALTH[/health Endpoint]
    end

    subgraph "Deployment"
        DOCK[Docker Container]
        ECR[AWS ECR]
        ECS[AWS ECS/Fargate]
        EB[Elastic Beanstalk]
    end

    subgraph "CI/CD"
        GHA[GitHub Actions]
        CI[CI Pipeline<br/>Test & Validate]
        CD[CD Pipeline<br/>Build & Deploy]
    end

    DS --> LD
    DV --> LD
    LD --> PP
    PP --> CV
    CV --> TR
    TR --> EV

    EV --> PAR
    EV --> MET
    EV --> ART

    PAR --> ML
    MET --> ML
    ART --> ML

    EV --> CHK
    CHK -->|Recall ≥ 95%<br/>Std ≤ 5%| PROMO
    CHK -->|Criteria Not Met| REJECT

    PROMO --> API
    API --> PRED
    API --> HEALTH

    PROMO --> DOCK
    DOCK --> ECR
    ECR --> ECS
    ECR --> EB

    GHA --> CI
    GHA --> CD
    CI --> TR
    CD --> DOCK

    style PROMO fill:#90EE90
    style REJECT fill:#FFB6C1
    style ML fill:#87CEEB
    style API fill:#DDA0DD
```

## Training Workflow

```mermaid
sequenceDiagram
    participant User
    participant Train as train.py
    participant MLflow
    participant Model as Model Registry
    participant Disk as models/latest/

    User->>Train: python train.py
    Train->>Train: Load & Preprocess Data
    Train->>Train: Compute Data Hash
    Train->>MLflow: Log data_version

    Train->>Train: 10-Fold CV
    Train->>MLflow: Log CV metrics (mean ± std)

    Train->>Train: Train Final Model
    Train->>Train: Evaluate on Test Set
    Train->>MLflow: Log test metrics

    Train->>Train: Generate Artifacts
    Train->>MLflow: Log artifacts (cm, report, model)

    Train->>Train: Check Promotion Criteria

    alt Recall ≥ 95% AND Std ≤ 5%
        Train->>Disk: Copy to models/latest/
        Train->>Disk: Save promotion_metadata.json
        Train->>User: ✅ Model Promoted!
    else Criteria Not Met
        Train->>User: ❌ Model Not Promoted
    end

    Train->>MLflow: Mark run complete
    User->>MLflow: View in UI (mlflow ui)
```

## API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Model as Loaded Model
    participant MLflow

    Client->>API: GET /health
    API-->>Client: {status: healthy, model_status: loaded}

    Client->>API: POST /predict<br/>{features: [30 values]}
    API->>API: Validate Input (Pydantic)
    API->>Model: model.predict(features)
    Model-->>API: prediction, probability
    API->>API: Determine confidence level
    API-->>Client: {prediction: 1, label: "Malignant",<br/>probability: 0.92, confidence: "high"}

    Client->>API: GET /model/info
    API->>API: Load promotion_metadata.json
    API-->>Client: {model_type, promotion_metadata}
```

## CI/CD Pipeline Flow

```mermaid
graph LR
    subgraph "Developer Workflow"
        DEV[Developer]
        CODE[Write Code]
        COMMIT[Git Commit]
        PR[Open PR]
    end

    subgraph "CI Pipeline (On PR)"
        LINT[Code Quality<br/>black, flake8]
        TEST[Unit Tests<br/>pytest]
        SMOKE[Smoke Test<br/>train --smoke]
        CHECK[Validate Artifacts]
    end

    subgraph "CD Pipeline (On Release)"
        TAG[Git Tag v1.0.0]
        TRAIN[Full Training]
        PROMOTE{Model<br/>Promoted?}
        BUILD[Build Docker]
        PUSH[Push to ECR]
        DEPLOY[Deploy to AWS]
        RELEASE[GitHub Release]
    end

    DEV --> CODE
    CODE --> COMMIT
    COMMIT --> PR

    PR --> LINT
    LINT --> TEST
    TEST --> SMOKE
    SMOKE --> CHECK

    TAG --> TRAIN
    TRAIN --> PROMOTE
    PROMOTE -->|Yes| BUILD
    PROMOTE -->|No| FAIL[❌ Stop]
    BUILD --> PUSH
    PUSH --> DEPLOY
    DEPLOY --> RELEASE

    style PROMOTE fill:#FFD700
    style DEPLOY fill:#90EE90
    style FAIL fill:#FF6B6B
```

## AWS Deployment Architecture

```mermaid
graph TB
    subgraph "GitHub"
        GH[GitHub Repository]
        ACT[GitHub Actions]
    end

    subgraph "AWS Services"
        ECR[Amazon ECR<br/>Container Registry]

        subgraph "Compute Options"
            EB[Elastic Beanstalk<br/>Simplest]
            ECS[ECS Fargate<br/>Production]
            LAMBDA[Lambda<br/>Serverless]
        end

        ALB[Application<br/>Load Balancer]
        CW[CloudWatch<br/>Monitoring]
        SM[Secrets Manager]
    end

    subgraph "External"
        USER[End Users]
    end

    GH --> ACT
    ACT -->|docker push| ECR

    ECR --> EB
    ECR --> ECS
    ECR --> LAMBDA

    USER --> ALB
    ALB --> ECS
    USER --> EB
    USER --> LAMBDA

    ECS --> CW
    EB --> CW
    LAMBDA --> CW

    ECS --> SM
    EB --> SM

    style ECR fill:#FF9900
    style ECS fill:#FF9900
    style CW fill:#FF9900
```

## Data Flow

```mermaid
graph LR
    A[Raw Dataset<br/>569 samples] --> B[Preprocessing<br/>Drop ID, Encode Target]
    B --> C[Feature-Target Split<br/>X: 30 features<br/>y: 0/1]
    C --> D[Train-Test Split<br/>80/20 Stratified]
    D --> E[Scaling<br/>StandardScaler]
    E --> F[Model Training<br/>Logistic Regression]
    F --> G[Prediction<br/>0=Benign, 1=Malignant]

    style A fill:#FFE4B5
    style G fill:#90EE90
```

---

## Key Design Decisions

### 1. Model Promotion Thresholds
- **Recall ≥ 95%**: Critical for medical diagnosis - minimizes false negatives
- **Std ≤ 5%**: Ensures model stability across different data splits

### 2. MLflow Tracking
- Local file-based tracking for development
- Can be upgraded to remote tracking server for team collaboration

### 3. API Design
- FastAPI for automatic documentation and validation
- Pydantic models for type safety
- Health checks for monitoring

### 4. Deployment Strategy
- Docker for consistency across environments
- Multiple AWS options for different scales
- CI/CD ensures only good models reach production

### 5. Testing Strategy
- Unit tests for core functionality
- Smoke tests in CI (fast, 20% data)
- Full training in CD (before deployment)

---

**For more details, see:**
- [MLFLOW_GUIDE.md](MLFLOW_GUIDE.md) - Training pipeline
- [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md) - AWS deployment
- [README.md](README.md) - Complete documentation
