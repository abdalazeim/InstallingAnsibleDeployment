// Shared step: run a Semaphore template and poll until it finishes.
//
// Usage:
//   infrastructureSemaphore(
//     url: 'https://semaphore.example.internal',
//     projectId: '1',
//     templateName: 'Django - Deploy Application [prod]',
//     variables: [django_application: 'portal', confirm_operation: 'true'],
//     credentialsId: 'semaphore-api-token'
//   )
//
// The token is read from a Jenkins credential and never written to logs.
def call(Map config = [:]) {
    def url = config.url ?: error('infrastructureSemaphore: url is required')
    def projectId = config.projectId ?: error('infrastructureSemaphore: projectId is required')
    def credentialsId = config.credentialsId ?: 'semaphore-api-token'
    def variables = config.variables ?: [:]
    def pollSeconds = (config.pollSeconds ?: 5) as int
    def maxAttempts = (config.maxAttempts ?: 180) as int
    def message = config.message ?: "Jenkins ${env.JOB_NAME} #${env.BUILD_NUMBER}"

    if (!(url ==~ /^https:\/\/[^\/]+.*$/) &&
        !(url ==~ /^http:\/\/(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$/)) {
        error('infrastructureSemaphore: use HTTPS or a loopback HTTP Semaphore URL')
    }

    withCredentials([string(credentialsId: credentialsId, variable: 'SEMAPHORE_API_TOKEN')]) {
        def headers = [[name: 'Authorization', value: "Bearer ${env.SEMAPHORE_API_TOKEN}"]]
        def templateId = config.templateId as Integer

        if (templateId == null) {
            def templateName = config.templateName ?: error(
                'infrastructureSemaphore: templateId or templateName is required')
            def listResponse = httpRequest(
                url: "${url}/api/project/${projectId}/templates",
                httpMode: 'GET',
                customHeaders: headers,
                validResponseCodes: '200',
                timeout: 30
            )
            def matches = readJSON(text: listResponse.content).findAll { it.name == templateName }
            if (matches.size() != 1) {
                error("infrastructureSemaphore: expected one template named '${templateName}', found ${matches.size()}")
            }
            templateId = matches[0].id as Integer
        }

        def payload = groovy.json.JsonOutput.toJson([
            template_id: templateId,
            environment: groovy.json.JsonOutput.toJson(variables),
            message: message
        ])

        def taskResponse = httpRequest(
            url: "${url}/api/project/${projectId}/tasks",
            httpMode: 'POST',
            contentType: 'APPLICATION_JSON',
            customHeaders: headers,
            requestBody: payload,
            validResponseCodes: '200:299',
            timeout: 30
        )
        def task = readJSON(text: taskResponse.content)
        if (!task.id) {
            error('infrastructureSemaphore: Semaphore did not return a task ID')
        }
        echo "Semaphore task ${task.id} started for template ${templateId}"

        def status = 'unknown'
        for (int attempt = 0; attempt < maxAttempts; attempt++) {
            sleep(time: pollSeconds, unit: 'SECONDS')
            def statusResponse = httpRequest(
                url: "${url}/api/project/${projectId}/tasks/${task.id}",
                httpMode: 'GET',
                customHeaders: headers,
                validResponseCodes: '200',
                timeout: 30
            )
            status = readJSON(text: statusResponse.content).status
            if (status in ['success', 'error', 'stopped']) {
                break
            }
        }

        if (status != 'success') {
            error("infrastructureSemaphore: Semaphore task ${task.id} finished with status '${status}'")
        }
        echo "Semaphore task ${task.id} completed successfully"
        return task
    }
}
