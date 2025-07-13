"""
Tests for LXC container tools.

This module tests the LXC container management functionality:
- Container listing and status retrieval
- Container lifecycle operations (create, start, stop, etc.)
- Configuration management
- Command execution
- Snapshot operations
- Error handling and edge cases

Tests follow the same patterns as VM tests with appropriate
mocking and validation for LXC-specific operations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.proxmox_mcp.tools.lxc import LXCTools

class TestLXCTools:
    """Test cases for LXC container tools."""

    @pytest.fixture
    def mock_proxmox_api(self):
        """Create a mock Proxmox API for testing."""
        mock_api = Mock()
        
        # Mock nodes
        mock_nodes = [{"node": "pve1"}, {"node": "pve2"}]
        mock_api.nodes.get.return_value = mock_nodes
        
        # Mock container list for each node
        mock_containers = [
            {"vmid": "200", "name": "web-server", "status": "running", "mem": 1024, "maxmem": 2048},
            {"vmid": "201", "name": "db-server", "status": "stopped", "mem": 0, "maxmem": 4096}
        ]
        mock_api.nodes.return_value.lxc.get.return_value = mock_containers
        
        # Mock container config
        mock_config = {
            "hostname": "test-container",
            "cores": 2,
            "memory": 2048,
            "template": "ubuntu-20.04-standard"
        }
        mock_api.nodes.return_value.lxc.return_value.config.get.return_value = mock_config
        
        # Mock container status
        mock_status = {"status": "running"}
        mock_api.nodes.return_value.lxc.return_value.status.current.get.return_value = mock_status
        
        return mock_api

    @pytest.fixture
    def lxc_tools(self, mock_proxmox_api):
        """Create LXCTools instance with mocked API."""
        return LXCTools(mock_proxmox_api)

    def test_get_containers_success(self, lxc_tools):
        """Test successful container listing."""
        with patch.object(lxc_tools, '_format_response') as mock_format:
            mock_format.return_value = [{"type": "text", "text": "containers"}]
            result = lxc_tools.get_containers()
            
            assert result == [{"type": "text", "text": "containers"}]
            mock_format.assert_called_once()

    def test_get_containers_with_fallback(self, lxc_tools, mock_proxmox_api):
        """Test container listing with config retrieval fallback."""
        # Mock config retrieval failure
        mock_proxmox_api.nodes.return_value.lxc.return_value.config.get.side_effect = Exception("Config error")
        
        with patch.object(lxc_tools, '_format_response') as mock_format:
            mock_format.return_value = [{"type": "text", "text": "containers"}]
            result = lxc_tools.get_containers()
            
            assert result == [{"type": "text", "text": "containers"}]
            mock_format.assert_called_once()

    def test_create_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container creation."""
        # Mock existing containers check
        mock_proxmox_api.nodes.return_value.lxc.get.return_value = []
        
        # Mock container creation
        mock_proxmox_api.nodes.return_value.lxc.post.return_value = {"data": "success"}
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_creation_result.return_value = "Container created"
            
            result = lxc_tools.create_container(
                node="pve1",
                vmid="200",
                hostname="test-container",
                template="ubuntu-20.04-standard",
                storage="local-lvm",
                cores=2,
                memory=2048,
                password="testpass"
            )
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container created"

    def test_create_container_id_exists(self, lxc_tools, mock_proxmox_api):
        """Test container creation with existing ID."""
        # Mock existing container
        mock_proxmox_api.nodes.return_value.lxc.get.return_value = [
            {"vmid": "200", "name": "existing"}
        ]
        
        with pytest.raises(ValueError, match="Container ID 200 already exists"):
            lxc_tools.create_container(
                node="pve1",
                vmid="200",
                hostname="test-container",
                template="ubuntu-20.04-standard",
                storage="local-lvm",
                cores=2,
                memory=2048,
                password="testpass"
            )

    def test_start_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container start."""
        # Mock container start
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.start.post.return_value = "started"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container started"
            
            result = lxc_tools.start_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container started"

    def test_stop_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container stop."""
        # Mock container stop
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.stop.post.return_value = "stopped"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container stopped"
            
            result = lxc_tools.stop_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container stopped"

    def test_shutdown_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container shutdown."""
        # Mock container shutdown
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.shutdown.post.return_value = "shutdown"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container shutdown"
            
            result = lxc_tools.shutdown_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container shutdown"

    def test_reboot_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container reboot."""
        # Mock container reboot
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.reboot.post.return_value = "rebooted"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container rebooted"
            
            result = lxc_tools.reboot_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container rebooted"

    def test_suspend_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container suspend."""
        # Mock container suspend
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.suspend.post.return_value = "suspended"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container suspended"
            
            result = lxc_tools.suspend_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container suspended"

    def test_resume_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container resume."""
        # Mock container resume
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.resume.post.return_value = "resumed"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container resumed"
            
            result = lxc_tools.resume_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container resumed"

    def test_get_container_config_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container config retrieval."""
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_config_result.return_value = "Container config"
            
            result = lxc_tools.get_container_config("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container config"

    def test_update_container_config_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container config update."""
        # Mock config update
        mock_proxmox_api.nodes.return_value.lxc.return_value.config.put.return_value = "updated"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_config_result.return_value = "Config updated"
            
            result = lxc_tools.update_container_config("pve1", "200", cores=4, memory=4096)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Config updated"

    @pytest.mark.asyncio
    async def test_execute_command_success(self, lxc_tools, mock_proxmox_api):
        """Test successful command execution."""
        # Mock command execution
        mock_proxmox_api.nodes.return_value.lxc.return_value.exec.post.return_value = {
            "output": "Linux test-container 5.4.0",
            "exit_code": 0
        }
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxFormatters') as mock_formatters:
            mock_formatters.format_command_output.return_value = "Command executed"
            
            result = await lxc_tools.execute_command("pve1", "200", "uname -a")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Command executed"

    @pytest.mark.asyncio
    async def test_execute_command_container_not_running(self, lxc_tools, mock_proxmox_api):
        """Test command execution on non-running container."""
        # Mock container not running
        mock_proxmox_api.nodes.return_value.lxc.return_value.status.current.get.return_value = {
            "status": "stopped"
        }
        
        with pytest.raises(ValueError, match="Container 200 is not running"):
            await lxc_tools.execute_command("pve1", "200", "uname -a")

    def test_clone_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container cloning."""
        # Mock container clone
        mock_proxmox_api.nodes.return_value.lxc.return_value.clone.post.return_value = "cloned"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_creation_result.return_value = "Container cloned"
            
            result = lxc_tools.clone_container("pve1", "200", "201", "clone", "local-lvm")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container cloned"

    def test_destroy_container_success(self, lxc_tools, mock_proxmox_api):
        """Test successful container destruction."""
        # Mock container destruction
        mock_proxmox_api.nodes.return_value.lxc.return_value.delete.return_value = "destroyed"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_power_operation.return_value = "Container destroyed"
            
            result = lxc_tools.destroy_container("pve1", "200")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Container destroyed"

    def test_get_container_snapshots_success(self, lxc_tools, mock_proxmox_api):
        """Test successful snapshot listing."""
        # Mock snapshots
        mock_snapshots = [
            {"name": "backup1", "time": "2024-01-01T12:00:00Z"},
            {"name": "backup2", "time": "2024-01-02T12:00:00Z"}
        ]
        mock_proxmox_api.nodes.return_value.lxc.return_value.snapshot.get.return_value = mock_snapshots
        
        result = lxc_tools.get_container_snapshots("pve1", "200")
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "backup1" in result[0].text
        assert "backup2" in result[0].text

    def test_create_container_snapshot_success(self, lxc_tools, mock_proxmox_api):
        """Test successful snapshot creation."""
        # Mock snapshot creation
        mock_proxmox_api.nodes.return_value.lxc.return_value.snapshot.post.return_value = "created"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_snapshot_result.return_value = "Snapshot created"
            
            result = lxc_tools.create_container_snapshot("pve1", "200", "backup1", "Test backup")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Snapshot created"

    def test_delete_container_snapshot_success(self, lxc_tools, mock_proxmox_api):
        """Test successful snapshot deletion."""
        # Mock snapshot deletion
        mock_proxmox_api.nodes.return_value.lxc.return_value.snapshot.return_value.delete.return_value = "deleted"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_snapshot_result.return_value = "Snapshot deleted"
            
            result = lxc_tools.delete_container_snapshot("pve1", "200", "backup1")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Snapshot deleted"

    def test_rollback_container_snapshot_success(self, lxc_tools, mock_proxmox_api):
        """Test successful snapshot rollback."""
        # Mock snapshot rollback
        mock_proxmox_api.nodes.return_value.lxc.return_value.snapshot.return_value.rollback.post.return_value = "rolled back"
        
        with patch('src.proxmox_mcp.tools.lxc.ProxmoxTemplates') as mock_templates:
            mock_templates.container_snapshot_result.return_value = "Snapshot rolled back"
            
            result = lxc_tools.rollback_container_snapshot("pve1", "200", "backup1")
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == "Snapshot rolled back"

    def test_error_handling(self, lxc_tools, mock_proxmox_api):
        """Test error handling in LXC tools."""
        # Mock API error
        mock_proxmox_api.nodes.return_value.lxc.get.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError, match="Failed to get containers"):
            lxc_tools.get_containers() 