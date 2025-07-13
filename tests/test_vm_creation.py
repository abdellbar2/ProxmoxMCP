"""
Tests for VM creation functionality.
"""
import pytest
from unittest.mock import Mock, patch
from mcp.types import TextContent

from src.proxmox_mcp.tools.vm import VMTools


class TestVMCreation:
    """Test VM creation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_proxmox = Mock()
        self.vm_tools = VMTools(self.mock_proxmox)

    def test_create_vm_success(self):
        """Test successful VM creation."""
        # Mock existing VMs (empty list)
        self.mock_proxmox.nodes.return_value.qemu.get.return_value = []
        
        # Mock VM creation
        self.mock_proxmox.nodes.return_value.qemu.post.return_value = {"vmid": "100"}
        
        # Test VM creation
        result = self.vm_tools.create_vm(
            node="pve1",
            vmid="100",
            name="test-vm",
            cores=2,
            memory=2048,
            storage="local-lvm",
            ostype="l26"
        )
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "VM Created Successfully" in result[0].text
        assert "test-vm" in result[0].text
        assert "100" in result[0].text

    def test_create_vm_id_exists(self):
        """Test VM creation with existing VM ID."""
        # Mock existing VM with same ID
        self.mock_proxmox.nodes.return_value.qemu.get.return_value = [
            {"vmid": "100", "name": "existing-vm"}
        ]
        
        # Test VM creation should fail
        with pytest.raises(ValueError, match="VM ID 100 already exists"):
            self.vm_tools.create_vm(
                node="pve1",
                vmid="100",
                name="test-vm",
                cores=2,
                memory=2048,
                storage="local-lvm",
                ostype="l26"
            )

    def test_create_vm_api_error(self):
        """Test VM creation with API error."""
        # Mock existing VMs (empty list)
        self.mock_proxmox.nodes.return_value.qemu.get.return_value = []
        
        # Mock API error
        self.mock_proxmox.nodes.return_value.qemu.post.side_effect = Exception("API Error")
        
        # Test VM creation should fail
        with pytest.raises(RuntimeError, match="Failed to create VM test-vm on node pve1"):
            self.vm_tools.create_vm(
                node="pve1",
                vmid="100",
                name="test-vm",
                cores=2,
                memory=2048,
                storage="local-lvm",
                ostype="l26"
            )

    def test_create_vm_configuration(self):
        """Test VM creation with correct configuration."""
        # Mock existing VMs (empty list)
        self.mock_proxmox.nodes.return_value.qemu.get.return_value = []
        
        # Mock VM creation
        mock_post = self.mock_proxmox.nodes.return_value.qemu.post
        
        # Test VM creation
        self.vm_tools.create_vm(
            node="pve1",
            vmid="100",
            name="test-vm",
            cores=4,
            memory=4096,
            storage="ceph-prod",
            ostype="win10"
        )
        
        # Verify correct configuration was passed
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]  # Get keyword arguments
        
        assert call_args['vmid'] == "100"
        assert call_args['name'] == "test-vm"
        assert call_args['cores'] == 4
        assert call_args['memory'] == 4096
        assert call_args['ostype'] == "win10"
        assert call_args['sata0'] == "ceph-prod:32"
        assert call_args['net0'] == "virtio,bridge=vmbr0" 