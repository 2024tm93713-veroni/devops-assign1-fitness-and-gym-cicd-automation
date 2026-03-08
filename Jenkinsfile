pipeline {
    agent any

    parameters {
        string(name: 'VERSION', defaultValue: 'latest', description: 'ACEest API version')
    }

    environment {
        DOCKER_IMAGE = "aceest-api-local"
        TAG = "${params.VERSION}"
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

        stage('Docker Build') {
            steps {
                sh '''
                # Pick version based on VERSION param
                if [ "$VERSION" = "v1.0.0" ]; then
                    cp app_v1.py app.py
                elif [ "$VERSION" = "v2.0.0" ]; then
                    cp app_v2.py app.py
                else
                    cp app_v3.py app.py
                fi
                
                docker build -t $DOCKER_IMAGE:$TAG .
                '''
            }
        }

        stage('Docker Test') {
            steps {
                sh '''
                docker run -d --name aceest-test -p 5000:5000 $DOCKER_IMAGE:$TAG
                sleep 10
                curl -f http://localhost:5000/health || (echo "Health check failed" && exit 1)
                docker rm -f aceest-test
                echo "✓ Docker test passed for $TAG"
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                # Stop any old containers
                docker rm -f aceest-prod || true
                # Run production
                docker run -d --name aceest-prod -p 8080:5000 $DOCKER_IMAGE:$TAG
                echo "✓ Deployed $TAG to http://localhost:8080"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker ps -a'
        }
    }
}
