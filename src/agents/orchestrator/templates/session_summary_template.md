# Session Summary — {{session_id}}

**Generated:** {{timestamp}}  
**Phase:** {{phase}}  
**Total Agents:** {{total_agents}}  

---

## 📊 Agent Execution Summary

| Agent | Status | Notes |
|--------|---------|-------|
{% for agent in agents %}
| {{agent.name}} | {{agent.status}} | {{agent.message}} |
{% endfor %}

---

## 📋 Combined Results

{{combined_results}}

---

## 📁 Outputs Generated

{% for output in outputs %}
- {{output}}
{% endfor %}

---

## 🔍 Session Metrics

- **Duration:** {{duration}}
- **Successful:** {{successful_count}}
- **Skipped:** {{skipped_count}}
- **Errors:** {{error_count}}

---

**Orchestrator Version:** {{orchestrator_version}}  
**Log file:** {{log_path}}  
**Registry:** {{registry_path}}

