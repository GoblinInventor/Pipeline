# Pipeline Quick Start Guide

Get up and running with Pipeline in under 5 minutes! This guide will walk you through installation, basic setup, and your first inter-terminal communication session.

## 🚀 Installation (2 minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pipeline.git
cd pipeline

# Make executable
chmod +x pipeline.py

# Optional: Add to PATH for global access
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Verify Installation

```bash
python3 pipeline.py --help
```

You should see the Pipeline help menu.

## 🎯 First Steps (3 minutes)

### Step 1: Start the Pipeline Server

Open your first terminal and start the server:

```bash
python3 pipeline.py server
```

You'll see:
```
Pipeline server started on port 9999
Pipeline server is running. Press Ctrl+C to stop.
```

**Keep this terminal open!** The server needs to run continuously.

### Step 2: Create Your First Named Terminal

Open a **second terminal** and create a terminal named "main":

```bash
python3 pipeline.py main
```

You'll see a new Mosaic terminal window open with the title "Pipeline: main".

### Step 3: Create a Second Named Terminal

Open a **third terminal** and create another terminal named "helper":

```bash
python3 pipeline.py helper
```

Another Mosaic window opens titled "Pipeline: helper".

### Step 4: Test Inter-Terminal Communication

**In the "main" terminal window:**

```bash
# List all active terminals
plist
```

Output:
```
Active terminals: main, helper
```

**Send a message to the "helper" terminal:**

```bash
psend helper "Hello from main terminal!"
```

**Switch to the "helper" terminal window** and you'll see:
```
[Pipeline Message]: Hello from main terminal!
```

🎉 **Congratulations!** You've successfully sent your first inter-terminal message!

## 🔥 Essential Commands (Try These Now!)

### Message Communication

**From any terminal, send messages to others:**

```bash
# Basic message
psend main "Task completed successfully"

# Status update
psend helper "Starting deployment process..."
```

### Remote Command Execution

**Execute commands in other terminals without leaving your current one:**

```bash
# Run a simple command
pexec helper "ls -la"

# Check system status
pexec main "ps aux | grep python"

# Run with completion callback
pexec helper "sleep 5 && echo 'Task done'" --callback
```

### Terminal Management

```bash
# List all active terminals
plist

# Example output: Active terminals: main, helper, build, test
```

## 💡 Real-World Example (Try This!)

Let's simulate a development workflow:

### Terminal 1: "development"
```bash
python3 pipeline.py development
# In the new terminal:
cd ~/my-project
psend testing "Ready to test new feature"
```

### Terminal 2: "testing"  
```bash
python3 pipeline.py testing
# In the new terminal:
pexec development "git status" --callback
# You'll see the git status from the development terminal
```

### Terminal 3: "monitoring"
```bash
python3 pipeline.py monitoring
# In the new terminal:
psend development "Monitoring system is online"
pexec development "echo 'Build started'" --callback
```

## 🛠️ Common Patterns

### Pattern 1: Build and Test Workflow

```bash
# Terminal: build
pexec test "npm test" --callback
# Wait for test results, then:
pexec deploy "docker build -t app:latest ." --callback

# Terminal: test  
psend build "All tests passed ✅"

# Terminal: deploy
psend build "Deployment complete 🚀"
```

### Pattern 2: System Administration

```bash
# Terminal: monitor
pexec services "sudo systemctl status nginx" --callback

# Terminal: services
psend monitor "Nginx status: active (running)"
pexec logs "tail -n 50 /var/log/nginx/error.log" --callback

# Terminal: logs
psend monitor "No critical errors found"
```

### Pattern 3: Development Server Management

```bash
# Terminal: server
psend dev "Starting development server..."
pexec dev "npm start" 

# Terminal: dev
pexec test "curl -I http://localhost:3000" --callback

# Terminal: test
psend server "Server is responding correctly ✅"
```

## 🔧 Troubleshooting

### Server Not Starting?

```bash
# Check if port 9999 is in use
lsof -i :9999

# Use different port
python3 pipeline.py server --port 8888
python3 pipeline.py main --port 8888
```

### Terminal Not Connecting?

```bash
# Verify server is running
ps aux | grep pipeline

# Check for error messages in server terminal
# Restart server if needed
```

### Commands Not Working?

Make sure you're using the commands **inside** the Pipeline terminal windows (the Mosaic windows that opened), not in your original terminal.

## 🎯 Next Steps

### Explore Advanced Features

1. **Set up custom shortcuts** in `~/.pipeline/shortcuts.json`
2. **Create complex workflows** with multiple terminals
3. **Integrate with your development tools** (git, docker, npm, etc.)
4. **Use callbacks** for automated workflow coordination

### Read the Full Documentation

- Check out the complete [README.md](README.md) for detailed features
- Explore configuration options
- Learn about advanced use cases

### Create Your Own Workflow

Think about your daily terminal usage:
- What repetitive tasks do you do?
- Which commands do you run across multiple terminals?
- How could Pipeline streamline your workflow?

## 🚀 You're Ready!

You now know the basics of Pipeline:
- ✅ Start the server
- ✅ Create named terminals  
- ✅ Send messages between terminals
- ✅ Execute remote commands
- ✅ Use completion callbacks

Start building your own multi-terminal workflows and boost your productivity!

---

**Need help?** Check the [README.md](README.md) or open an issue on GitHub.
