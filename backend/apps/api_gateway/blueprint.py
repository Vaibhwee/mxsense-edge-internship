PRIMARY_MODULES = [
    {
        "slug": "operations-dashboard",
        "title": "Operations Dashboard",
        "summary": "Single-pane command center for runtime, quality, devices, alerts, and sync.",
        "primary_users": ["operator", "admin", "qa analyst"],
        "cards": ["Devices Online", "Jobs Running", "Quality Index", "GPU Load"],
    },
    {
        "slug": "devices-assets",
        "title": "Devices & Assets",
        "summary": "Fleet lifecycle, assignment, firmware, and configuration management.",
        "primary_users": ["admin", "service engineer"],
        "cards": ["Total Devices", "Offline Devices", "Firmware Pending"],
    },
    {
        "slug": "connectivity-adaptation",
        "title": "Connectivity & Adaptation",
        "summary": "Protocol adapters, connectors, and payload/schema normalization.",
        "primary_users": ["integration engineer", "admin"],
        "cards": ["Active Adapters", "Schema Errors", "Topic Health"],
    },
    {
        "slug": "data-collection-sessions",
        "title": "Data Collection & Sessions",
        "summary": "Session control, sampling, metadata binding, and live collection.",
        "primary_users": ["operator", "analyst"],
        "cards": ["Active Sessions", "Packet Rate", "Dropped Packets"],
    },
    {
        "slug": "preprocessing-feature-engineering",
        "title": "Preprocessing & Feature Engineering",
        "summary": "Signal cleaning, image QC, temporal alignment, and feature generation.",
        "primary_users": ["data scientist", "analyst"],
        "cards": ["Signal Quality", "Drift Risk", "Feature Count"],
    },
    {
        "slug": "inferencing-fusion",
        "title": "Inferencing & Fusion",
        "summary": "Sensing AI, vision AI, fusion runtime, and model orchestration.",
        "primary_users": ["qa analyst", "ai engineer"],
        "cards": ["Active Model", "Queued Jobs", "Confidence Trend"],
    },
    {
        "slug": "quality-decision-intelligence",
        "title": "Quality / Decision Intelligence",
        "summary": "Scores, grades, rules, recommendations, and human review.",
        "primary_users": ["qa analyst", "operator"],
        "cards": ["Quality Score", "Risk Band", "Decision Status"],
    },
    {
        "slug": "alerts-incidents",
        "title": "Alerts & Incidents",
        "summary": "Alert routing, incident drill-down, and acknowledgement workflows.",
        "primary_users": ["operator", "service engineer"],
        "cards": ["Open Alerts", "Critical Alerts", "Ack State"],
    },
    {
        "slug": "monitoring-performance",
        "title": "Monitoring & Performance",
        "summary": "Service health, telemetry, logs, metrics, and pipeline observability.",
        "primary_users": ["devops", "service engineer"],
        "cards": ["Healthy Services", "GPU Utilization", "Queue Depth"],
    },
    {
        "slug": "storage-retention",
        "title": "Storage & Retention",
        "summary": "Raw, processed, result, and evidence storage lifecycle management.",
        "primary_users": ["admin", "devops"],
        "cards": ["Storage Used", "Archive Ready", "Last Backup"],
    },
    {
        "slug": "api-gateway-integrations",
        "title": "API Gateway & Integrations",
        "summary": "Endpoint registry, live streams, request logs, and enterprise integration.",
        "primary_users": ["developer", "integration engineer"],
        "cards": ["API Volume", "Connected Clients", "Endpoint Health"],
    },
    {
        "slug": "edge-to-cloud-sync",
        "title": "Edge-to-Cloud Sync",
        "summary": "Store-and-forward result, evidence, config, and model synchronization.",
        "primary_users": ["admin", "devops"],
        "cards": ["Pending Sync", "Sync Latency", "Model Update Status"],
    },
    {
        "slug": "admin-security-governance",
        "title": "Admin / Security / Governance",
        "summary": "Users, policies, secrets, approvals, and audit continuity.",
        "primary_users": ["admin", "security lead"],
        "cards": ["Active Users", "Pending Approvals", "Audit Events"],
    },
]

BACKEND_SERVICES = [
    {"name": "device-manager", "responsibility": "registry, provisioning, heartbeat, lifecycle"},
    {"name": "protocol-adapter", "responsibility": "MQTT, RTSP, Modbus, serial, API bridging"},
    {"name": "data-ingestion", "responsibility": "validation, buffering, routing, batch/session capture"},
    {"name": "ai-orchestration", "responsibility": "preprocessing, features, models, inference jobs"},
    {"name": "quality-center", "responsibility": "scores, decision rules, alerts, human review"},
    {"name": "storage-sync", "responsibility": "artifact retention, backup, edge-to-cloud sync"},
    {"name": "monitoring-agent", "responsibility": "health, metrics, logs, incidents"},
    {"name": "api-gateway", "responsibility": "unified REST and product blueprint endpoints"},
    {"name": "governance", "responsibility": "roles, policies, approvals, audit, secrets"},
]

STACK_LAYERS = [
    {"layer": "Edge Runtime", "recommendation": "Ubuntu + Jetson Orin NX + Docker/K3s"},
    {"layer": "Backend", "recommendation": "Django + DRF modular domain apps"},
    {"layer": "Messaging", "recommendation": "MQTT broker + WebSocket live streams"},
    {"layer": "Database", "recommendation": "PostgreSQL operational store + JSON-rich models"},
    {"layer": "Cache/Queue", "recommendation": "Redis for buffering and retry orchestration"},
    {"layer": "Frontend", "recommendation": "Next.js operations console"},
]

OPERATOR_WORKFLOWS = [
    "Select device or sample",
    "Start collection session",
    "Watch live quality and runtime indicators",
    "Trigger or review inference",
    "Take decision: accept, hold, or reject",
    "Drill into alerts with evidence and action guidance",
]
