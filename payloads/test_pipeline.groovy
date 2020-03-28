pipeline {
    agent any

    parameters {
            string(name: 'BUILD_NAME', defaultValue: 'agnet_name/job_id', description: '')
    }

    stages {
        stage("Run agent") {
            steps {
                buildName "${BUILD_NAME}"
                script {
                    sh "ls -a"
//                     sh "sleep 5"
                }
            }
        }
    }
}