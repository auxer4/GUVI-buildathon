# Deployment Guide - Scam Intelligence Engine

## Deployment Options

### Option 1: Local Development

#### Prerequisites
- Python 3.8+
- pip package manager
- (Optional) Redis server

#### Steps

1. **Clone/Download Repository**
```bash
cd path/to/GUVI
```

2. **Create Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # Linux/Mac
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **(Optional) Start Redis**
```bash
# Windows: Use Redis installer or Docker
redis-server

# Linux: apt-get install redis-server && redis-server
# Mac: brew install redis && redis-server
```

5. **Run Application**
```bash
python main.py
```

6. **Access Application**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

### Option 2: Docker (Single Container)

#### Prerequisites
- Docker installed
- Docker Compose (optional)

#### Steps

1. **Build Image**
```bash
docker build -t scam_engine:latest .
```

2. **Run Container**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -e REDIS_HOST=host.docker.internal \
  scam_engine:latest
```

3. **Access Application**
- API: http://localhost:8000
- Logs: Check `logs/` directory

---

### Option 3: Docker Compose (Recommended)

#### Prerequisites
- Docker and Docker Compose installed

#### Steps

1. **Start Services**
```bash
docker-compose up -d
```

2. **Verify Services**
```bash
docker-compose ps
```

3. **View Logs**
```bash
docker-compose logs -f scam_engine
```

4. **Access Application**
- API: http://localhost:8000
- Redis: localhost:6379

5. **Stop Services**
```bash
docker-compose down
```

---

### Option 4: Cloud Deployment (Azure)

#### Prerequisites
- Azure account
- Azure CLI installed

#### Steps

1. **Create Azure Container Registry**
```bash
az group create --name scam-engine-rg --location eastus

az acr create --resource-group scam-engine-rg \
  --name scamengineacr --sku Basic
```

2. **Build and Push Image**
```bash
az acr build --registry scamengineacr \
  --image scam_engine:latest .
```

3. **Create Container Instance**
```bash
az container create \
  --resource-group scam-engine-rg \
  --name scam-engine-container \
  --image scamengineacr.azurecr.io/scam_engine:latest \
  --registry-login-server scamengineacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8000 \
  --cpu 2 \
  --memory 4
```

4. **Create Azure Database for Redis**
```bash
az redis create \
  --resource-group scam-engine-rg \
  --name scam-engine-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

5. **Configure Environment Variables**
```bash
az container create ... \
  --environment-variables \
    REDIS_HOST=scam-engine-redis.redis.cache.windows.net \
    REDIS_PORT=6379
```

---

### Option 5: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (minikube, EKS, AKS, GKE)
- kubectl installed

#### Steps

1. **Create Docker Image**
```bash
docker build -t scam_engine:1.0.0 .
docker push your-registry/scam_engine:1.0.0
```

2. **Create Kubernetes Manifests**

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scam-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scam-engine
  template:
    metadata:
      labels:
        app: scam-engine
    spec:
      containers:
      - name: scam-engine
        image: your-registry/scam_engine:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: scam-engine-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: scam-engine
```

3. **Deploy to Kubernetes**
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Monitor deployment
kubectl get pods
kubectl logs <pod-name>
```

---

## Environment Configuration

### Development (.env)
```
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=DEBUG
PYTHONUNBUFFERED=1
```

### Production (.env)
```
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_password
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
CORS_ORIGINS=https://yourdomain.com
API_KEY_ENABLED=true
```

---

## Performance Tuning

### Uvicorn Workers
```bash
uvicorn main:app --workers 4 --port 8000
```

### Redis Connection Pool
- Adjust `redis_client.py` pool size for high throughput
- Default: 10 connections

### Database Optimization
- Enable Redis persistence: `--appendonly yes`
- Use Redis cluster for high availability

---

## Monitoring & Logging

### Log File Locations
- Application: `logs/scam_engine.log`
- Errors: `logs/errors.log`

### Monitoring Endpoints
- Health: `GET /health`
- System Info: `GET /system/info`

### Alerting (Recommended)
- Monitor error logs for exceptions
- Track detection accuracy metrics
- Alert on service downtime

---

## Security Checklist

- [ ] Use HTTPS in production (reverse proxy)
- [ ] Enable Redis authentication
- [ ] Implement API rate limiting
- [ ] Use API keys for external access
- [ ] Sanitize all inputs
- [ ] Enable CORS only for trusted origins
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Log audit trail
- [ ] Implement request signing

---

## Troubleshooting

### Container Won't Start
```bash
# View logs
docker logs scam_engine

# Rebuild image
docker build -t scam_engine:latest --no-cache .
```

### Redis Connection Issues
```bash
# Verify Redis is running
redis-cli ping

# Check Redis logs
docker logs scam_engine_redis
```

### High Memory Usage
- Reduce number of workers
- Clear old logs: `rm logs/scam_engine.log`
- Increase Redis memory limit

### Slow API Responses
- Check system resources
- Monitor number of concurrent connections
- Review detection pipeline performance

---

## Backup & Recovery

### Backup Redis Data
```bash
# Using Docker
docker exec scam_engine_redis redis-cli BGSAVE

# Manual backup
cp -r /var/lib/redis /backup/redis_backup
```

### Restore Redis Data
```bash
# Copy backup back
cp -r /backup/redis_backup /var/lib/redis

# Restart service
docker-compose restart redis
```

---

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use shared Redis instance
- Use distributed session storage

### Vertical Scaling
- Increase CPU/memory resources
- Optimize detector algorithms
- Use caching for repeated analyses

### Database Scaling
- Redis clustering
- Read replicas
- Sharding by conversation_id

---

## Support & Maintenance

- Monitor logs regularly
- Update dependencies monthly
- Review security advisories
- Performance benchmarking
- Regular backups

---

**Last Updated**: February 5, 2025
**Recommended**: Docker Compose for development, Kubernetes for production
