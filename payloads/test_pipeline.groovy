pipeline {
    agent any
    stages {
        stage("Run agent") {
            steps {
                script {
                    sh "ls -a"
                }
            }
        }
    }
}