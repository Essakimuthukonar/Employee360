
pipeline {
    agent any

    environment {
        DOCKER_USER = 'muthukonar'
        APP_SERVER = 'ubuntu@10.20.1.185'
        SSH_KEY = '/var/lib/jenkins/.ssh/employee360_deploy_key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    docker build -t ${DOCKER_USER}/employee360-backend:${BUILD_NUMBER} backend
                    docker build -t ${DOCKER_USER}/employee360-frontend:${BUILD_NUMBER} frontend
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DH_TOKEN" | docker login \
                            --username "$DH_USER" \
                            --password-stdin

                        docker push ${DOCKER_USER}/employee360-backend:${BUILD_NUMBER}
                        docker push ${DOCKER_USER}/employee360-frontend:${BUILD_NUMBER}

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy with Helm to Kind') {
            steps {
                sh '''
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${APP_SERVER} "
                        cd /opt/employee360 &&
                        helm upgrade --install employee360 ./helm/employee360 \
                        --set-string backend.image=${DOCKER_USER}/employee360-backend:${BUILD_NUMBER} \
                        --set-string frontend.image=${DOCKER_USER}/employee360-frontend:${BUILD_NUMBER} \
                        --wait --timeout 180s
                    "
                '''
            }
        }

        stage('Verify Kubernetes') {
            steps {
                sh '''
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${APP_SERVER} \
                        "kubectl get pods && helm status employee360"
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful. Cleaning local Docker images.'

            sh '''
                docker image ls "${DOCKER_USER}/employee360-backend" -q \
                    | sort -u | xargs -r docker image rm -f

                docker image ls "${DOCKER_USER}/employee360-frontend" -q \
                    | sort -u | xargs -r docker image rm -f

                docker image prune -f

                echo "Docker cleanup completed."
                docker system df
            '''

            echo 'Employee360 successfully deployed to Kind using Helm!'
        }

        failure {
            echo 'Deployment failed. Keeping local images for troubleshooting.'
        }
    }
}
