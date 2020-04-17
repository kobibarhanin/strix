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
                    NUM = Math.abs(new Random().nextInt() % 10 + 1)
                    sh "echo $NUM"
                    sh "sleep ${[ ( ${NUM} % 10 )  + 1 ]}s"
                }
            }
        }
    }
}