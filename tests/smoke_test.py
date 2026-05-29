import requests

BASE = "http://localhost:8000/api/v1"

# Health
r = requests.get(f"{BASE}/health")
print("Health:", r.status_code)

# Register
user = {"name": "Test User", "email": "test@test.com", "password": "Test12345", "role": "admin"}

requests.post(f"{BASE}/auth/register", json=user)

# Login
r = requests.post(f"{BASE}/auth/login", json={"email": user["email"], "password": user["password"]})

token = r.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create workflow
workflow = {"workflow_name": "Smoke Test", "workflow_type": "analytics", "input_payload": {"test": True}}

r = requests.post(f"{BASE}/workflows", json=workflow, headers=headers)

workflow_id = r.json()["id"]

print("Workflow created:", workflow_id)

# Trigger workflow
r = requests.post(f"{BASE}/workflows/{workflow_id}/trigger", headers=headers)

print("Workflow trigger:", r.status_code)

# Execute agent
r = requests.post(
    f"{BASE}/agents/execute",
    json={"agent_type": "analytics", "task": "Generate report", "context": {}},
    headers=headers,
)

print("Agent execute:", r.status_code)

# Analytics
r = requests.get(f"{BASE}/analytics/overview", headers=headers)

print("Analytics:", r.status_code)

print("SYSTEM OK")
