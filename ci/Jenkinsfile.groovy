pipeline {

    agent any

    stages {
        stage("Prepare") {
            steps {
                script {
                    echo "preparing"
                }
            }      
        }
        stage("Run") {
            steps {
                script {
                    echo "running"
                }
            }
        }
    }
}
