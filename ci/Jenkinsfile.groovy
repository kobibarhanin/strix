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
                    for (i=0; i<3; i++){
                        Integer x = i;
                        echo "$x"
                        build job: 'job_temp', parameters: [string(name: 'ID', value: x.toString())]
                    }
                }
            }
        }
    }
}
