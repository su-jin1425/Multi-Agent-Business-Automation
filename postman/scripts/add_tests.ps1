# Script to add test scripts to all request YAML files

$base = "postman/collections/Multi-Agent Business Automation"

function Add-Tests {
    param(
        [string]$filePath,
        [string]$testsCode
    )
    $content = [System.IO.File]::ReadAllText($filePath)
    if ($content -notmatch "scripts:") {
        $scriptBlock = "`r`nscripts:`r`n  - type: afterResponse`r`n    language: text/javascript`r`n    code: |-`r`n"
        foreach ($line in $testsCode -split "`n") {
            $scriptBlock += "      $($line.TrimEnd())`r`n"
        }
        [System.IO.File]::WriteAllText($filePath, $content + $scriptBlock)
        Write-Host "Updated: $filePath"
    } else {
        Write-Host "Skipped (already has scripts): $filePath"
    }
}

# Health Check
Add-Tests "$base\Health\Health Check.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has status ok', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('ok');
});
pm.test('Response has environment field', function () {
    pm.expect(pm.response.json()).to.have.property('environment');
});
pm.test('Response has version field', function () {
    pm.expect(pm.response.json()).to.have.property('version');
});
pm.test('Response time under 2000ms', function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
"@

# Readiness
Add-Tests "$base\Health\Readiness.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has status ready', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('ready');
});
pm.test('Response time under 3000ms', function () {
    pm.expect(pm.response.responseTime).to.be.below(3000);
});
"@

# Register User
Add-Tests "$base\Authentication\Register User.request.yaml" @"
pm.test('Status code is 201', function () {
    pm.response.to.have.status(201);
});
pm.test('Response has user id', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('id');
});
pm.test('Response has email field', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('email');
});
pm.test('Response has role field', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('role');
});
"@

# Login
Add-Tests "$base\Authentication\Login.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has access_token', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('access_token');
    pm.expect(json.access_token).to.be.a('string').and.not.empty;
});
pm.test('Response has token_type bearer', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('token_type');
    pm.expect(json.token_type.toLowerCase()).to.eql('bearer');
});
pm.test('Response has user object', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('user');
});
if (pm.response.code === 200) {
    const json = pm.response.json();
    pm.collectionVariables.set('token', json.access_token);
}
"@

# Get Current User (Me)
Add-Tests "$base\Authentication\Get Current User (Me).request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has email field', function () {
    pm.expect(pm.response.json()).to.have.property('email');
});
pm.test('Response has role field', function () {
    pm.expect(pm.response.json()).to.have.property('role');
});
"@

# List Agents
Add-Tests "$base\Agents\List Agents.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response is an array', function () {
    pm.expect(pm.response.json()).to.be.an('array');
});
pm.test('Each agent has id and agent_type', function () {
    const agents = pm.response.json();
    if (agents.length > 0) {
        pm.expect(agents[0]).to.have.property('id');
        pm.expect(agents[0]).to.have.property('agent_type');
        pm.collectionVariables.set('agent_id', agents[0].id);
    }
});
"@

# Get Agent
Add-Tests "$base\Agents\Get Agent.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has agent_type field', function () {
    pm.expect(pm.response.json()).to.have.property('agent_type');
});
pm.test('Response has status field', function () {
    pm.expect(pm.response.json()).to.have.property('status');
});
"@

# Execute Agent
Add-Tests "$base\Agents\Execute Agent.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has agent_type field', function () {
    pm.expect(pm.response.json()).to.have.property('agent_type');
});
pm.test('Response has result field', function () {
    pm.expect(pm.response.json()).to.have.property('result');
});
pm.test('Response has delegated_to field', function () {
    pm.expect(pm.response.json()).to.have.property('delegated_to');
});
"@

# Overview Metrics
Add-Tests "$base\Analytics\Overview Metrics.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has workflows_total', function () {
    pm.expect(pm.response.json()).to.have.property('workflows_total');
});
pm.test('Response has active_agents', function () {
    pm.expect(pm.response.json()).to.have.property('active_agents');
});
pm.test('Response has open_tickets', function () {
    pm.expect(pm.response.json()).to.have.property('open_tickets');
});
"@

