pipeline {
    agent any
    
    parameters {
        string(name: 'VERSION', defaultValue: 'latest', description: 'Git tag to build')
    }
    
    // ⚠️ NEVER hardcode creds here! Use Jenkins Credentials
    environment {
        SUPABASE_URL = credentials('supabase-url')      // Jenkins credential ID
        SUPABASE_KEY = credentials('supabase-key')      // Jenkins credential ID
    }
    
    stages {
        stage('Checkout Version') {
            steps {
                script {
                    checkout scm
                    if (params.VERSION != 'latest') {
                        git branch: 'main', tag: params.VERSION
                        echo "✓ Checked out ${params.VERSION}"
                    }
                }
            }
        }
        
        stage('Lint & Test') {
            steps {
                sh '''
                pip install --upgrade pip
                pip install -r requirements.txt .
                pytest -v
                '''
            }
        }
        
        stage('Build Docker') {
            steps {
                sh "docker build -t aceest-app:${params.VERSION} ."
                echo "✓ Docker image: aceest-app:${params.VERSION}"
            }
        }
        
        stage('Quality Gate') {
            steps {
                sh '''
                docker run --rm \
                  -e SUPABASE_URL="$SUPABASE_URL" \
                  -e SUPABASE_KEY="$SUPABASE_KEY" \
                  aceest-app:${VERSION} \
                  curl -f http://localhost:5000/ || exit 1
                '''
                echo "✅ Quality gate passed!"
            }
        }
    }
    
    post {
        always {
            echo "Build complete: aceest-app:${params.VERSION}"
        }
    }
}
