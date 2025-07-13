"""
Tests for VM power management and configuration operations.
"""
import pytest
from unittest.mock import Mock, patch
from mcp.types import TextContent

from src.proxmox_mcp.tools.vm import VMTools


class TestVMPowerOperations:
    """Test VM power management operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_proxmox = Mock()
        self.vm_tools = VMTools(self.mock_proxmox)

    def test_start_vm_success(self):
        """Test successful VM start."""
        # Mock VM start
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.start.post.return_value = {}
        
        # Mock VM status
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "running"
        }
        
        # Test VM start
        result = self.vm_tools.start_vm("pve1", "100")
        
        # Verify API calls
        self.mock_proxmox.nodes.assert_called_with("pve1")
        self.mock_proxmox.nodes.return_value.qemu.assert_called_with("100")
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.start.post.assert_called_once()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Start Successful" in result[0].text
        assert "running" in result[0].text

    def test_stop_vm_success(self):
        """Test successful VM stop."""
        # Mock VM stop
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.stop.post.return_value = {}
        
        # Mock VM status
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "stopped"
        }
        
        # Test VM stop
        result = self.vm_tools.stop_vm("pve1", "100")
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.stop.post.assert_called_once()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Stop Successful" in result[0].text
        assert "stopped" in result[0].text

    def test_shutdown_vm_success(self):
        """Test successful VM shutdown."""
        # Mock VM shutdown
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.shutdown.post.return_value = {}
        
        # Mock VM status
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "stopped"
        }
        
        # Test VM shutdown
        result = self.vm_tools.shutdown_vm("pve1", "100")
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.shutdown.post.assert_called_once()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Shutdown Successful" in result[0].text

    def test_reboot_vm_success(self):
        """Test successful VM reboot."""
        # Mock VM reboot
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.reset.post.return_value = {}
        
        # Mock VM status
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "running"
        }
        
        # Test VM reboot
        result = self.vm_tools.reboot_vm("pve1", "100")
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.reset.post.assert_called_once()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Reboot Successful" in result[0].text

    def test_power_operation_api_error(self):
        """Test power operation with API error."""
        # Mock API error
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.start.post.side_effect = Exception("API Error")
        
        # Test VM start with error
        with pytest.raises(Exception):
            self.vm_tools.start_vm("pve1", "100")


class TestVMConfiguration:
    """Test VM configuration operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_proxmox = Mock()
        self.vm_tools = VMTools(self.mock_proxmox)

    def test_get_vm_config_success(self):
        """Test successful VM configuration retrieval."""
        # Mock VM configuration
        mock_config = {
            "name": "test-vm",
            "cores": 2,
            "memory": 2048,
            "ostype": "l26",
            "description": "Test VM"
        }
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.get.return_value = mock_config
        
        # Mock VM status
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "running"
        }
        
        # Test VM config retrieval
        result = self.vm_tools.get_vm_config("pve1", "100")
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.get.assert_called_once()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Configuration Retrieved" in result[0].text
        assert "test-vm" in result[0].text

    def test_update_vm_config_success(self):
        """Test successful VM configuration update."""
        # Mock VM config update
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.put.return_value = {}
        
        # Test VM config update
        result = self.vm_tools.update_vm_config("pve1", "100", cores=4, memory=4096)
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.put.assert_called_with(
            cores=4, memory=4096
        )
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "VM Configuration Updated" in result[0].text

    def test_update_vm_config_partial(self):
        """Test partial VM configuration update."""
        # Mock VM config update
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.put.return_value = {}
        
        # Test VM config update with only name
        result = self.vm_tools.update_vm_config("pve1", "100", name="new-name")
        
        # Verify API calls
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.put.assert_called_with(
            name="new-name"
        )
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

    def test_config_operation_api_error(self):
        """Test configuration operation with API error."""
        # Mock API error
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.get.side_effect = Exception("API Error")
        
        # Test VM config retrieval with error
        with pytest.raises(Exception):
            self.vm_tools.get_vm_config("pve1", "100")


class TestVMOperationsIntegration:
    """Integration tests for VM operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_proxmox = Mock()
        self.vm_tools = VMTools(self.mock_proxmox)

    def test_vm_lifecycle_workflow(self):
        """Test complete VM lifecycle workflow."""
        # Mock all operations
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.start.post.return_value = {}
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
            "status": "running"
        }
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.get.return_value = {
            "name": "test-vm",
            "cores": 2,
            "memory": 2048
        }
        self.mock_proxmox.nodes.return_value.qemu.return_value.config.put.return_value = {}
        self.mock_proxmox.nodes.return_value.qemu.return_value.status.shutdown.post.return_value = {}
        
        # Test workflow: start -> get config -> update config -> shutdown
        start_result = self.vm_tools.start_vm("pve1", "100")
        config_result = self.vm_tools.get_vm_config("pve1", "100")
        update_result = self.vm_tools.update_vm_config("pve1", "100", cores=4)
        shutdown_result = self.vm_tools.shutdown_vm("pve1", "100")
        
        # Verify all operations completed successfully
        assert all(isinstance(result, list) and len(result) == 1 for result in [start_result, config_result, update_result, shutdown_result])
        assert all("Successful" in result[0].text for result in [start_result, config_result, update_result, shutdown_result]) 