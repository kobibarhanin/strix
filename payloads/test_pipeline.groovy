pipeline {
    agent any
    stages {
        stage(&apos;Run agent&apos;) {
            steps {
                script {
                    sh &quot;ls -a /&quot;
                }
            }
        }
    }
}