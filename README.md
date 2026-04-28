#  Automated CI/CD Pipeline Implementation

## Overview
This project demonstrates the implementation of an **Automated CI/CD Pipeline** using modern DevOps tools such as **GitHub Actions, Docker, and Jenkins**. The pipeline ensures continuous integration, automated testing, and reliable deployment workflows.

---

## Git & Branching Strategy
The repository follows a structured branching model:

- **main branch** → Contains stable, production-ready code  
- **feature/** branches → Used for developing new features  
- **bugfix/** branches → Used for fixing defects  
- **enhancement/** branches → Used for improvements  

All changes are integrated via **Pull Requests (PRs)** with automated checks before merging.

---

## Versioning & Triggers
- The pipeline uses **semantic versioning** (e.g., v1.0.1)
- Builds are automatically triggered on:
  - Push events containing version tags  
- Ensures controlled and traceable deployments

---

## GitHub Actions Workflow

Workflow is defined in:

```
.github/workflows/main.yml
```

### Pipeline Stages

1. **Build & Lint**
   - Installs dependencies  
   - Checks for syntax errors  

2. **Docker Image Build**
   - Builds container image using Dockerfile  

3. **Automated Tests**
   - Executes full Pytest test suite inside Docker  

4. **Pre-PR Checks**
   - Validates code automatically before merging PRs  

---

## Jenkins Integration

- Triggered automatically via **GitHub Webhooks**
- Executes:
  - Clean builds  
  - Validation steps in an isolated environment

---

## Ngrok Setup

- Since Jenkins runs locally, **Ngrok** is used to expose it publicly  
- Enables GitHub to trigger Jenkins via webhooks  

---

## Local Setup & Running Tests
### Prerequisites

Ensure the following are installed:

Python 3.11+
pip
Docker

### 1. Clone the repository
### 2. Install dependencies
pip install -r requirements.txt

### 3. Run Tests Locally
Execute:  pytest

---

## Run Tests Using Docker
### 1. Build Docker Image
docker build -t devops-assign1 .

### 2. Run Tests Inside Container
docker run devops-assign1 pytest

### Push Image
```
docker login -u %DOCKER_USER% -p %DOCKER_PASS%
docker push DOCKER_IMAGE:TAG
```

### SonarQube setup in Jenkins
1. Install SonarQube Scanner
2. Save the SonarQube token in Jenkins
3. Add SonarQube server
4. The SonarQube Analysis stage of the pipeline will analyse your code

## Container orchestration

1. Install minikube
2. Run this command to start minikube
```minikube start```

### Deployennt stratergies
1. Each stratergy is created inside k8s folder witha respective folder of it's own
2. A base deployment and service file also exists
3. Update the path according to the stratergy
```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
