pipeline {

    agent { label 'agent_1'}

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