# Workflow Metrics
Add-Tests "$base\Analytics\Workflow Metrics.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has by_status field', function () {
    pm.expect(pm.response.json()).to.have.property('by_status');
});
pm.test('Response has completion_rate', function () {
    pm.expect(pm.response.json()).to.have.property('completion_rate');
});
pm.test('Response has failure_rate', function () {
    pm.expect(pm.response.json()).to.have.property('failure_rate');
});
"@

# Agent Performance
Add-Tests "$base\Analytics\Agent Performance.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response is an array', function () {
    pm.expect(pm.response.json()).to.be.an('array');
});
pm.test('Each entry has agent_name and agent_type', function () {
    const data = pm.response.json();
    if (data.length > 0) {
        pm.expect(data[0]).to.have.property('agent_name');
        pm.expect(data[0]).to.have.property('agent_type');
    }
});
"@

# Create Ticket
Add-Tests "$base\Support Tickets\Create Ticket.request.yaml" @"
pm.test('Status code is 201', function () {
    pm.response.to.have.status(201);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has status open', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('open');
});
if (pm.response.code === 201) {
    pm.collectionVariables.set('ticket_id', pm.response.json().id);
}
"@

# List Tickets
Add-Tests "$base\Support Tickets\List Tickets.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response is an array', function () {
    pm.expect(pm.response.json()).to.be.an('array');
});
"@

# Update Ticket
Add-Tests "$base\Support Tickets\Update Ticket.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has updated status', function () {
    pm.expect(pm.response.json()).to.have.property('status');
});
"@

# List Workflows
Add-Tests "$base\Workflows\List Workflows.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response is an array', function () {
    pm.expect(pm.response.json()).to.be.an('array');
});
"@

# Create Workflow
Add-Tests "$base\Workflows\Create Workflow.request.yaml" @"
pm.test('Status code is 201', function () {
    pm.response.to.have.status(201);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has status pending', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('pending');
});
pm.test('Response has workflow_name', function () {
    pm.expect(pm.response.json()).to.have.property('workflow_name');
});
if (pm.response.code === 201) {
    pm.collectionVariables.set('workflow_id', pm.response.json().id);
}
"@

# Get Workflow
Add-Tests "$base\Workflows\Get Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has workflow_type', function () {
    pm.expect(pm.response.json()).to.have.property('workflow_type');
});
pm.test('Response has status field', function () {
    pm.expect(pm.response.json()).to.have.property('status');
});
"@

# Update Workflow
Add-Tests "$base\Workflows\Update Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has workflow_name', function () {
    pm.expect(pm.response.json()).to.have.property('workflow_name');
});
"@

# Trigger Workflow
Add-Tests "$base\Workflows\Trigger Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has workflow_id', function () {
    pm.expect(pm.response.json()).to.have.property('workflow_id');
});
pm.test('Response has celery_task_id', function () {
    pm.expect(pm.response.json()).to.have.property('celery_task_id');
});
pm.test('Response has message', function () {
    pm.expect(pm.response.json()).to.have.property('message');
});
"@

# Execute Workflow (Inline)
Add-Tests "$base\Workflows\Execute Workflow (Inline).request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has status completed', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('completed');
});
"@

# Pause Workflow
Add-Tests "$base\Workflows\Pause Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has status paused', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('paused');
});
"@

# Resume Workflow
Add-Tests "$base\Workflows\Resume Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has id field', function () {
    pm.expect(pm.response.json()).to.have.property('id');
});
pm.test('Response has status field', function () {
    pm.expect(pm.response.json()).to.have.property('status');
});
"@

# Retry Workflow
Add-Tests "$base\Workflows\Retry Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has status retrying', function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json.status).to.eql('retrying');
});
"@

# Delete Workflow
Add-Tests "$base\Workflows\Delete Workflow.request.yaml" @"
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
pm.test('Response has message field', function () {
    pm.expect(pm.response.json()).to.have.property('message');
});
"@

Write-Host "All test scripts added successfully!"
