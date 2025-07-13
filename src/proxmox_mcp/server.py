"""
Main server implementation for Proxmox MCP.

This module implements the core MCP server for Proxmox integration, providing:
- Configuration loading and validation
- Logging setup
- Proxmox API connection management
- MCP tool registration and routing
- Signal handling for graceful shutdown

The server exposes a set of tools for managing Proxmox resources including:
- Node management
- VM operations
- Storage management
- Cluster status monitoring
"""
import logging
import os
import sys
import signal
from typing import Optional, List, Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from mcp.types import TextContent as Content
from pydantic import Field

from .config.loader import load_config
from .core.logging import setup_logging
from .core.proxmox import ProxmoxManager
from .tools.node import NodeTools
from .tools.vm import VMTools
from .tools.lxc import LXCTools
from .tools.storage import StorageTools
from .tools.cluster import ClusterTools
from .tools.definitions import (
    GET_NODES_DESC,
    GET_NODE_STATUS_DESC,
    GET_VMS_DESC,
    EXECUTE_VM_COMMAND_DESC,
    CREATE_VM_DESC,
    START_VM_DESC,
    STOP_VM_DESC,
    SHUTDOWN_VM_DESC,
    REBOOT_VM_DESC,
    GET_VM_CONFIG_DESC,
    UPDATE_VM_CONFIG_DESC,
    GET_CONTAINERS_DESC,
    CREATE_CONTAINER_DESC,
    START_CONTAINER_DESC,
    STOP_CONTAINER_DESC,
    SHUTDOWN_CONTAINER_DESC,
    REBOOT_CONTAINER_DESC,
    SUSPEND_CONTAINER_DESC,
    RESUME_CONTAINER_DESC,
    GET_CONTAINER_CONFIG_DESC,
    UPDATE_CONTAINER_CONFIG_DESC,
    EXECUTE_CONTAINER_COMMAND_DESC,
    CLONE_CONTAINER_DESC,
    DESTROY_CONTAINER_DESC,
    GET_CONTAINER_SNAPSHOTS_DESC,
    CREATE_CONTAINER_SNAPSHOT_DESC,
    DELETE_CONTAINER_SNAPSHOT_DESC,
    ROLLBACK_CONTAINER_SNAPSHOT_DESC,
    GET_STORAGE_DESC,
    GET_CLUSTER_STATUS_DESC
)

