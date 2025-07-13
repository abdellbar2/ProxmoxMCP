"""
Output templates for Proxmox MCP resource types.
"""
from typing import Dict, List, Any
from .formatters import ProxmoxFormatters
from .theme import ProxmoxTheme
from .colors import ProxmoxColors
from .components import ProxmoxComponents

class ProxmoxTemplates:
    """Output templates for different Proxmox resource types."""
    
    @staticmethod
    def node_list(nodes: List[Dict[str, Any]]) -> str:
        """Template for node list output.
        
        Args:
            nodes: List of node data dictionaries
            
        Returns:
            Formatted node list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['node']} Proxmox Nodes"]
        
        for node in nodes:
            # Get node status
            status = node.get("status", "unknown")
            
            # Get memory info
            memory = node.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            # Format node info
            result.extend([
                "",  # Empty line between nodes
                f"{ProxmoxTheme.RESOURCES['node']} {node['node']}",
                f"  • Status: {status.upper()}",
                f"  • Uptime: {ProxmoxFormatters.format_uptime(node.get('uptime', 0))}",
                f"  • CPU Cores: {node.get('maxcpu', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
            # Add disk usage if available
            disk = node.get("disk", {})
            if disk:
                disk_used = disk.get("used", 0)
                disk_total = disk.get("total", 0)
                disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
                result.append(
                    f"  • Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                    f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
                )
            
        return "\n".join(result)
    
    @staticmethod
    def node_status(node: str, status: Dict[str, Any]) -> str:
        """Template for detailed node status output.
        
        Args:
            node: Node name
            status: Node status data
            
        Returns:
            Formatted node status string
        """
        memory = status.get("memory", {})
        memory_used = memory.get("used", 0)
        memory_total = memory.get("total", 0)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        result = [
            f"{ProxmoxTheme.RESOURCES['node']} Node: {node}",
            f"  • Status: {status.get('status', 'unknown').upper()}",
            f"  • Uptime: {ProxmoxFormatters.format_uptime(status.get('uptime', 0))}",
            f"  • CPU Cores: {status.get('maxcpu', 'N/A')}",
            f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
            f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
        ]
        
        # Add disk usage if available
        disk = status.get("disk", {})
        if disk:
            disk_used = disk.get("used", 0)
            disk_total = disk.get("total", 0)
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            result.append(
                f"  • Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
            )
        
        return "\n".join(result)
    
    @staticmethod
    def vm_list(vms: List[Dict[str, Any]]) -> str:
        """Template for VM list output.
        
        Args:
            vms: List of VM data dictionaries
            
        Returns:
            Formatted VM list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['vm']} Virtual Machines"]
        
        for vm in vms:
            memory = vm.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between VMs
                f"{ProxmoxTheme.RESOURCES['vm']} {vm['name']} (ID: {vm['vmid']})",
                f"  • Status: {vm['status'].upper()}",
                f"  • Node: {vm['node']}",
                f"  • CPU Cores: {vm.get('cpus', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def storage_list(storage: List[Dict[str, Any]]) -> str:
        """Template for storage list output.
        
        Args:
            storage: List of storage data dictionaries
            
        Returns:
            Formatted storage list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['storage']} Storage Pools"]
        
        for store in storage:
            used = store.get("used", 0)
            total = store.get("total", 0)
            percent = (used / total * 100) if total > 0 else 0
            
            result.extend([
                "",  # Empty line between storage pools
                f"{ProxmoxTheme.RESOURCES['storage']} {store['storage']}",
                f"  • Status: {store.get('status', 'unknown').upper()}",
                f"  • Type: {store['type']}",
                f"  • Usage: {ProxmoxFormatters.format_bytes(used)} / "
                f"{ProxmoxFormatters.format_bytes(total)} ({percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def container_list(containers: List[Dict[str, Any]]) -> str:
        """Template for container list output.
        
        Args:
            containers: List of container data dictionaries
            
        Returns:
            Formatted container list string
        """
        if not containers:
            return f"{ProxmoxTheme.RESOURCES['container']} No containers found"
            
        result = [f"{ProxmoxTheme.RESOURCES['container']} Containers"]
        
        for container in containers:
            memory = container.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between containers
                f"{ProxmoxTheme.RESOURCES['container']} {container['name']} (ID: {container['vmid']})",
                f"  • Status: {container['status'].upper()}",
                f"  • Node: {container['node']}",
                f"  • CPU Cores: {container.get('cpus', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)

    @staticmethod
    def cluster_status(status: Dict[str, Any]) -> str:
        """Template for cluster status output.
        
        Args:
            status: Cluster status data
            
        Returns:
            Formatted cluster status string
        """
        result = [f"{ProxmoxTheme.SECTIONS['configuration']} Proxmox Cluster"]
        
        # Basic cluster info
        result.extend([
            "",
            f"  • Name: {status.get('name', 'N/A')}",
            f"  • Quorum: {'OK' if status.get('quorum') else 'NOT OK'}",
            f"  • Nodes: {status.get('nodes', 0)}",
        ])
        
        # Add resource count if available
        resources = status.get('resources', [])
        if resources:
            result.append(f"  • Resources: {len(resources)}")
        
        return "\n".join(result)

    @staticmethod
    def vm_creation_result(success: bool, vmid: str, node: str, name: str, 
                          cores: int, memory: int, storage: str, ostype: str, 
                          error: str = None) -> str:
        """Template for VM creation result output.
        
        Args:
            success: Whether VM creation succeeded
            vmid: VM ID
            node: Target node
            name: VM name
            cores: CPU cores
            memory: Memory in MB
            storage: Storage pool
            ostype: OS type
            error: Error message if creation failed
            
        Returns:
            Formatted VM creation result string
        """
        if success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} VM Created Successfully",
                "",
                f"{ProxmoxTheme.RESOURCES['vm']} {name} (ID: {vmid})",
                f"  • Node: {node}",
                f"  • CPU Cores: {cores}",
                f"  • Memory: {memory} MB",
                f"  • Storage: {storage}",
                f"  • OS Type: {ostype}",
                "",
                f"{ProxmoxTheme.ACTIONS['info']} VM is ready for configuration and startup"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} VM Creation Failed",
                "",
                f"  • VM Name: {name}",
                f"  • Target Node: {node}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def vm_power_operation(operation: str, success: bool, vmid: str, node: str, 
                          status: str, error: str = "") -> str:
        """Template for VM power operation results.
        
        Args:
            operation: Type of operation (start, stop, shutdown, reboot)
            success: Whether operation succeeded
            vmid: VM ID
            node: Target node
            status: VM status after operation
            error: Error message if operation failed
            
        Returns:
            Formatted VM power operation result string
        """
        operation_emoji = {
            'start': ProxmoxTheme.ACTIONS['start'],
            'stop': ProxmoxTheme.ACTIONS['stop'],
            'shutdown': ProxmoxTheme.ACTIONS['stop'],
            'reboot': ProxmoxTheme.ACTIONS['restart']
        }.get(operation.lower(), ProxmoxTheme.ACTIONS['info'])
        
        if success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} VM {operation.title()} Successful",
                "",
                f"{ProxmoxTheme.RESOURCES['vm']} VM {vmid}",
                f"  • Node: {node}",
                f"  • Operation: {operation.title()}",
                f"  • Status: {status.upper()}",
                "",
                f"{operation_emoji} VM is now {status}"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} VM {operation.title()} Failed",
                "",
                f"  • VM ID: {vmid}",
                f"  • Target Node: {node}",
                f"  • Operation: {operation.title()}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def vm_config_result(success: bool, vmid: str, node: str, config: Dict[str, Any] = None, 
                        error: str = "") -> str:
        """Template for VM configuration operation results.
        
        Args:
            success: Whether operation succeeded
            vmid: VM ID
            node: Target node
            config: VM configuration data
            error: Error message if operation failed
            
        Returns:
            Formatted VM configuration result string
        """
        if success and config:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} VM Configuration Retrieved",
                "",
                f"{ProxmoxTheme.RESOURCES['vm']} VM {vmid}",
                f"  • Node: {node}",
                f"  • Name: {config.get('name', 'N/A')}",
                f"  • CPU Cores: {config.get('cores', 'N/A')}",
                f"  • Memory: {config.get('memory', 'N/A')} MB",
                f"  • OS Type: {config.get('ostype', 'N/A')}",
                f"  • Status: {config.get('status', 'N/A')}"
            ]
            
            # Add additional configuration details if available
            if config.get('description'):
                result.append(f"  • Description: {config['description']}")
            if config.get('bootdisk'):
                result.append(f"  • Boot Disk: {config['bootdisk']}")
        elif success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} VM Configuration Updated",
                "",
                f"{ProxmoxTheme.RESOURCES['vm']} VM {vmid}",
                f"  • Node: {node}",
                f"  • Status: Configuration updated successfully"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} VM Configuration Operation Failed",
                "",
                f"  • VM ID: {vmid}",
                f"  • Target Node: {node}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def container_creation_result(success: bool, vmid: str, node: str, hostname: str, 
                                 template: str, cores: int, memory: int, storage: str, 
                                 error: str = "") -> str:
        """Template for container creation result output.
        
        Args:
            success: Whether container creation succeeded
            vmid: Container ID
            node: Target node
            hostname: Container hostname
            template: Template used
            cores: CPU cores
            memory: Memory in MB
            storage: Storage pool
            error: Error message if creation failed
            
        Returns:
            Formatted container creation result string
        """
        if success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} Container Created Successfully",
                "",
                f"{ProxmoxTheme.RESOURCES['container']} {hostname} (ID: {vmid})",
                f"  • Node: {node}",
                f"  • Template: {template}",
                f"  • CPU Cores: {cores}",
                f"  • Memory: {memory} MB",
                f"  • Storage: {storage}",
                "",
                f"{ProxmoxTheme.ACTIONS['info']} Container is ready for startup"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} Container Creation Failed",
                "",
                f"  • Container Hostname: {hostname}",
                f"  • Target Node: {node}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def container_power_operation(operation: str, success: bool, vmid: str, node: str, 
                                 status: str, error: str = "") -> str:
        """Template for container power operation results.
        
        Args:
            operation: Type of operation (start, stop, shutdown, reboot, suspend, resume)
            success: Whether operation succeeded
            vmid: Container ID
            node: Target node
            status: Container status after operation
            error: Error message if operation failed
            
        Returns:
            Formatted container power operation result string
        """
        operation_emoji = {
            'start': ProxmoxTheme.ACTIONS['start'],
            'stop': ProxmoxTheme.ACTIONS['stop'],
            'shutdown': ProxmoxTheme.ACTIONS['stop'],
            'reboot': ProxmoxTheme.ACTIONS['restart'],
            'suspend': ProxmoxTheme.ACTIONS['lock'],
            'resume': ProxmoxTheme.ACTIONS['unlock']
        }.get(operation.lower(), ProxmoxTheme.ACTIONS['info'])
        
        if success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} Container {operation.title()} Successful",
                "",
                f"{ProxmoxTheme.RESOURCES['container']} Container {vmid}",
                f"  • Node: {node}",
                f"  • Operation: {operation.title()}",
                f"  • Status: {status.upper()}",
                "",
                f"{operation_emoji} Container is now {status}"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} Container {operation.title()} Failed",
                "",
                f"  • Container ID: {vmid}",
                f"  • Target Node: {node}",
                f"  • Operation: {operation.title()}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def container_config_result(success: bool, vmid: str, node: str, config: Dict[str, Any] = None, 
                               error: str = "") -> str:
        """Template for container configuration operation results.
        
        Args:
            success: Whether operation succeeded
            vmid: Container ID
            node: Target node
            config: Container configuration data
            error: Error message if operation failed
            
        Returns:
            Formatted container configuration result string
        """
        if success and config:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} Container Configuration Retrieved",
                "",
                f"{ProxmoxTheme.RESOURCES['container']} Container {vmid}",
                f"  • Node: {node}",
                f"  • Hostname: {config.get('hostname', 'N/A')}",
                f"  • CPU Cores: {config.get('cores', 'N/A')}",
                f"  • Memory: {config.get('memory', 'N/A')} MB",
                f"  • Template: {config.get('template', 'N/A')}",
                f"  • Status: {config.get('status', 'N/A')}"
            ]
            
            # Add additional configuration details if available
            if config.get('description'):
                result.append(f"  • Description: {config['description']}")
            if config.get('arch'):
                result.append(f"  • Architecture: {config['arch']}")
        elif success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} Container Configuration Updated",
                "",
                f"{ProxmoxTheme.RESOURCES['container']} Container {vmid}",
                f"  • Node: {node}",
                f"  • Status: Configuration updated successfully"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} Container Configuration Operation Failed",
                "",
                f"  • Container ID: {vmid}",
                f"  • Target Node: {node}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)

    @staticmethod
    def container_snapshot_result(success: bool, vmid: str, node: str, snapname: str, 
                                 operation: str, error: str = "") -> str:
        """Template for container snapshot operation results.
        
        Args:
            success: Whether operation succeeded
            vmid: Container ID
            node: Target node
            snapname: Snapshot name
            operation: Type of operation (create, delete, rollback)
            error: Error message if operation failed
            
        Returns:
            Formatted container snapshot result string
        """
        operation_emoji = {
            'create': ProxmoxTheme.ACTIONS['create'],
            'delete': ProxmoxTheme.ACTIONS['delete'],
            'rollback': ProxmoxTheme.ACTIONS['restart']
        }.get(operation.lower(), ProxmoxTheme.ACTIONS['info'])
        
        if success:
            result = [
                f"{ProxmoxTheme.ACTIONS['success']} Container Snapshot {operation.title()} Successful",
                "",
                f"{ProxmoxTheme.RESOURCES['snapshot']} Snapshot: {snapname}",
                f"  • Container ID: {vmid}",
                f"  • Node: {node}",
                f"  • Operation: {operation.title()}",
                "",
                f"{operation_emoji} Snapshot {operation} completed"
            ]
        else:
            result = [
                f"{ProxmoxTheme.ACTIONS['error']} Container Snapshot {operation.title()} Failed",
                "",
                f"  • Snapshot: {snapname}",
                f"  • Container ID: {vmid}",
                f"  • Target Node: {node}",
                f"  • Operation: {operation.title()}",
                f"  • Error: {error or 'Unknown error'}"
            ]
        
        return "\n".join(result)
