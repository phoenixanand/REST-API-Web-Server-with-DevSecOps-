pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock'

        }
    }
    environment {

    }
    stages {
        stage('Clean') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt'''
            }
        }
        stage('Pytest') {
            steps {
                sh '''. venv/bin/activate
                pytest -v -s test/test_user.py --cov=app '''
            }
        }
        // stage('Coverage') {
        //     steps {
        //         sh '''. venv/bin/activate
        //         pytest --cov=app'''
        //     }
        // }
        stage('SonarQube') {
            agent {
                    docker {
                        image 'sonarsource/sonar-scanner-cli:latest'
                        args '--network devops-net'
                        reuseNode true          
                    }
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh "sonar-scanner"
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('Secret Scan') {
            agent {
                docker {
                    image 'zricethezav/gitleaks:latest'
                    reuseNode true
                }
            }
            steps {
                sh '''gitleaks detect . '''
            }
        }
        stage('Filesystem Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                    reuseNode true
                }
            }
            steps {
                sh 'trivy fs .'
            }
        }
        stage('Hadolint') {
            agent {
                docker {
                    image 'hadolint/hadolint:latest'
                    reuseNode true
                }
            }
            steps {
                sh 'hadolint Dockerfile'
            }
        }
        stage('Checkov') {
            agent {
                docker {
                    image 'bridgecrew/checkov:latest'
                    reuseNode true
                }
            }
            steps {
                sh 'checkov -d .'
            } 
        }
        
        stage('Docker Build and Push') {
            agent {
                docker {
                    image 'docker:24-cli'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'docker build -t $DOCKER_USER/fastapi:${BUILD_NUMBER} -t $DOCKER_USER/fastapi:latest .
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_USER/fastapi:${BUILD_NUMBER}
                    docker push $DOCKER_USER/fastapi:latest
                    '
                }
            }
        }

        stage('Image Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                    reuseNode true
                }
            }
            steps {
                sh ' trivy image alphaman02/fastapi:${BUILD_NUMBER} '
            }
        }
        stage('Update Manifest') {
            steps {
                sh ' sed -i "s/latest/${BUILD_NUMBER}/g" kubernetes/deployment.yaml'
            }
        } 
    }

    post {

        success {
            emailext(
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """ Build completed successfully Job Name: ${env.JOB_NAME}
                Build Number: ${env.BUILD_NUMBER} Build URL: ${env.BUILD_URL}
                Status: SUCCESS""",
                to: "team@example.com"
            )
        }   
    
        failure {
            emailext(
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """Build failed
                Job Name: ${env.JOB_NAME}
                Build Number: ${env.BUILD_NUMBER}
                Build URL: ${env.BUILD_URL}
            Please check Jenkins logs""",
                to: "team@example.com"
            )
        }
        unstable {
            emailext(
                subject: "UNSTABLE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """Build is unstable
                Job Name: ${env.JOB_NAME}
                Build Number: ${env.BUILD_NUMBER}
                Build URL: ${env.BUILD_URL}""",
                to: "team@example.com"
            )
        }
        always {
            echo "Pipeline completed"
        }
    }
}