class ProxmoxMCPServer:
    """Main server class for Proxmox MCP."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the server.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config.logging)
        
        # Initialize core components
        self.proxmox_manager = ProxmoxManager(self.config.proxmox, self.config.auth)
        self.proxmox = self.proxmox_manager.get_api()
        
        # Initialize tools
        self.node_tools = NodeTools(self.proxmox)
        self.vm_tools = VMTools(self.proxmox)
        self.lxc_tools = LXCTools(self.proxmox)
        self.storage_tools = StorageTools(self.proxmox)
        self.cluster_tools = ClusterTools(self.proxmox)
        
        # Initialize MCP server
        self.mcp = FastMCP("ProxmoxMCP")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Register MCP tools with the server.
        
        Initializes and registers all available tools with the MCP server:
        - Node management tools (list nodes, get status)
        - VM operation tools (list VMs, execute commands)
        - Storage management tools (list storage)
        - Cluster tools (get cluster status)
        
        Each tool is registered with appropriate descriptions and parameter
        validation using Pydantic models.
        """
        
        # Node tools
        @self.mcp.tool(description=GET_NODES_DESC)
        def get_nodes():
            return self.node_tools.get_nodes()

        @self.mcp.tool(description=GET_NODE_STATUS_DESC)
        def get_node_status(
            node: Annotated[str, Field(description="Name/ID of node to query (e.g. 'pve1', 'proxmox-node2')")]
        ):
            return self.node_tools.get_node_status(node)

        # VM tools
        @self.mcp.tool(description=GET_VMS_DESC)
        def get_vms():
            return self.vm_tools.get_vms()

        @self.mcp.tool(description=CREATE_VM_DESC)
        def create_vm(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")],
            name: Annotated[str, Field(description="VM name (e.g. 'ubuntu-server')")],
            cores: Annotated[int, Field(description="CPU cores (e.g. 2)")],
            memory: Annotated[int, Field(description="Memory in MB (e.g. 2048)")],
            storage: Annotated[str, Field(description="Storage pool (e.g. 'local-lvm')")],
            ostype: Annotated[str, Field(description="OS type (e.g. 'l26', 'win10')")]
        ):
            return self.vm_tools.create_vm(node, vmid, name, cores, memory, storage, ostype)

        @self.mcp.tool(description=START_VM_DESC)
        def start_vm(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")]
        ):
            return self.vm_tools.start_vm(node, vmid)

        @self.mcp.tool(description=STOP_VM_DESC)
        def stop_vm(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")]
        ):
            return self.vm_tools.stop_vm(node, vmid)

        @self.mcp.tool(description=SHUTDOWN_VM_DESC)
        def shutdown_vm(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")]
        ):
            return self.vm_tools.shutdown_vm(node, vmid)

        @self.mcp.tool(description=REBOOT_VM_DESC)
        def reboot_vm(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")]
        ):
            return self.vm_tools.reboot_vm(node, vmid)

        @self.mcp.tool(description=GET_VM_CONFIG_DESC)
        def get_vm_config(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")]
        ):
            return self.vm_tools.get_vm_config(node, vmid)

        @self.mcp.tool(description=UPDATE_VM_CONFIG_DESC)
        def update_vm_config(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100')")],
            cores: Annotated[Optional[int], Field(description="CPU cores (e.g. 4)")] = None,
            memory: Annotated[Optional[int], Field(description="Memory in MB (e.g. 4096)")] = None,
            name: Annotated[Optional[str], Field(description="VM name (e.g. 'new-name')")] = None,
            description: Annotated[Optional[str], Field(description="VM description")] = None
        ):
            config_params = {}
            if cores is not None:
                config_params['cores'] = cores
            if memory is not None:
                config_params['memory'] = memory
            if name is not None:
                config_params['name'] = name
            if description is not None:
                config_params['description'] = description
            return self.vm_tools.update_vm_config(node, vmid, **config_params)

        @self.mcp.tool(description=EXECUTE_VM_COMMAND_DESC)
        async def execute_vm_command(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            command: Annotated[str, Field(description="Shell command to run (e.g. 'uname -a', 'systemctl status nginx')")]
        ):
            return await self.vm_tools.execute_command(node, vmid, command)

        # LXC Container tools
        @self.mcp.tool(description=GET_CONTAINERS_DESC)
        def get_containers():
            return self.lxc_tools.get_containers()

        @self.mcp.tool(description=CREATE_CONTAINER_DESC)
        def create_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")],
            hostname: Annotated[str, Field(description="Container hostname (e.g. 'web-server')")],
            template: Annotated[str, Field(description="Template to use (e.g. 'ubuntu-20.04-standard')")],
            storage: Annotated[str, Field(description="Storage pool (e.g. 'local-lvm')")],
            cores: Annotated[int, Field(description="CPU cores (e.g. 2)")],
            memory: Annotated[int, Field(description="Memory in MB (e.g. 2048)")],
            password: Annotated[str, Field(description="Root password for container")]
        ):
            return self.lxc_tools.create_container(node, vmid, hostname, template, storage, cores, memory, password)

        @self.mcp.tool(description=START_CONTAINER_DESC)
        def start_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.start_container(node, vmid)

        @self.mcp.tool(description=STOP_CONTAINER_DESC)
        def stop_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.stop_container(node, vmid)

        @self.mcp.tool(description=SHUTDOWN_CONTAINER_DESC)
        def shutdown_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.shutdown_container(node, vmid)

        @self.mcp.tool(description=REBOOT_CONTAINER_DESC)
        def reboot_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.reboot_container(node, vmid)

        @self.mcp.tool(description=SUSPEND_CONTAINER_DESC)
        def suspend_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.suspend_container(node, vmid)

        @self.mcp.tool(description=RESUME_CONTAINER_DESC)
        def resume_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.resume_container(node, vmid)

        @self.mcp.tool(description=GET_CONTAINER_CONFIG_DESC)
        def get_container_config(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.get_container_config(node, vmid)

        @self.mcp.tool(description=UPDATE_CONTAINER_CONFIG_DESC)
        def update_container_config(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")],
            cores: Annotated[Optional[int], Field(description="CPU cores (e.g. 4)")] = None,
            memory: Annotated[Optional[int], Field(description="Memory in MB (e.g. 4096)")] = None,
            hostname: Annotated[Optional[str], Field(description="Container hostname (e.g. 'new-hostname')")] = None,
            description: Annotated[Optional[str], Field(description="Container description")] = None
        ):
            config_params = {}
            if cores is not None:
                config_params['cores'] = cores
            if memory is not None:
                config_params['memory'] = memory
            if hostname is not None:
                config_params['hostname'] = hostname
            if description is not None:
                config_params['description'] = description
            return self.lxc_tools.update_container_config(node, vmid, **config_params)

        @self.mcp.tool(description=EXECUTE_CONTAINER_COMMAND_DESC)
        async def execute_container_command(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200', '201')")],
            command: Annotated[str, Field(description="Shell command to run (e.g. 'uname -a', 'systemctl status nginx')")]
        ):
            return await self.lxc_tools.execute_command(node, vmid, command)

        @self.mcp.tool(description=CLONE_CONTAINER_DESC)
        def clone_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Source container ID (e.g. '200')")],
            newid: Annotated[str, Field(description="New container ID (e.g. '201')")],
            name: Annotated[str, Field(description="New container name (e.g. 'web-server-clone')")],
            storage: Annotated[str, Field(description="Storage pool for clone (e.g. 'local-lvm')")]
        ):
            return self.lxc_tools.clone_container(node, vmid, newid, name, storage)

        @self.mcp.tool(description=DESTROY_CONTAINER_DESC)
        def destroy_container(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.destroy_container(node, vmid)

        @self.mcp.tool(description=GET_CONTAINER_SNAPSHOTS_DESC)
        def get_container_snapshots(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")]
        ):
            return self.lxc_tools.get_container_snapshots(node, vmid)

        @self.mcp.tool(description=CREATE_CONTAINER_SNAPSHOT_DESC)
        def create_container_snapshot(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")],
            snapname: Annotated[str, Field(description="Snapshot name (e.g. 'backup-2024-01-01')")],
            description: Annotated[Optional[str], Field(description="Snapshot description")] = None
        ):
            return self.lxc_tools.create_container_snapshot(node, vmid, snapname, description)

        @self.mcp.tool(description=DELETE_CONTAINER_SNAPSHOT_DESC)
        def delete_container_snapshot(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")],
            snapname: Annotated[str, Field(description="Snapshot name (e.g. 'backup-2024-01-01')")]
        ):
            return self.lxc_tools.delete_container_snapshot(node, vmid, snapname)

        @self.mcp.tool(description=ROLLBACK_CONTAINER_SNAPSHOT_DESC)
        def rollback_container_snapshot(
            node: Annotated[str, Field(description="Target node name (e.g. 'pve1')")],
            vmid: Annotated[str, Field(description="Container ID number (e.g. '200')")],
            snapname: Annotated[str, Field(description="Snapshot name (e.g. 'backup-2024-01-01')")]
        ):
            return self.lxc_tools.rollback_container_snapshot(node, vmid, snapname)

        # Storage tools
        @self.mcp.tool(description=GET_STORAGE_DESC)
        def get_storage():
            return self.storage_tools.get_storage()

        # Cluster tools
        @self.mcp.tool(description=GET_CLUSTER_STATUS_DESC)
        def get_cluster_status():
            return self.cluster_tools.get_cluster_status()

    def start(self) -> None:
        """Start the MCP server.
        
        Initializes the server with:
        - Signal handlers for graceful shutdown (SIGINT, SIGTERM)
        - Async runtime for handling concurrent requests
        - Error handling and logging
        
        The server runs until terminated by a signal or fatal error.
        """
        import anyio

        def signal_handler(signum, frame):
            self.logger.info("Received signal to shutdown...")
            sys.exit(0)

        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            self.logger.info("Starting MCP server...")
            anyio.run(self.mcp.run_stdio_async)
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    config_path = os.getenv("PROXMOX_MCP_CONFIG")
    if not config_path:
        print("PROXMOX_MCP_CONFIG environment variable must be set")
        sys.exit(1)
    
    try:
        server = ProxmoxMCPServer(config_path)
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
