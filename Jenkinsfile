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
                sh ' trivy image alphaman02/fastapi:${BUILD_NUMBER} --cache-dir .trivycache'
            }
        }
        stage('Update Deployment File') {
            steps {
                withCredentials([string(credentialsId: 'github', variable: 'GITHUB_TOKEN')]) {   
                    sh '''
                    rm -rf gitops-repo
                    git clone https://x-access-token:${GITHUB_TOKEN}@github.com/phoenixanand/REST-API-Web-Server-with-DevSecOps- gitops
                    cd gitops

                    git config user.email "phoenixanand02@gmail.com"           
                    git config user.name "Anand"

                    sed -i "s/replaceImageTag/${BUILD_NUMBER}/g" deployment.yaml
                    
                    git add deployment.yaml
                    git commit -m "Update deployment image to version ${BUILD_NUMBER}" || echo "No changes to commit"

                    git push https://x-access-token:${GITHUB_TOKEN}@github.com/phoenixanand/REST-API-Web-Server-with-DevSecOps- HEAD:main
                    '''
                }
            }
        }

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


