#!groovy
library identifier: 'adtran-pipeline-library@v3.21.0', changelog: false
library identifier: 'porg@v3.3.6', changelog: false

def config = [:]
def default_config = [
    'jenkins_agent_label': 'small',
    'publish_pr_package': false
]

def shouldRunPublishStage(config) {
    return porgPipelineUtils.isPublishableBranch(config) && porgPipelineUtils.shouldPublish()
}

def localDockerImage = 'selene-python'
def remoteDockerImage = 'docker.adtran.com:5000/selene-python'

pipeline {
  agent {
    label 'small'
  }

  options {
    buildDiscarder(logRotator(numToKeepStr:'100'))
    timestamps()
  }

  environment {
    ARTIFACTORY = credentials('artifactory-publish')
    TWINE_USERNAME = "${ARTIFACTORY_USR}"
    TWINE_PASSWORD = "${ARTIFACTORY_PSW}"
    TWINE_REPOSITORY_URL = "https://artifactory.adtran.com/artifactory/api/pypi/pypi"
  }

  stages {
    stage('Setup') {
      steps {
          script {
              checkout scm
              porgPipelineUtils.initialize()

              def configuration = porgPipelineUtils.readTOML('pyproject.toml')['tool']['porg']
              config = mergedMap(configuration, default_config)
              echo "Merged Build Config: ${config}"

          }
      }
  }
    stage('Tests') {
      steps {
        script {
          porgPipelineUtils.lintAndRunTests()
        }
      }

      post {
        always {
          junit ".porg/test_results/*/test_results.xml"
        }
      }
    }

    stage('Publish') {
      when { expression { shouldRunPublishStage(config)}}
      steps {
        script {
          porgPipelineUtils.publishPackage()
        }
      }
    }
  }

  post {
    always {
      deleteDir()
    }
  }
}
