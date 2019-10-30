pipeline {

    agent { label 'master'}

    stages {
        stage("Prepare") {
            steps {
                script {
                    echo "preparing"
                }
            }      
        }
        stage("API tests") {
            agent { label 'agent_1'}
            steps {
                script {
                    echo "running"
                }
            }
        }
    }
}
