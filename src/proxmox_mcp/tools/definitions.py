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

CREATE_CONTAINER_DESC = """Create a new LXC container on a Proxmox node.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
hostname* - Container hostname (e.g. 'web-server')
template* - Template to use (e.g. 'ubuntu-20.04-standard')
storage* - Storage pool (e.g. 'local-lvm')
cores* - CPU cores (e.g. 2)
memory* - Memory in MB (e.g. 2048)
password* - Root password for container

Example:
{"success": true, "vmid": "200", "node": "pve1"}"""

START_CONTAINER_DESC = """Start an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "running"}"""

STOP_CONTAINER_DESC = """Stop an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "stopped"}"""

SHUTDOWN_CONTAINER_DESC = """Shutdown an LXC container gracefully.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "stopped"}"""

REBOOT_CONTAINER_DESC = """Reboot an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "running"}"""

SUSPEND_CONTAINER_DESC = """Suspend an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "suspended"}"""

RESUME_CONTAINER_DESC = """Resume a suspended LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "status": "running"}"""

GET_CONTAINER_CONFIG_DESC = """Get LXC container configuration.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"vmid": "200", "hostname": "web-server", "cores": 2, "memory": 2048}"""

UPDATE_CONTAINER_CONFIG_DESC = """Update LXC container configuration.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
cores - CPU cores (e.g. 4)
memory - Memory in MB (e.g. 4096)
hostname - Container hostname (e.g. 'new-hostname')
description - Container description

Example:
{"success": true, "vmid": "200", "message": "Configuration updated"}"""

EXECUTE_CONTAINER_COMMAND_DESC = """Execute commands in an LXC container.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
command* - Shell command to run (e.g. 'uname -a')

Example:
{"success": true, "output": "Linux container1 5.4.0", "exit_code": 0}"""

CLONE_CONTAINER_DESC = """Clone an existing LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Source container ID (e.g. '200')
newid* - New container ID (e.g. '201')
name* - New container name (e.g. 'web-server-clone')
storage* - Storage pool for clone (e.g. 'local-lvm')

Example:
{"success": true, "newid": "201", "name": "web-server-clone"}"""

DESTROY_CONTAINER_DESC = """Destroy an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"success": true, "vmid": "200", "message": "Container destroyed"}"""

GET_CONTAINER_SNAPSHOTS_DESC = """Get LXC container snapshots.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')

Example:
{"snapshots": [{"name": "backup1", "time": "2024-01-01T12:00:00Z"}]}"""

CREATE_CONTAINER_SNAPSHOT_DESC = """Create a snapshot of an LXC container.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
snapname* - Snapshot name (e.g. 'backup-2024-01-01')
description - Snapshot description

Example:
{"success": true, "snapname": "backup-2024-01-01"}"""

DELETE_CONTAINER_SNAPSHOT_DESC = """Delete a container snapshot.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
snapname* - Snapshot name (e.g. 'backup-2024-01-01')

Example:
{"success": true, "snapname": "backup-2024-01-01"}"""

ROLLBACK_CONTAINER_SNAPSHOT_DESC = """Rollback container to a snapshot.

Parameters:
node* - Target node name (e.g. 'pve1')
vmid* - Container ID number (e.g. '200')
snapname* - Snapshot name (e.g. 'backup-2024-01-01')

Example:
{"success": true, "snapname": "backup-2024-01-01"}"""

# Storage tool descriptions
GET_STORAGE_DESC = """List storage pools across the cluster with their usage and configuration.

Example:
{"storage": "local-lvm", "type": "lvm", "used": "500GB", "total": "1TB"}"""

# Cluster tool descriptions
GET_CLUSTER_STATUS_DESC = """Get overall Proxmox cluster health and configuration status.

Example:
{"name": "proxmox", "quorum": "ok", "nodes": 3, "ha_status": "active"}"""
