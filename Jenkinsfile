pipeline {
    agent {
        docker {
            image 'alphaman02/new-python:1.0'
            args '-v /var/run/docker.sock:/var/run/docker.sock  --network devops-net --group-add 110'

        }
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
        stage('Setup Env') {
            steps {
                withCredentials([file(credentialsId: 'app-env-file', variable: 'ENV_FILE')]) {
                    sh 'cp $ENV_FILE .env'
                }
            }
        }
        stage('Pytest') {
            steps {
                sh '''. venv/bin/activate
                pytest -v -s test/test_user.py --cov=app '''
            }
        }
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
                    args '--entrypoint=""'
                    reuseNode true
                }
            }
            steps {
                sh '''gitleaks detect . --no-git -v  || true '''
            }
        }
        stage('Filesystem Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                    args '--entrypoint=""'
                    reuseNode true
                }
            }
            steps {
                sh 'trivy fs . --cache-dir .trivycache'
            }
        }
        stage('Hadolint') {
            steps {
                sh 'docker run --rm -i hadolint/hadolint:latest < Dockerfile || true'
            }
        }
        stage('Checkov') {
            agent {
                docker {
                    image 'bridgecrew/checkov:latest'
                    args '--entrypoint=""'
                    reuseNode true
                }
            }
            steps {
                sh 'checkov -d . --skip-path venv --skip-path .git || true'
            } 
        }
        
        stage('Docker Build and Push') {
            agent {
                docker {
                    image 'docker:27-cli'
                    args '-v /var/run/docker.sock:/var/run/docker.sock --group-add 110'
                    reuseNode true
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh ''' 
                    export HOME=/tmp
                    docker build -t $DOCKER_USER/fastapi:${BUILD_NUMBER} -t $DOCKER_USER/fastapi:latest .
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_USER/fastapi:${BUILD_NUMBER}
                    docker push $DOCKER_USER/fastapi:latest'''
                }
            }
        }

        stage('Image Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                    args '--entrypoint=""'
                    reuseNode true
                }
            }
            steps {
                sh ' trivy image alphaman02/fastapi:${BUILD_NUMBER} '
            }
        }
        // stage('Update Manifest') {
        //     steps {
        //         sh ' sed -i "s/latest/${BUILD_NUMBER}/g" kubernetes/deployment.yaml'
        //     }
        // } 
    }

    // post {

    //     success {
    //         emailext(
    //             subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
    //             body: """ Build completed successfully Job Name: ${env.JOB_NAME}
    //             Build Number: ${env.BUILD_NUMBER} Build URL: ${env.BUILD_URL}
    //             Status: SUCCESS""",
    //             to: "phoenixanand02@example.com"
    //         )
    //     }   
    
    //     failure {
    //         emailext(
    //             subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
    //             body: """Build failed
    //             Job Name: ${env.JOB_NAME}
    //             Build Number: ${env.BUILD_NUMBER}
    //             Build URL: ${env.BUILD_URL}
    //         Please check Jenkins logs""",
    //             to: "phoenixanand02@example.com"
    //         )
    //     }
    //     unstable {
    //         emailext(
    //             subject: "UNSTABLE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
    //             body: """Build is unstable
    //             Job Name: ${env.JOB_NAME}
    //             Build Number: ${env.BUILD_NUMBER}
    //             Build URL: ${env.BUILD_URL}""",
    //             to: "phoenixanand02@example.com"
    //         )
    //     }
    //     always {
    //         echo "Pipeline completed"
    //     }
    // }
}


