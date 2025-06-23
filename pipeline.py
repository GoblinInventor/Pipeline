#!/usr/bin/env python3
"""
Pipeline - Advanced Terminal Multiplexer for Mosaic
A powerful terminal management system with inter-terminal communication,
remote command execution, and customizable shortcuts.
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import queue
import socket
import select
from pathlib import Path
from typing import Dict, List, Optional, Callable
import argparse

class PipelineConfig:
    """Configuration management for Pipeline"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.pipeline'
        self.config_file = self.config_dir / 'config.json'
        self.shortcuts_file = self.config_dir / 'shortcuts.json'
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
        
    def load_config(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {'terminals': {}, 'port': 9999}
    
    def save_config(self, config: dict):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_shortcuts(self) -> dict:
        if self.shortcuts_file.exists():
            with open(self.shortcuts_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_shortcuts(self, shortcuts: dict):
        with open(self.shortcuts_file, 'w') as f:
            json.dump(shortcuts, f, indent=2)

class TerminalManager:
    """Manages terminal instances and their communication"""
    
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.terminals = {}
        self.message_queue = queue.Queue()
        self.completion_callbacks = {}
        self.server_socket = None
        self.running = True
        self.config = PipelineConfig()
        
    def start_server(self):
        """Start the communication server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(10)
            print(f"Pipeline server started on port {self.port}")
            
            # Start server thread
            server_thread = threading.Thread(target=self._handle_connections)
            server_thread.daemon = True
            server_thread.start()
            
        except OSError as e:
            print(f"Error starting server: {e}")
            return False
        return True
    
    def _handle_connections(self):
        """Handle incoming connections"""
        while self.running:
            try:
                ready, _, _ = select.select([self.server_socket], [], [], 1.0)
                if ready:
                    client_socket, addr = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
            except:
                break
    
    def _handle_client(self, client_socket):
        """Handle client messages"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                message = json.loads(data.decode())
                self._process_message(message, client_socket)
        except:
            pass
        finally:
            client_socket.close()
    
    def _process_message(self, message: dict, client_socket):
        """Process incoming messages"""
        msg_type = message.get('type')
        
        if msg_type == 'register':
            self._register_terminal(message, client_socket)
        elif msg_type == 'send':
            self._send_to_terminal(message)
        elif msg_type == 'execute':
            self._execute_command(message)
        elif msg_type == 'complete':
            self._handle_completion(message)
        elif msg_type == 'list':
            self._list_terminals(client_socket)
    
    def _register_terminal(self, message: dict, client_socket):
        """Register a new terminal"""
        term_name = message.get('name')
        if term_name:
            self.terminals[term_name] = {
                'socket': client_socket,
                'pid': message.get('pid'),
                'cwd': message.get('cwd', os.getcwd())
            }
            response = {'status': 'registered', 'name': term_name}
            client_socket.send(json.dumps(response).encode())
    
    def _send_to_terminal(self, message: dict):
        """Send message to specific terminal"""
        target = message.get('target')
        content = message.get('content')
        
        if target in self.terminals:
            target_socket = self.terminals[target]['socket']
            msg = {'type': 'message', 'content': content}
            try:
                target_socket.send(json.dumps(msg).encode())
            except:
                # Terminal disconnected
                del self.terminals[target]
    
    def _execute_command(self, message: dict):
        """Execute command in target terminal"""
        target = message.get('target')
        command = message.get('command')
        callback_terminal = message.get('callback')
        
        if target in self.terminals:
            target_socket = self.terminals[target]['socket']
            msg = {
                'type': 'execute',
                'command': command,
                'callback': callback_terminal
            }
            
            if callback_terminal:
                self.completion_callbacks[f"{target}:{command}"] = callback_terminal
            
            try:
                target_socket.send(json.dumps(msg).encode())
            except:
                del self.terminals[target]
    
    def _handle_completion(self, message: dict):
        """Handle task completion notifications"""
        terminal = message.get('terminal')
        command = message.get('command')
        result = message.get('result')
        
        callback_key = f"{terminal}:{command}"
        if callback_key in self.completion_callbacks:
            callback_terminal = self.completion_callbacks[callback_key]
            if callback_terminal in self.terminals:
                callback_socket = self.terminals[callback_terminal]['socket']
                msg = {
                    'type': 'callback',
                    'from_terminal': terminal,
                    'command': command,
                    'result': result
                }
                try:
                    callback_socket.send(json.dumps(msg).encode())
                except:
                    pass
            del self.completion_callbacks[callback_key]
    
    def _list_terminals(self, client_socket):
        """List active terminals"""
        terminal_list = list(self.terminals.keys())
        response = {'type': 'list', 'terminals': terminal_list}
        client_socket.send(json.dumps(response).encode())

class PipelineTerminal:
    """Individual terminal instance with Pipeline integration"""
    
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.socket = None
        self.running = True
        self.config = PipelineConfig()
        
    def connect(self):
        """Connect to Pipeline server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', self.port))
            
            # Register this terminal
            register_msg = {
                'type': 'register',
                'name': self.name,
                'pid': os.getpid(),
                'cwd': os.getcwd()
            }
            self.socket.send(json.dumps(register_msg).encode())
            
            # Start message listener
            listener_thread = threading.Thread(target=self._listen_for_messages)
            listener_thread.daemon = True
            listener_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to Pipeline server: {e}")
            return False
    
    def _listen_for_messages(self):
        """Listen for incoming messages"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode())
                self._handle_message(message)
            except:
                break
    
    def _handle_message(self, message: dict):
        """Handle incoming messages"""
        msg_type = message.get('type')
        
        if msg_type == 'message':
            print(f"\n[Pipeline Message]: {message.get('content')}")
        elif msg_type == 'execute':
            self._execute_received_command(message)
        elif msg_type == 'callback':
            self._handle_callback(message)
    
    def _execute_received_command(self, message: dict):
        """Execute command received from another terminal"""
        command = message.get('command')
        callback = message.get('callback')
        
        print(f"\n[Pipeline Execute]: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            print(output)
            
            # Send completion notification if callback requested
            if callback:
                completion_msg = {
                    'type': 'complete',
                    'terminal': self.name,
                    'command': command,
                    'result': {
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                }
                self.socket.send(json.dumps(completion_msg).encode())
                
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def _handle_callback(self, message: dict):
        """Handle completion callbacks"""
        from_terminal = message.get('from_terminal')
        command = message.get('command')
        result = message.get('result')
        
        print(f"\n[Pipeline Callback from {from_terminal}]:")
        print(f"Command: {command}")
        print(f"Return code: {result.get('returncode')}")
        if result.get('stdout'):
            print(f"Output: {result.get('stdout')}")
        if result.get('stderr'):
            print(f"Error: {result.get('stderr')}")
    
    def send_to_terminal(self, target: str, content: str):
        """Send message to another terminal"""
        if self.socket:
            msg = {
                'type': 'send',
                'target': target,
                'content': content
            }
            self.socket.send(json.dumps(msg).encode())
    
    def execute_in_terminal(self, target: str, command: str, callback: bool = False):
        """Execute command in another terminal"""
        if self.socket:
            msg = {
                'type': 'execute',
                'target': target,
                'command': command,
                'callback': self.name if callback else None
            }
            self.socket.send(json.dumps(msg).encode())
    
    def list_terminals(self):
        """List all active terminals"""
        if self.socket:
            msg = {'type': 'list'}
            self.socket.send(json.dumps(msg).encode())

def start_pipeline_server(port: int = 9999):
    """Start the Pipeline server"""
    manager = TerminalManager("pipeline-server", port)
    
    if not manager.start_server():
        return False
    
    print("Pipeline server is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Pipeline server...")
        manager.running = False
        if manager.server_socket:
            manager.server_socket.close()
    
    return True

def create_mosaic_terminal(name: str, port: int = 9999):
    """Create a new Mosaic terminal window with Pipeline integration"""
    script_content = f'''#!/bin/bash
export PIPELINE_NAME="{name}"
export PIPELINE_PORT="{port}"

# Start Pipeline terminal integration
python3 -c "
import sys
sys.path.append('{os.path.dirname(os.path.abspath(__file__))}')
from pipeline import PipelineTerminal
import os
import subprocess
import threading

terminal = PipelineTerminal('{name}', {port})
if terminal.connect():
    print(f'Pipeline terminal \"{name}\" connected')
    
    # Add Pipeline commands to bash
    pipeline_commands = """
    
    # Pipeline command functions
    psend() {{
        python3 -c \"
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', {port}))
msg = {{'type': 'send', 'target': '$1', 'content': '$2'}}
s.send(json.dumps(msg).encode())
s.close()
\"
    }}
    
    pexec() {{
        callback_flag=\"\"
        if [[ \"$3\" == \"--callback\" ]]; then
            callback_flag=\"'{name}'\"
        fi
        python3 -c \"
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', {port}))
msg = {{'type': 'execute', 'target': '$1', 'command': '$2', 'callback': $callback_flag}}
s.send(json.dumps(msg).encode())
s.close()
\"
    }}
    
    plist() {{
        python3 -c \"
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', {port}))
msg = {{'type': 'list'}}
s.send(json.dumps(msg).encode())
response = s.recv(4096)
data = json.loads(response.decode())
print('Active terminals:', ', '.join(data.get('terminals', [])))
s.close()
\"
    }}
    """
    
    echo \"$pipeline_commands\" >> ~/.bashrc
    source ~/.bashrc
else:
    echo 'Failed to connect to Pipeline server'
fi
"

# Start bash with Pipeline integration
exec bash --rcfile <(echo '. ~/.bashrc')
'''

    script_path = f"/tmp/pipeline_{name}.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    
    # Launch Mosaic terminal
    subprocess.Popen([
        'mosaic', 
        '--terminal-title', f'Pipeline: {name}',
        '--exec', script_path
    ])

def main():
    parser = argparse.ArgumentParser(description='Pipeline - Advanced Terminal Multiplexer')
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('name', nargs='?', help='Terminal name')
    parser.add_argument('--port', type=int, default=9999, help='Server port')
    parser.add_argument('--server', action='store_true', help='Start Pipeline server')
    
    args = parser.parse_args()
    
    if args.server or args.command == 'server':
        start_pipeline_server(args.port)
    elif args.name:
        create_mosaic_terminal(args.name, args.port)
    else:
        print("Usage:")
        print("  pipeline server              # Start Pipeline server")
        print("  pipeline {NAME}              # Create terminal with name")
        print("  pipeline --server --port N   # Start server on specific port")
        print()
        print("Terminal Commands (once connected):")
        print("  psend TARGET MESSAGE         # Send message to terminal")
        print("  pexec TARGET COMMAND         # Execute command in terminal")
        print("  pexec TARGET COMMAND --callback  # Execute with completion callback")
        print("  plist                        # List active terminals")

if __name__ == '__main__':
    main()
