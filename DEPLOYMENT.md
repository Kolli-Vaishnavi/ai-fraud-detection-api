# Deployment Guide - AI Fraud Detection API

## Overview

This guide covers deployment options for the AI Fraud Detection API in various environments, from local development to production deployment in low-connectivity environments.

## Prerequisites

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB disk space for models and logs
- Audio processing libraries (automatically installed)

## Quick Start (Local Development)

### Option 1: Using the startup script

```bash
# Make script executable and run
chmod +x scripts/run_server.sh
./scripts/run_server.sh
```

### Option 2: Manual setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p models temp_uploads logs

# Run the API
python app.py
```

The API will be available at `http://localhost:5000`

## Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -f docker/Dockerfile -t fraud-detection-api .

# Run the container
docker run -p 5000:5000 -v $(pwd)/models:/app/models fraud-detection-api
```

### Using Docker Compose

```bash
# Start the service
docker-compose -f docker/docker-compose.yml up -d

# Check logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the service
docker-compose -f docker/docker-compose.yml down
```

## Production Deployment

### Environment Configuration

Create a `.env` file for production settings:

```bash
# .env file
FLASK_ENV=production
API_HOST=0.0.0.0
API_PORT=5000
MAX_CONTENT_LENGTH=52428800  # 50MB
LOG_LEVEL=INFO
MODEL_PATH=models/fraud_model.joblib
```

### Using Gunicorn (Recommended for Production)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Systemd Service (Linux)

Create `/etc/systemd/system/fraud-detection-api.service`:

```ini
[Unit]
Description=AI Fraud Detection API
After=network.target

[Service]
Type=simple
User=fraud-api
WorkingDirectory=/opt/fraud-detection-api
Environment=PATH=/opt/fraud-detection-api/venv/bin
ExecStart=/opt/fraud-detection-api/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable fraud-detection-api
sudo systemctl start fraud-detection-api
sudo systemctl status fraud-detection-api
```

## Offline Environment Deployment

### Air-Gapped Network Setup

1. **Prepare offline package bundle:**

```bash
# On internet-connected machine
pip download -r requirements.txt -d offline_packages/

# Transfer offline_packages/ to target machine
```

2. **Install on offline machine:**

```bash
# Install from local packages
pip install --no-index --find-links offline_packages/ -r requirements.txt
```

3. **Pre-trained model deployment:**

```bash
# Train model on internet-connected machine with larger dataset
python -c "
from src.model_trainer import ModelTrainer
trainer = ModelTrainer()
trainer.train_model({'training_data': trainer.get_default_training_data()})
"

# Transfer models/ directory to offline machine
```

### Low-Connectivity Environment

For environments with limited internet access:

1. **Minimal installation:**
   - Use lightweight Python distribution
   - Pre-download all dependencies
   - Use compressed model files

2. **Resource optimization:**
   - Reduce model complexity if needed
   - Implement model caching
   - Use efficient audio processing

## Load Balancing and Scaling

### Nginx Configuration

```nginx
upstream fraud_detection_api {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}

server {
    listen 80;
    server_name fraud-detection.example.com;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://fraud_detection_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### Multiple Instance Setup

```bash
# Start multiple instances on different ports
gunicorn --bind 0.0.0.0:5001 --workers 2 app:app &
gunicorn --bind 0.0.0.0:5002 --workers 2 app:app &
gunicorn --bind 0.0.0.0:5003 --workers 2 app:app &
gunicorn --bind 0.0.0.0:5004 --workers 2 app:app &
```

## Security Considerations

### API Key Management

For production, replace the sandbox API key:

```python
# In app.py, replace:
SANDBOX_API_KEY = "sandbox_key_12345"

# With secure key generation:
import secrets
API_KEY = secrets.token_urlsafe(32)
```

### HTTPS Configuration

```bash
# Generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with HTTPS
gunicorn --bind 0.0.0.0:5000 --certfile cert.pem --keyfile key.pem app:app
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 5000/tcp
sudo ufw enable
```

## Monitoring and Logging

### Log Configuration

The API automatically logs to:
- `fraud_detection.log` - Application logs
- Console output - Real-time monitoring

### Health Monitoring

```bash
# Simple health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/health)
if [ $response -eq 200 ]; then
    echo "API is healthy"
else
    echo "API is down - Status: $response"
    # Restart service if needed
    systemctl restart fraud-detection-api
fi
```

### Performance Monitoring

Monitor these metrics:
- Response time per endpoint
- Memory usage
- CPU utilization
- Model accuracy over time
- Error rates

## Backup and Recovery

### Model Backup

```bash
# Backup models and configuration
tar -czf fraud-detection-backup-$(date +%Y%m%d).tar.gz models/ logs/ *.json

# Restore from backup
tar -xzf fraud-detection-backup-20260201.tar.gz
```

### Database Backup (if using external storage)

```bash
# For future database integration
# pg_dump fraud_detection > backup.sql
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process if needed
kill -9 <PID>
```

2. **Memory issues:**
```bash
# Monitor memory usage
free -h
# Reduce model complexity or increase swap
```

3. **Audio processing errors:**
```bash
# Install audio libraries
sudo apt-get install portaudio19-dev python3-pyaudio
```

4. **Permission errors:**
```bash
# Fix file permissions
chmod -R 755 models/ temp_uploads/ logs/
```

### Log Analysis

```bash
# Check application logs
tail -f fraud_detection.log

# Check system logs
journalctl -u fraud-detection-api -f
```

## Performance Tuning

### Model Optimization

- Use smaller vocabulary size for TF-IDF
- Implement model quantization
- Cache frequent predictions
- Use batch processing for multiple requests

### System Optimization

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python garbage collection
export PYTHONOPTIMIZE=1
```

## Testing Deployment

After deployment, run the test suite:

```bash
# Run API tests
python test_api.py

# Run sample analysis
python examples/sample_requests.py

# Run shell tests
./scripts/test_api.sh
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Model retraining** - Weekly/monthly with new data
2. **Log rotation** - Prevent disk space issues
3. **Security updates** - Keep dependencies updated
4. **Performance monitoring** - Track response times
5. **Backup verification** - Test restore procedures

### Updating the API

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
systemctl restart fraud-detection-api
```

This deployment guide ensures the AI Fraud Detection API can be successfully deployed in various environments while maintaining security, performance, and reliability.