"""
Tool descriptions for Proxmox MCP tools.
"""

# Node tool descriptions
GET_NODES_DESC = """List all nodes in the Proxmox cluster with their status, CPU, memory, and role information.

Example:
{"node": "pve1", "status": "online", "cpu_usage": 0.15, "memory": {"used": "8GB", "total": "32GB"}}"""

GET_NODE_STATUS_DESC = """Get detailed status information for a specific Proxmox node.

Parameters:
node* - Name/ID of node to query (e.g. 'pve1')

Example:
{"cpu": {"usage": 0.15}, "memory": {"used": "8GB", "total": "32GB"}}"""

# VM tool descriptions
GET_VMS_DESC = """List all virtual machines across the cluster with their status and resource usage.

Example:
{"vmid": "100", "name": "ubuntu", "status": "running", "cpu": 2, "memory": 4096}"""

CREATE_VM_DESC = """Create a new virtual machine on a Proxmox node.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
name* - VM name (e.g. 'ubuntu-server')
cores* - CPU cores (e.g. 2)
memory* - Memory in MB (e.g. 2048)
storage* - Storage pool (e.g. 'local-lvm')
ostype* - OS type (e.g. 'l26', 'win10', 'other')

Example:
{"success": true, "vmid": "100", "node": "pve1"}"""

START_VM_DESC = """Start a virtual machine.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "vmid": "100", "status": "running"}"""

STOP_VM_DESC = """Stop a virtual machine.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "vmid": "100", "status": "stopped"}"""

SHUTDOWN_VM_DESC = """Shutdown a virtual machine gracefully.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "vmid": "100", "status": "stopped"}"""

REBOOT_VM_DESC = """Reboot a virtual machine.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "vmid": "100", "status": "running"}"""

GET_VM_CONFIG_DESC = """Get virtual machine configuration.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"vmid": "100", "name": "ubuntu", "cores": 2, "memory": 2048}"""

UPDATE_VM_CONFIG_DESC = """Update virtual machine configuration.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
cores - CPU cores (e.g. 4)
memory - Memory in MB (e.g. 4096)
name - VM name (e.g. 'new-name')

Example:
{"success": true, "vmid": "100", "message": "Configuration updated"}"""

EXECUTE_VM_COMMAND_DESC = """Execute commands in a VM via QEMU guest agent.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
command* - Shell command to run (e.g. 'uname -a')

Example:
{"success": true, "output": "Linux vm1 5.4.0", "exit_code": 0}"""

# Container tool descriptions
GET_CONTAINERS_DESC = """List all LXC containers across the cluster with their status and configuration.

Example:
{"vmid": "200", "name": "nginx", "status": "running", "template": "ubuntu-20.04"}"""

# Storage tool descriptions
GET_STORAGE_DESC = """List storage pools across the cluster with their usage and configuration.

Example:
{"storage": "local-lvm", "type": "lvm", "used": "500GB", "total": "1TB"}"""

# Cluster tool descriptions
GET_CLUSTER_STATUS_DESC = """Get overall Proxmox cluster health and configuration status.

Example:
{"name": "proxmox", "quorum": "ok", "nodes": 3, "ha_status": "active"}"""
