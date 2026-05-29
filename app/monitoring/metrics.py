from prometheus_client import Counter, Gauge, Histogram


workflow_counter = Counter("workflow_total", "Total workflows processed", ["status", "workflow_type"])
task_latency = Histogram("workflow_task_latency_seconds", "Task latency by agent", ["agent_type"])
agent_response_time = Histogram("agent_response_time_seconds", "Agent response time", ["agent_type"])
queue_size = Gauge("queue_size", "Current queue size", ["queue"])
failure_rate = Gauge("workflow_failure_rate", "Workflow failure rate")

