pipeline {
    agent any

    parameters {
        string(name: 'VERSION', defaultValue: 'latest', description: 'ACEest API version')
    }

    environment {
        DOCKER_IMAGE = "2024tm93713/aceest-app-2024tm93713"
        TAG = "${params.VERSION}"
        CONTAINER_NAME = "aceest-prod"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Tests') {
            steps {
                bat '''
                python -m venv venv
                call venv\\Scripts\\activate
                pip install -r requirements.txt pytest
                pytest
                '''
            }
        }

        stage('Checkout Version') {
            steps {
                bat '''
                git checkout %VERSION%
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                docker build -t $DOCKER_IMAGE:$TAG .
                '''
            }
        }

        stage('Test Inside Container') {
            steps {
                bat '''
                docker run --del $DOCKER_IMAGE:$TAG pytest || exit 1
                echo "✓ Container tests passed"
                '''
            }
        }

        stage('Docker Health Check') {
            steps {
                bat '''
                docker run -d --name aceest-test -p 5000:5000 $DOCKER_IMAGE:$TAG
                timeout /t 10
                curl -f http://localhost:5000/ || (echo "Health check failed" && exit 1)
                docker del -f aceest-test
                echo "✓ Health check passed"
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_IMAGE:$TAG
                    '''
                }
            }
        }

        stage('Deploy (Local Docker)') {
            steps {
                bat '''
                docker del -f $CONTAINER_NAME || true
                docker run -d --name $CONTAINER_NAME -p 8080:5000 $DOCKER_IMAGE:$TAG
                echo "✓ Deployed $TAG locally at http://localhost:8080"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    bat '''
                    sonar-scanner \
                    -Dsonar.projectKey=aceest \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://localhost:9000 \
                    -Dsonar.login=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful for version ${TAG}"
        }
        failure {
            echo "❌ Build failed. Consider rollback"

            bat '''
            echo "Rolling back to previous container (if exists)..."
            docker ps -a
            '''
        }
        always {
            bat 'docker system prune -f'
        }
    }
}