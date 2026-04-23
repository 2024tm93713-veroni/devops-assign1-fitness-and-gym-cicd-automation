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
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt pytest
                pytest
                '''
            }
        }

        stage('Select Version') {
            steps {
                sh '''
                echo "Using version: $VERSION"

                if [ "$VERSION" = "v1.0.0" ]; then
                    cp app_v1.py app.py
                elif [ "$VERSION" = "v2.0.0" ]; then
                    cp app_v2.py app.py
                else
                    cp app_v3.py app.py
                fi
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $DOCKER_IMAGE:$TAG .
                '''
            }
        }

        stage('Test Inside Container') {
            steps {
                sh '''
                docker run --rm $DOCKER_IMAGE:$TAG pytest || exit 1
                echo "✓ Container tests passed"
                '''
            }
        }

        stage('Docker Health Check') {
            steps {
                sh '''
                docker run -d --name aceest-test -p 5000:5000 $DOCKER_IMAGE:$TAG
                sleep 10
                curl -f http://localhost:5000/ || (echo "Health check failed" && exit 1)
                docker rm -f aceest-test
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
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_IMAGE:$TAG
                    '''
                }
            }
        }

        stage('Deploy (Local Docker)') {
            steps {
                sh '''
                docker rm -f $CONTAINER_NAME || true
                docker run -d --name $CONTAINER_NAME -p 8080:5000 $DOCKER_IMAGE:$TAG
                echo "✓ Deployed $TAG locally at http://localhost:8080"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
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

            sh '''
            echo "Rolling back to previous container (if exists)..."
            docker ps -a
            '''
        }
        always {
            sh 'docker system prune -f'
        }
    }
}