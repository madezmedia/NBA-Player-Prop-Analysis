# Deployment Guide for NBA Player Prop Analysis

## Deployment Options

### 1. Local Docker Deployment

#### Prerequisites
- Docker installed
- Docker Compose installed
- Git
- `.env` file configured (use `.env.example` as a template)

#### Steps
1. Clone the repository
```bash
git clone https://github.com/your-username/nba-player-prop-analysis.git
cd nba-player-prop-analysis
```

2. Copy and customize environment variables
```bash
cp .env.example .env
# Edit .env with your specific configuration
```

3. Build and Run with Docker Compose
```bash
docker-compose up --build
```

#### Access the Application
- Local URL: http://localhost:3001 (default port)
- Customizable via `DOCKER_HOST_PORT` in `.env`

### 2. Elest.io Deployment

#### Configuration Steps

1. **Project Setup**
   - Create a new project on Elest.io
   - Select Docker Container deployment type
   - Connect to your GitHub repository

2. **Docker Configuration**
   - **Build Command**: 
     ```
     docker build -t nba-player-prop-analysis .
     ```
   - **Start Command**: 
     ```
     docker run -p 3001:8080 nba-player-prop-analysis
     ```

3. **Environment Variables**
   Configure the following in Elest.io dashboard:
   ```
   STREAMLIT_SERVER_PORT=8080
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   STREAMLIT_SERVER_ENABLE_CORS=false
   STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   
   # Add your API keys and other sensitive configurations
   OPENAI_API_KEY=your_key
   RAPIDAPI_KEY=your_key
   ```

4. **Deployment Settings**
   - **Container Port**: 8080
   - **Host Port**: 3001
   - **Interface**: 172.17.0.1
   - **Protocol**: HTTP
   - **Health Check Path**: /_stcore/health
   - **Memory**: At least 1GB
   - **CPU**: At least 1 vCPU

### 3. Advanced Deployment Configurations

#### Port Customization
- Modify `DOCKER_HOST_PORT` in `.env`
- Update `CONTAINER_INTERNAL_PORT` in Dockerfile
- Adjust docker-compose.yml port mappings

#### Security Considerations
- Never commit sensitive information to repository
- Use environment-specific `.env` files
- Rotate API keys regularly
- Implement IP restrictions if possible

### 4. Troubleshooting

#### Common Deployment Issues
1. **Port Conflicts**
   - Ensure port 8080/3001 is available
   - Check for running services on the same port
   - Modify port mappings in `.env`

2. **Environment Variable Problems**
   - Verify all required keys are set
   - Check API key validity
   - Ensure correct formatting

3. **Docker Build Failures**
   - Verify Docker installation
   - Check network connectivity
   - Ensure all dependencies are correctly specified

### 5. Monitoring and Maintenance

#### Logging
- Container logs accessible via:
  ```bash
  docker-compose logs app
  ```
- Application logs in `logs/` directory

#### Performance Monitoring
- Use Docker stats: `docker stats`
- Monitor Elest.io dashboard metrics
- Implement application-level logging

### 6. Continuous Deployment

#### GitHub Actions Workflow
```yaml
name: Docker Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and Push to Elest.io
      run: |
        docker build -t nba-player-prop-analysis .
        # Add Elest.io deployment script
```

### 7. Scaling Considerations
- Horizontal scaling via container orchestration
- Implement caching mechanisms
- Optimize database queries
- Use load balancing for high traffic

## Recommended Next Steps
1. Review security configurations
2. Set up comprehensive monitoring
3. Implement CI/CD pipeline
4. Regular dependency updates
5. Performance optimization
