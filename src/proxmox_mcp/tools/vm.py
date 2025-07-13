"""
VM-related tools for Proxmox MCP.

This module provides tools for managing and interacting with Proxmox VMs:
- Listing all VMs across the cluster with their status
- Retrieving detailed VM information including:
  * Resource allocation (CPU, memory)
  * Runtime status
  * Node placement
- Executing commands within VMs via QEMU guest agent
- Handling VM console operations

The tools implement fallback mechanisms for scenarios where
detailed VM information might be temporarily unavailable.
"""
from typing import List
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from .definitions import (
    GET_VMS_DESC, EXECUTE_VM_COMMAND_DESC, CREATE_VM_DESC,
    START_VM_DESC, STOP_VM_DESC, SHUTDOWN_VM_DESC, REBOOT_VM_DESC,
    GET_VM_CONFIG_DESC, UPDATE_VM_CONFIG_DESC
)
from .console.manager import VMConsoleManager

class VMTools(ProxmoxTool):
    """Tools for managing Proxmox VMs.
    
    Provides functionality for:
    - Retrieving cluster-wide VM information
    - Getting detailed VM status and configuration
    - Creating new virtual machines
    - Executing commands within VMs
    - Managing VM console operations
    
    Implements fallback mechanisms for scenarios where detailed
    VM information might be temporarily unavailable. Integrates
    with QEMU guest agent for VM command execution.
    """

    def __init__(self, proxmox_api):
        """Initialize VM tools.

        Args:
            proxmox_api: Initialized ProxmoxAPI instance
        """
        super().__init__(proxmox_api)
        self.console_manager = VMConsoleManager(proxmox_api)

    def get_vms(self) -> List[Content]:
        """List all virtual machines across the cluster with detailed status.

        Retrieves comprehensive information for each VM including:
        - Basic identification (ID, name)
        - Runtime status (running, stopped)
        - Resource allocation and usage:
          * CPU cores
          * Memory allocation and usage
        - Node placement
        
        Implements a fallback mechanism that returns basic information
        if detailed configuration retrieval fails for any VM.

        Returns:
            List of Content objects containing formatted VM information:
            {
                "vmid": "100",
                "name": "vm-name",
                "status": "running/stopped",
                "node": "node-name",
                "cpus": core_count,
                "memory": {
                    "used": bytes,
                    "total": bytes
                }
            }

        Raises:
            RuntimeError: If the cluster-wide VM query fails
        """
        try:
            result = []
            for node in self.proxmox.nodes.get():
                node_name = node["node"]
                vms = self.proxmox.nodes(node_name).qemu.get()
                for vm in vms:
                    vmid = vm["vmid"]
                    # Get VM config for CPU cores
                    try:
                        config = self.proxmox.nodes(node_name).qemu(vmid).config.get()
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": config.get("cores", "N/A"),
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
                    except Exception:
                        # Fallback if can't get config
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": "N/A",
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
            return self._format_response(result, "vms")
        except Exception as e:
            self._handle_error("get VMs", e)

    def create_vm(self, node: str, vmid: str, name: str, cores: int, 
                  memory: int, storage: str, ostype: str) -> List[Content]:
        """Create a new virtual machine on a Proxmox node.

        Creates a new VM with the specified configuration including:
        - Basic VM settings (name, ID, OS type)
        - Resource allocation (CPU cores, memory)
        - Storage configuration (disk on specified storage pool)
        - Network configuration (default bridge)

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            name: VM name (e.g., 'ubuntu-server', 'web-app')
            cores: CPU cores (e.g., 2, 4, 8)
            memory: Memory in MB (e.g., 2048, 4096, 8192)
            storage: Storage pool (e.g., 'local-lvm', 'ceph-prod')
            ostype: OS type (e.g., 'l26', 'win10', 'other')

        Returns:
            List of Content objects containing formatted creation result:
            {
                "success": true/false,
                "vmid": "100",
                "node": "pve1",
                "message": "VM created successfully"
            }

        Raises:
            ValueError: If VM ID already exists, invalid parameters, or storage not found
            RuntimeError: If VM creation fails due to API errors or insufficient resources
        """
        try:
            # Check if VM ID already exists
            try:
                existing_vms = self.proxmox.nodes(node).qemu.get()
                for vm in existing_vms:
                    if str(vm["vmid"]) == str(vmid):
                        raise ValueError(f"VM ID {vmid} already exists on node {node}")
            except Exception as e:
                if "not found" not in str(e).lower():
                    raise

            # Prepare VM configuration
            config = {
                'vmid': vmid,
                'name': name,
                'cores': cores,
                'memory': memory,
                'ostype': ostype,
                'sata0': f'{storage}:32',  # 32GB disk
                'net0': 'virtio,bridge=vmbr0'
            }
            
            self.logger.info(f"Creating VM {name} (ID: {vmid}) on node {node}")
            
            # Create VM using Proxmox API
            result = self.proxmox.nodes(node).qemu.post(**config)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_creation_result(
                success=True,
                vmid=vmid,
                node=node,
                name=name,
                cores=cores,
                memory=memory,
                storage=storage,
                ostype=ostype
            )
            
            return [Content(type="text", text=formatted)]
        except ValueError:
            # Re-raise ValueError for validation errors
            raise
        except Exception as e:
            self._handle_error(f"create VM {name} on node {node}", e)

    def start_vm(self, node: str, vmid: str) -> List[Content]:
        """Start a virtual machine.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')

        Returns:
            List of Content objects containing formatted start result

        Raises:
            ValueError: If VM is not found or already running
            RuntimeError: If VM start fails due to API errors
        """
        try:
            self.logger.info(f"Starting VM {vmid} on node {node}")
            
            # Start VM using Proxmox API
            result = self.proxmox.nodes(node).qemu(vmid).status.start.post()
            
            # Get updated VM status
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            status = vm_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_power_operation(
                operation="start",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"start VM {vmid} on node {node}", e)

    def stop_vm(self, node: str, vmid: str) -> List[Content]:
        """Stop a virtual machine.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')

        Returns:
            List of Content objects containing formatted stop result

        Raises:
            ValueError: If VM is not found or already stopped
            RuntimeError: If VM stop fails due to API errors
        """
        try:
            self.logger.info(f"Stopping VM {vmid} on node {node}")
            
            # Stop VM using Proxmox API
            result = self.proxmox.nodes(node).qemu(vmid).status.stop.post()
            
            # Get updated VM status
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            status = vm_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_power_operation(
                operation="stop",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"stop VM {vmid} on node {node}", e)

    def shutdown_vm(self, node: str, vmid: str) -> List[Content]:
        """Shutdown a virtual machine gracefully.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')

        Returns:
            List of Content objects containing formatted shutdown result

        Raises:
            ValueError: If VM is not found or already stopped
            RuntimeError: If VM shutdown fails due to API errors
        """
        try:
            self.logger.info(f"Shutting down VM {vmid} on node {node}")
            
            # Shutdown VM using Proxmox API
            result = self.proxmox.nodes(node).qemu(vmid).status.shutdown.post()
            
            # Get updated VM status
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            status = vm_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_power_operation(
                operation="shutdown",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"shutdown VM {vmid} on node {node}", e)

    def reboot_vm(self, node: str, vmid: str) -> List[Content]:
        """Reboot a virtual machine.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')

        Returns:
            List of Content objects containing formatted reboot result

        Raises:
            ValueError: If VM is not found or not running
            RuntimeError: If VM reboot fails due to API errors
        """
        try:
            self.logger.info(f"Rebooting VM {vmid} on node {node}")
            
            # Reboot VM using Proxmox API
            result = self.proxmox.nodes(node).qemu(vmid).status.reset.post()
            
            # Get updated VM status
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            status = vm_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_power_operation(
                operation="reboot",
                success=True,
                vmid=vmid,
                node=node,
                status=status
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"reboot VM {vmid} on node {node}", e)

    def get_vm_config(self, node: str, vmid: str) -> List[Content]:
        """Get virtual machine configuration.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')

        Returns:
            List of Content objects containing formatted VM configuration

        Raises:
            ValueError: If VM is not found
            RuntimeError: If configuration retrieval fails
        """
        try:
            self.logger.info(f"Getting configuration for VM {vmid} on node {node}")
            
            # Get VM configuration using Proxmox API
            config = self.proxmox.nodes(node).qemu(vmid).config.get()
            
            # Get VM status for additional info
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            config['status'] = vm_status.get("status", "unknown")
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_config_result(
                success=True,
                vmid=vmid,
                node=node,
                config=config
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"get configuration for VM {vmid} on node {node}", e)

    def update_vm_config(self, node: str, vmid: str, **config_params) -> List[Content]:
        """Update virtual machine configuration.

        Args:
            node: Target node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            **config_params: Configuration parameters to update

        Returns:
            List of Content objects containing formatted update result

        Raises:
            ValueError: If VM is not found or invalid parameters
            RuntimeError: If configuration update fails
        """
        try:
            self.logger.info(f"Updating configuration for VM {vmid} on node {node}")
            
            # Update VM configuration using Proxmox API
            result = self.proxmox.nodes(node).qemu(vmid).config.put(**config_params)
            
            # Format response
            from ..formatting import ProxmoxTemplates
            formatted = ProxmoxTemplates.vm_config_result(
                success=True,
                vmid=vmid,
                node=node
            )
            
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"update configuration for VM {vmid} on node {node}", e)

    async def execute_command(self, node: str, vmid: str, command: str) -> List[Content]:
        """Execute a command in a VM via QEMU guest agent.

        Uses the QEMU guest agent to execute commands within a running VM.
        Requires:
        - VM must be running
        - QEMU guest agent must be installed and running in the VM
        - Command execution permissions must be enabled

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            command: Shell command to run (e.g., 'uname -a', 'systemctl status nginx')

        Returns:
            List of Content objects containing formatted command output:
            {
                "success": true/false,
                "output": "command output",
                "error": "error message if any"
            }

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If command execution fails due to permissions or other issues
        """
        try:
            result = await self.console_manager.execute_command(node, vmid, command)
            # Use the command output formatter from ProxmoxFormatters
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_command_output(
                success=result["success"],
                command=command,
                output=result["output"],
                error=result.get("error")
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"execute command on VM {vmid}", e)
