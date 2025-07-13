"""
LXC container-related tools for Proxmox MCP.

This module provides tools for managing and interacting with Proxmox LXC containers:
- Listing all containers across the cluster with their status
- Creating new LXC containers from templates
- Container lifecycle management (start, stop, shutdown, reboot, suspend, resume)
- Configuration management (get, update)
- Command execution within containers
- Container cloning and destruction
- Snapshot management (create, delete, rollback)

The tools implement comprehensive container management following the same patterns
as VM management, with specialized handling for LXC-specific operations.
"""
from typing import List
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from .definitions import (
    GET_CONTAINERS_DESC, CREATE_CONTAINER_DESC, START_CONTAINER_DESC,
    STOP_CONTAINER_DESC, SHUTDOWN_CONTAINER_DESC, REBOOT_CONTAINER_DESC,
    SUSPEND_CONTAINER_DESC, RESUME_CONTAINER_DESC, GET_CONTAINER_CONFIG_DESC,
    UPDATE_CONTAINER_CONFIG_DESC, EXECUTE_CONTAINER_COMMAND_DESC,
    CLONE_CONTAINER_DESC, DESTROY_CONTAINER_DESC, GET_CONTAINER_SNAPSHOTS_DESC,
    CREATE_CONTAINER_SNAPSHOT_DESC, DELETE_CONTAINER_SNAPSHOT_DESC,
    ROLLBACK_CONTAINER_SNAPSHOT_DESC
)

