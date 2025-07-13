# 🚀 Proxmox Manager - Proxmox MCP Server

> **Fork Notice:**
> 
> This project is a **fork** of the original [canvrno/ProxmoxMCP](https://github.com/canvrno/ProxmoxMCP) repository. It adds comprehensive LXC container management tools and other enhancements. All credit for the original architecture and VM/node/storage/cluster features goes to the upstream authors.

![ProxmoxMCP](https://github.com/user-attachments/assets/e32ab79f-be8a-420c-ab2d-475612150534)

A Python-based Model Context Protocol (MCP) server for interacting with Proxmox hypervisors, providing a clean interface for managing nodes, VMs, and containers.

## 🏗️ Built With


- [Proxmoxer](https://github.com/proxmoxer/proxmoxer) - Python wrapper for Proxmox API
- [MCP SDK](https://github.com/modelcontextprotocol/sdk) - Model Context Protocol SDK
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type annotations

## ✨ Features


- 🛠️ Built with the official MCP SDK
- 🔒 Secure token-based authentication with Proxmox
- 🖥️ Tools for managing nodes and VMs
- 📦 **Comprehensive LXC container management** (NEW!)
  - Create, start, stop, shutdown, reboot, suspend, resume containers
  - Get and update container configuration
  - Execute commands inside containers
  - Clone and destroy containers
  - Manage container snapshots (create, delete, rollback)
- 💻 VM console command execution
- 📝 Configurable logging system
- ✅ Type-safe implementation with Pydantic
- 🎨 Rich output formatting with customizable themes



https://github.com/user-attachments/assets/1b5f42f7-85d5-4918-aca4-d38413b0e82b



## 📦 Installation

### Prerequisites
- UV package manager (recommended)
- Python 3.10 or higher
- Git
- Access to a Proxmox server with API token credentials

Before starting, ensure you have:
- [ ] Proxmox server hostname or IP
- [ ] Proxmox API token (see [API Token Setup](#proxmox-api-token-setup))
- [ ] UV installed (`pip install uv`)

### Option 1: Quick Install (Recommended)

1. Clone and set up environment:
   ```bash
   # Clone repository
   cd ~/Documents/Cline/MCP  # For Cline users
   # OR
   cd your/preferred/directory  # For manual installation
   
   git clone https://github.com/canvrno/ProxmoxMCP.git
   cd ProxmoxMCP

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # OR
   .\.venv\Scripts\Activate.ps1  # Windows
   ```

2. Install dependencies:
   ```bash
   # Install with development dependencies
   uv pip install -e ".[dev]"
   ```

3. Create configuration:
   ```bash
   # Create config directory and copy template
   mkdir -p proxmox-config
   cp config/config.example.json proxmox-config/config.json
   ```

4. Edit `proxmox-config/config.json`:
   ```json
   {
       "proxmox": {
           "host": "PROXMOX_HOST",        # Required: Your Proxmox server address
           "port": 8006,                  # Optional: Default is 8006
           "verify_ssl": false,           # Optional: Set false for self-signed certs
           "service": "PVE"               # Optional: Default is PVE
       },
       "auth": {
           "user": "USER@pve",            # Required: Your Proxmox username
           "token_name": "TOKEN_NAME",    # Required: API token ID
           "token_value": "TOKEN_VALUE"   # Required: API token value
       },
       "logging": {
           "level": "INFO",               # Optional: DEBUG for more detail
           "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
           "file": "proxmox_mcp.log"      # Optional: Log to file
       }
   }
   ```

### Verifying Installation

1. Check Python environment:
   ```bash
   python -c "import proxmox_mcp; print('Installation OK')"
   ```

2. Run the tests:
   ```bash
   pytest
   ```

3. Verify configuration:
   ```bash
   # Linux/macOS
   PROXMOX_MCP_CONFIG="proxmox-config/config.json" python -m proxmox_mcp.server

   # Windows (PowerShell)
   $env:PROXMOX_MCP_CONFIG="proxmox-config\config.json"; python -m proxmox_mcp.server
   ```

   You should see either:
   - A successful connection to your Proxmox server
   - Or a connection error (if Proxmox details are incorrect)

## ⚙️ Configuration

### Proxmox API Token Setup
1. Log into your Proxmox web interface
2. Navigate to Datacenter -> Permissions -> API Tokens
3. Create a new API token:
   - Select a user (e.g., root@pam)
   - Enter a token ID (e.g., "mcp-token")
   - Uncheck "Privilege Separation" if you want full access
   - Save and copy both the token ID and secret


## 🚀 Running the Server

### Development Mode
For testing and development:
```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/macOS
# OR
.\.venv\Scripts\Activate.ps1  # Windows

# Run the server
python -m proxmox_mcp.server
```





# 🔧 Available Tools

The server provides the following MCP tools for interacting with Proxmox:

## Node & Cluster Tools
- `get_nodes`: List all nodes in the cluster
- `get_node_status`: Get detailed status of a node
- `get_cluster_status`: Get overall cluster health and configuration

## VM Tools
- `get_vms`: List all VMs
- `create_vm`: Create a new VM
- `start_vm`, `stop_vm`, `shutdown_vm`, `reboot_vm`: VM lifecycle
- `get_vm_config`, `update_vm_config`: VM configuration
- `execute_vm_command`: Run commands in a VM (QEMU Guest Agent)

## **LXC Container Tools (NEW)**
- `get_containers`: List all LXC containers
- `create_container`: Create a new LXC container from a template
- `start_container`, `stop_container`, `shutdown_container`, `reboot_container`, `suspend_container`, `resume_container`: Full container lifecycle
- `get_container_config`, `update_container_config`: Get/update container configuration
- `execute_container_command`: Run commands inside a container
- `clone_container`: Clone an existing container
- `destroy_container`: Destroy a container
- `get_container_snapshots`: List container snapshots
- `create_container_snapshot`: Create a snapshot
- `delete_container_snapshot`: Delete a snapshot
- `rollback_container_snapshot`: Rollback to a snapshot

## Storage Tools
- `get_storage`: List available storage pools

---

## 👨‍💻 Development

After activating your virtual environment:

- Run tests: `pytest`
- Format code: `black .`
- Type checking: `mypy .`
- Lint: `ruff .`

## 📁 Project Structure

```
proxmox-mcp/
├── src/
│   └── proxmox_mcp/
│       ├── server.py          # Main MCP server implementation
│       ├── config/            # Configuration handling
│       ├── core/              # Core functionality
│       ├── formatting/        # Output formatting and themes
│       ├── tools/             # Tool implementations
│       │   └── console/       # VM console operations
│       └── utils/             # Utilities (auth, logging)
├── tests/                     # Test suite
├── proxmox-config/
│   └── config.example.json    # Configuration template
├── pyproject.toml            # Project metadata and dependencies
└── LICENSE                   # MIT License
```

## 📄 License

MIT License
