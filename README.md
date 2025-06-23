# Pipeline - Advanced Terminal Multiplexer

Pipeline is a powerful terminal management system designed specifically for Mosaic that enables seamless inter-terminal communication, remote command execution, and task coordination across multiple terminal sessions.

## Features

- **Named Terminal Management**: Create and manage multiple terminal instances with custom names
- **Inter-Terminal Communication**: Send messages between terminals without leaving your current session
- **Remote Command Execution**: Execute commands in any terminal from any other terminal
- **Task Completion Callbacks**: Receive notifications when tasks complete in other terminals
- **Program Integration**: Launch and manage external programs from any terminal
- **Custom Shortcuts**: Define user-specific shortcuts for quick terminal navigation
- **Persistent Configuration**: Save terminal names, shortcuts, and settings
- **Multi-threaded Architecture**: Handle multiple concurrent terminal sessions efficiently

## Prerequisites

- Python 3.7 or higher
- Mosaic terminal multiplexer
- Linux/macOS (Unix-like system)
- Network access for local socket communication

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/pipeline.git
cd pipeline
```

### Make Pipeline Executable

```bash
chmod +x pipeline.py
```

### Optional: Add to PATH

```bash
# Add to your ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/pipeline"

# Or create a symlink
sudo ln -s /path/to/pipeline/pipeline.py /usr/local/bin/pipeline
```

## Quick Start

1. **Start the Pipeline Server**
   ```bash
   python3 pipeline.py server
   ```

2. **Create Named Terminals**
   ```bash
   # In separate terminal windows/tabs
   python3 pipeline.py development
   python3 pipeline.py testing
   python3 pipeline.py monitoring
   ```

3. **Use Pipeline Commands**
   ```bash
   # Send a message
   psend testing "Ready to deploy"
   
   # Execute a command
   pexec development "git status"
   
   # Execute with callback
   pexec testing "npm test" --callback
   ```

## Architecture

Pipeline uses a client-server architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Terminal A    │    │ Pipeline Server │    │   Terminal B    │
│   (Client)      │◄──►│   (Manager)     │◄──►│   (Client)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Configuration │
                    │   & Shortcuts   │
                    └─────────────────┘
```

## Commands Reference

### Server Commands

| Command | Description |
|---------|-------------|
| `pipeline server` | Start the Pipeline server |
| `pipeline server --port N` | Start server on specific port |

### Terminal Creation

| Command | Description |
|---------|-------------|
| `pipeline {NAME}` | Create a new named terminal |
| `pipeline {NAME} --port N` | Connect to server on specific port |

### In-Terminal Commands

| Command | Description | Example |
|---------|-------------|---------|
| `psend TARGET MESSAGE` | Send message to terminal | `psend dev "Build complete"` |
| `pexec TARGET COMMAND` | Execute command in terminal | `pexec test "python test.py"` |
| `pexec TARGET COMMAND --callback` | Execute with completion notification | `pexec build "make" --callback` |
| `plist` | List all active terminals | `plist` |

## Configuration

Pipeline stores configuration in `~/.pipeline/`:

```
~/.pipeline/
├── config.json      # Terminal registry and server settings
└── shortcuts.json   # Custom keyboard shortcuts
```

### Configuration Files

**config.json**
```json
{
  "terminals": {
    "development": {
      "pid": 12345,
      "cwd": "/home/user/project"
    }
  },
  "port": 9999
}
```

**shortcuts.json**
```json
{
  "ctrl+1": "development",
  "ctrl+2": "testing",
  "ctrl+3": "monitoring"
}
```

## Use Cases

### Development Workflow

```bash
# Terminal 1: Development
pipeline dev
git checkout feature-branch
psend test "Starting development on feature-branch"

# Terminal 2: Testing
pipeline test
pexec dev "git status" --callback
# Wait for callback, then run tests

# Terminal 3: Monitoring
pipeline monitor
pexec dev "docker-compose up" 
```

### Deployment Pipeline

```bash
# Build terminal
pipeline build
pexec test "npm test" --callback
# After tests pass, trigger build

# Test terminal  
pipeline test
psend build "Tests passed, ready for build"

# Deploy terminal
pipeline deploy
pexec build "docker build -t app:latest ." --callback
# After build completes, deploy
```

### System Administration

```bash
# Monitoring terminal
pipeline monitor
htop

# Services terminal
pipeline services
psend monitor "Restarting nginx"
pexec monitor "sudo systemctl restart nginx" --callback

# Logs terminal
pipeline logs
tail -f /var/log/nginx/access.log
```

## Advanced Features

### Task Completion Callbacks

Execute commands in other terminals and receive results:

```bash
# From terminal A
pexec terminal-b "long-running-command" --callback

# Terminal A will receive:
# [Pipeline Callback from terminal-b]:
# Command: long-running-command
# Return code: 0
# Output: command output here
```

### Message Broadcasting

Send status updates to multiple terminals:

```bash
# Send to specific terminal
psend build "Deployment started"

# Check active terminals first
plist
# Output: Active terminals: dev, test, build, deploy
```

### Program Integration

Launch external programs and coordinate between terminals:

```bash
# Start a development server
pexec dev "npm start"

# Monitor the server
pexec monitor "curl -I http://localhost:3000" --callback

# Run tests against the server
pexec test "npm run integration-tests" --callback
```

## Troubleshooting

### Common Issues

**Server Connection Failed**
```bash
# Check if server is running
ps aux | grep pipeline

# Check port availability
netstat -an | grep 9999

# Restart server
python3 pipeline.py server --port 9999
```

**Terminal Not Responding**
```bash
# List active terminals
plist

# Restart problematic terminal
# Kill the terminal and recreate
pipeline terminal-name
```

**Permission Errors**
```bash
# Ensure script is executable
chmod +x pipeline.py

# Check configuration directory
ls -la ~/.pipeline/
```

### Debug Mode

Enable debug output by setting environment variable:

```bash
export PIPELINE_DEBUG=1
python3 pipeline.py server
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/pipeline.git
cd pipeline

# Install development dependencies
pip3 install -r requirements-dev.txt

# Run tests
python3 -m pytest tests/

# Run linting
flake8 pipeline.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Basic terminal management
- Inter-terminal communication
- Remote command execution
- Task completion callbacks
- Mosaic integration

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pipeline/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/pipeline/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pipeline/discussions)

## Acknowledgments

- Mosaic terminal multiplexer team
- Python socket programming community
- Contributors and testers
