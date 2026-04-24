pipeline {
    agent any

    parameters {
        string(name: 'VERSION', defaultValue: 'latest', description: 'ACEest API version')
    }

    environment {
        DOCKER_IMAGE = "2024tm93713/aceest-app-2024tm93713"
        TAG = "${params.VERSION}"
        CONTAINER_NAME = "aceest-prod"
        SUPABASE_URL = credentials('SUPABASE_URL')
        SUPABASE_KEY = credentials('SUPABASE_KEY')
    }
    

    stages {

        stage('Checkout Version') {
            steps {
                bat '''
                git fetch --all --tags
                git checkout tags/%VERSION%
                '''
            }
        }

        stage('Python Tests (Docker)') {
            steps {
                bat '''
                docker build --no-cache -t test-image .
                docker run --rm test-image python -m pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                docker build -t %DOCKER_IMAGE%:%TAG% .
                '''
            }
        }

        stage('Test Inside Container') {
            steps {
                bat '''
                docker run --rm %DOCKER_IMAGE%:%TAG% python -m pytest
                echo "✓ Container tests passed"
                '''
            }
        }

    stage('Docker Health Check') {
        steps {
            bat '''
            echo Cleaning old container...
            docker rm -f aceest-test 2>nul

            echo Starting new container...
            docker run -d --name aceest-test ^
            -p 5000:5000 ^
            -e SUPABASE_URL=%SUPABASE_URL% ^
            -e SUPABASE_KEY=%SUPABASE_KEY% ^
            %DOCKER_IMAGE%:%TAG% || exit /b 1

            echo Waiting for app to start...
            ping 127.0.0.1 -n 15 > nul

            echo Checking logs...
            docker logs aceest-test

            curl -f http://localhost:5000/ || (
                echo "Health check failed"
                docker logs aceest-test
                docker rm -f aceest-test
                exit /b 1
            )

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
                    bat '''
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                    docker push %DOCKER_IMAGE%:%TAG%
                    '''
                }
            }
        }

        stage('Deploy (Local Docker)') {
            steps {
                bat '''
                docker rm -f %CONTAINER_NAME% 2>nul
                docker run -d --name %CONTAINER_NAME% -p 8081:5000 %DOCKER_IMAGE%:%TAG% || exit /b 1
                echo "✓ Deployed %TAG% locally at http://localhost:8081"
                '''
            }
        }

    stage('SonarQube Analysis') {
        steps {
            withSonarQubeEnv('sonar') {
                script {
                    def scannerHome = tool 'sonar-scanner'

                    bat """
                    call "${scannerHome}\\bin\\sonar-scanner.bat" ^
                    -Dsonar.projectKey=aceest ^
                    -Dsonar.sources=. ^
                    -Dsonar.login=%SONAR_AUTH_TOKEN%
                    """
                }
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