class LXCTools(ProxmoxTool):
    """Tools for managing Proxmox LXC containers.
    
    Provides functionality for:
    - Retrieving cluster-wide container information
    - Creating new containers from templates
    - Managing container lifecycle (start, stop, shutdown, reboot, suspend, resume)
    - Configuration management (get, update)
    - Command execution within containers
    - Container cloning and destruction
    - Snapshot management (create, delete, rollback)
    
    Implements comprehensive container management with proper error handling
    and fallback mechanisms for scenarios where detailed container information
    might be temporarily unavailable.
    """

    def __init__(self, proxmox_api):
        """Initialize LXC tools.

        Args:
            proxmox_api: Initialized ProxmoxAPI instance
        """
        super().__init__(proxmox_api)

    def get_containers(self) -> List[Content]:
        """List all LXC containers across the cluster with detailed status.

        Retrieves comprehensive information for each container including:
        - Basic identification (ID, name, hostname)
        - Runtime status (running, stopped, suspended)
        - Resource allocation and usage:
          * CPU cores
          * Memory allocation and usage
        - Node placement
        - Template information
        
        Implements a fallback mechanism that returns basic information
        if detailed configuration retrieval fails for any container.

        Returns:
            List of Content objects containing formatted container information

        Raises:
            RuntimeError: If the cluster-wide container query fails
        """
        try:
            result = []
            for node in self.proxmox.nodes.get():
                node_name = node["node"]
                containers = self.proxmox.nodes(node_name).lxc.get()
                for container in containers:
                    vmid = container["vmid"]
                    # Get container config for detailed info
                    try:
                        config = self.proxmox.nodes(node_name).lxc(vmid).config.get()
                        result.append({
                            "vmid": vmid,
                            "name": container["name"],
                            "hostname": config.get("hostname", "N/A"),
                            "status": container["status"],
                            "node": node_name,
                            "cpus": config.get("cores", "N/A"),
                            "memory": {
                                "used": container.get("mem", 0),
                                "total": container.get("maxmem", 0)
                            },
                            "template": config.get("template", "N/A")
                        })
                    except Exception:
                        # Fallback if can't get config
                        result.append({
                            "vmid": vmid,
                            "name": container["name"],
                            "hostname": "N/A",
                            "status": container["status"],
                            "node": node_name,
                            "cpus": "N/A",
                            "memory": {
                                "used": container.get("mem", 0),
                                "total": container.get("maxmem", 0)
                            },
                            "template": "N/A"
                        })
            return self._format_response(result, "containers")
        except Exception as e:
            self._handle_error("get containers", e)

    def create_container(self, node: str, vmid: str, hostname: str, template: str,
                        storage: str, cores: int, memory: int, password: str) -> List[Content]:
        """Create a new LXC container on a Proxmox node.

        Creates a new container with the specified configuration including:
        - Basic container settings (hostname, template)
        - Resource allocation (CPU cores, memory)
        - Storage configuration (root disk on specified storage pool)
        - Network configuration (default bridge)
        - Root password setup

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            hostname: Container hostname (e.g., 'web-server', 'db-server')
            template: Template to use (e.g., 'ubuntu-20.04-standard')
            storage: Storage pool (e.g., 'local-lvm', 'ceph-prod')
            cores: CPU cores (e.g., 2, 4, 8)
            memory: Memory in MB (e.g., 2048, 4096, 8192)
            password: Root password for container

        Returns:
            List of Content objects containing formatted creation result

        Raises:
            ValueError: If container ID already exists, invalid parameters, or template not found
            RuntimeError: If container creation fails due to API errors or insufficient resources
        """
        try:
            # Check if container ID already exists
            try:
                existing_containers = self.proxmox.nodes(node).lxc.get()
                for container in existing_containers:
                    if str(container["vmid"]) == str(vmid):
                        raise ValueError(f"Container ID {vmid} already exists on node {node}")
            except Exception as e:
                if "not found" not in str(e).lower():
                    raise

            # Prepare container configuration
            config = {
                'vmid': vmid,
                'hostname': hostname,
                'template': template,
                'storage': storage,
                'cores': cores,
                'memory': memory,
                'password': password,
                'net0': 'name=eth0,bridge=vmbr0,ip=dhcp'
            }
            
            self.logger.info(f"Creating container {hostname} (ID: {vmid}) on node {node}")
            
            # Create container using Proxmox API
            result = self.proxmox.nodes(node).lxc.post(**config)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_creation_result(
                success=True,
                vmid=vmid,
                node=node,
                hostname=hostname,
                template=template,
                cores=cores,
                memory=memory,
                storage=storage
            )
            
            return [Content(type="text", text=formatted)]
        except ValueError:
            # Re-raise ValueError for validation errors
            raise
        except Exception as e:
            self._handle_error(f"create container {hostname} on node {node}", e)

    def start_container(self, node: str, vmid: str) -> List[Content]:
        """Start an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted start result

        Raises:
            ValueError: If container is not found or already running
            RuntimeError: If container start fails due to API errors
        """
        try:
            self.logger.info(f"Starting container {vmid} on node {node}")
            
            # Start container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.start.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="start",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"start container {vmid} on node {node}", e)

    def stop_container(self, node: str, vmid: str) -> List[Content]:
        """Stop an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted stop result

        Raises:
            ValueError: If container is not found or already stopped
            RuntimeError: If container stop fails due to API errors
        """
        try:
            self.logger.info(f"Stopping container {vmid} on node {node}")
            
            # Stop container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.stop.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="stop",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"stop container {vmid} on node {node}", e)

    def shutdown_container(self, node: str, vmid: str) -> List[Content]:
        """Shutdown an LXC container gracefully.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted shutdown result

        Raises:
            ValueError: If container is not found or already stopped
            RuntimeError: If container shutdown fails due to API errors
        """
        try:
            self.logger.info(f"Shutting down container {vmid} on node {node}")
            
            # Shutdown container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.shutdown.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="shutdown",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"shutdown container {vmid} on node {node}", e)

    def reboot_container(self, node: str, vmid: str) -> List[Content]:
        """Reboot an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted reboot result

        Raises:
            ValueError: If container is not found or not running
            RuntimeError: If container reboot fails due to API errors
        """
        try:
            self.logger.info(f"Rebooting container {vmid} on node {node}")
            
            # Reboot container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.reboot.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="reboot",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"reboot container {vmid} on node {node}", e)

    def suspend_container(self, node: str, vmid: str) -> List[Content]:
        """Suspend an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted suspend result

        Raises:
            ValueError: If container is not found or not running
            RuntimeError: If container suspend fails due to API errors
        """
        try:
            self.logger.info(f"Suspending container {vmid} on node {node}")
            
            # Suspend container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.suspend.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="suspend",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"suspend container {vmid} on node {node}", e)

    def resume_container(self, node: str, vmid: str) -> List[Content]:
        """Resume a suspended LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted resume result

        Raises:
            ValueError: If container is not found or not suspended
            RuntimeError: If container resume fails due to API errors
        """
        try:
            self.logger.info(f"Resuming container {vmid} on node {node}")
            
            # Resume container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.resume.post()
            
            # Get updated container status
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            status = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="resume",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"resume container {vmid} on node {node}", e)

    def get_container_config(self, node: str, vmid: str) -> List[Content]:
        """Get LXC container configuration.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted container configuration

        Raises:
            ValueError: If container is not found
            RuntimeError: If configuration retrieval fails
        """
        try:
            self.logger.info(f"Getting configuration for container {vmid} on node {node}")
            
            # Get container configuration using Proxmox API
            config = self.proxmox.nodes(node).lxc(vmid).config.get()
            
            # Get container status for additional info
            container_status = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            config['status'] = container_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_config_result(
                success=True,
                vmid=vmid,
                node=node,
                config=config
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"get configuration for container {vmid} on node {node}", e)

    def update_container_config(self, node: str, vmid: str, **config_params) -> List[Content]:
        """Update LXC container configuration.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            **config_params: Configuration parameters to update

        Returns:
            List of Content objects containing formatted update result

        Raises:
            ValueError: If container is not found or invalid parameters
            RuntimeError: If configuration update fails
        """
        try:
            self.logger.info(f"Updating configuration for container {vmid} on node {node}")
            
            # Update container configuration using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).config.put(**config_params)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_config_result(
                success=True,
                vmid=vmid,
                node=node
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"update configuration for container {vmid} on node {node}", e)

    async def execute_command(self, node: str, vmid: str, command: str) -> List[Content]:
        """Execute a command in an LXC container.

        Uses the container console to execute commands within a running container.
        Requires:
        - Container must be running
        - Command execution permissions must be enabled

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            command: Shell command to run (e.g., 'uname -a', 'systemctl status nginx')

        Returns:
            List of Content objects containing formatted command output

        Raises:
            ValueError: If container is not found, not running, or command execution fails
            RuntimeError: If command execution fails due to permissions or other issues
        """
        try:
            # Execute command using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).status.current.get()
            if result.get("status") != "running":
                raise ValueError(f"Container {vmid} is not running (status: {result.get('status')})")
            
            # Execute command
            exec_result = self.proxmox.nodes(node).lxc(vmid).exec.post(command=command)
            
            # Format response
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_command_output(
                success=True,
                command=command,
                output=exec_result.get("output", ""),
                error=exec_result.get("error")
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"execute command on container {vmid}", e)

    def clone_container(self, node: str, vmid: str, newid: str, name: str, storage: str) -> List[Content]:
        """Clone an existing LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Source container ID (e.g., '200', '201')
            newid: New container ID (e.g., '201', '202')
            name: New container name (e.g., 'web-server-clone')
            storage: Storage pool for clone (e.g., 'local-lvm')

        Returns:
            List of Content objects containing formatted clone result

        Raises:
            ValueError: If source container not found or new ID already exists
            RuntimeError: If cloning fails due to API errors
        """
        try:
            self.logger.info(f"Cloning container {vmid} to {newid} on node {node}")
            
            # Clone container using Proxmox API
            config = {
                'newid': newid,
                'name': name,
                'storage': storage
            }
            result = self.proxmox.nodes(node).lxc(vmid).clone.post(**config)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_creation_result(
                success=True,
                vmid=newid,
                node=node,
                hostname=name,
                template="cloned",
                cores=0,
                memory=0,
                storage=storage
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"clone container {vmid} to {newid} on node {node}", e)

    def destroy_container(self, node: str, vmid: str) -> List[Content]:
        """Destroy an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted destroy result

        Raises:
            ValueError: If container is not found
            RuntimeError: If container destruction fails
        """
        try:
            self.logger.info(f"Destroying container {vmid} on node {node}")
            
            # Destroy container using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).delete()
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_power_operation(
                operation="destroy",
                success=True,
                vmid=vmid,
                node=node,
                status="destroyed"
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"destroy container {vmid} on node {node}", e)

    def get_container_snapshots(self, node: str, vmid: str) -> List[Content]:
        """Get LXC container snapshots.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')

        Returns:
            List of Content objects containing formatted snapshot list

        Raises:
            ValueError: If container is not found
            RuntimeError: If snapshot retrieval fails
        """
        try:
            self.logger.info(f"Getting snapshots for container {vmid} on node {node}")
            
            # Get snapshots using Proxmox API
            snapshots = self.proxmox.nodes(node).lxc(vmid).snapshot.get()
            
            # Format response
            import json
            formatted = json.dumps(snapshots, indent=2)
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"get snapshots for container {vmid} on node {node}", e)

    def create_container_snapshot(self, node: str, vmid: str, snapname: str, description: str = "") -> List[Content]:
        """Create a snapshot of an LXC container.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            snapname: Snapshot name (e.g., 'backup-2024-01-01')
            description: Snapshot description

        Returns:
            List of Content objects containing formatted snapshot creation result

        Raises:
            ValueError: If container is not found or snapshot name already exists
            RuntimeError: If snapshot creation fails
        """
        try:
            self.logger.info(f"Creating snapshot {snapname} for container {vmid} on node {node}")
            
            # Create snapshot using Proxmox API
            config = {'snapname': snapname}
            if description:
                config['description'] = description
            
            result = self.proxmox.nodes(node).lxc(vmid).snapshot.post(**config)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_snapshot_result(
                success=True,
                vmid=vmid,
                node=node,
                snapname=snapname,
                operation="create"
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"create snapshot {snapname} for container {vmid} on node {node}", e)

    def delete_container_snapshot(self, node: str, vmid: str, snapname: str) -> List[Content]:
        """Delete a container snapshot.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            snapname: Snapshot name (e.g., 'backup-2024-01-01')

        Returns:
            List of Content objects containing formatted snapshot deletion result

        Raises:
            ValueError: If container or snapshot is not found
            RuntimeError: If snapshot deletion fails
        """
        try:
            self.logger.info(f"Deleting snapshot {snapname} for container {vmid} on node {node}")
            
            # Delete snapshot using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).snapshot(snapname).delete()
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_snapshot_result(
                success=True,
                vmid=vmid,
                node=node,
                snapname=snapname,
                operation="delete"
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"delete snapshot {snapname} for container {vmid} on node {node}", e)

    def rollback_container_snapshot(self, node: str, vmid: str, snapname: str) -> List[Content]:
        """Rollback container to a snapshot.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: Container ID number (e.g., '200', '201')
            snapname: Snapshot name (e.g., 'backup-2024-01-01')

        Returns:
            List of Content objects containing formatted rollback result

        Raises:
            ValueError: If container or snapshot is not found
            RuntimeError: If rollback fails
        """
        try:
            self.logger.info(f"Rolling back container {vmid} to snapshot {snapname} on node {node}")
            
            # Rollback to snapshot using Proxmox API
            result = self.proxmox.nodes(node).lxc(vmid).snapshot(snapname).rollback.post()
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.container_snapshot_result(
                success=True,
                vmid=vmid,
                node=node,
                snapname=snapname,
                operation="rollback"
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"rollback container {vmid} to snapshot {snapname} on node {node}", e) 