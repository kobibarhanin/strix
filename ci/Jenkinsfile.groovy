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
//             agent { label 'agent_1'}
            steps {
                script {
                    echo "running"
                    for (i=0; i<5; i++){
                        Integer x = i;
                        build job: 'job_temp', parameters: [[$class: 'NodeParameterValue', labels: 'agent_1', nodeEligibility: [$class: 'AllNodeEligibility']],
                        string(name: 'ID', value: x.toString())]
                    }
                }
            }
        }
    }
}
