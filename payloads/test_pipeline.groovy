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
                    SLEEP = Math.abs(new Random().nextInt() % 15 + 1)
                    sh "echo $SLEEP"
                    sh "sleep ${SLEEP}s"
                }
            }
        }
    }
}