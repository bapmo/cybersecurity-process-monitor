#!/usr/bin/env python3
"""
Cybersecurity Process Monitor - Web Dashboard (Fixed)
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import psutil
import platform
import threading
import time
from datetime import datetime
import json
import subprocess
import os
import sys
import socket  # Add this import

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cybersecurity-dashboard-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
monitoring_active = True
connected_clients = 0

class SystemMonitor:
    @staticmethod
    def get_processes():
        """Get all running processes with detailed info"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                            'status', 'username', 'cmdline', 'create_time', 
                                            'num_threads']):
                try:
                    # Get process info
                    pinfo = proc.info
                    if pinfo['name'] and pinfo['pid']:
                        # Get CPU percentage (need to call twice for accurate reading)
                        try:
                            cpu_percent = proc.cpu_percent(interval=0.1)
                        except:
                            cpu_percent = 0
                            
                        memory_percent = pinfo['memory_percent'] or 0
                        
                        # Get username
                        try:
                            username = proc.username()
                        except:
                            username = 'N/A'
                        
                        # Get command line
                        try:
                            cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A'
                        except:
                            cmdline = 'N/A'
                        
                        # Get create time
                        try:
                            create_time = datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')
                        except:
                            create_time = 'N/A'
                        
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'][:60],
                            'cpu_percent': round(cpu_percent, 1),
                            'memory_percent': round(memory_percent, 1),
                            'status': pinfo['status'] or 'running',
                            'username': username[:40],
                            'command': cmdline[:100],
                            'threads': pinfo['num_threads'] or 0,
                            'created': create_time
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes
            
        except Exception as e:
            print(f"Error in get_processes: {e}")
            return []
    
    @staticmethod
    def get_system_stats():
        """Get overall system statistics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            net_io = psutil.net_io_counters()
            
            # System info
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                'cpu': {
                    'total': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                },
                'system': {
                    'platform': platform.system(),
                    'release': platform.release(),
                    'processor': platform.processor(),
                    'hostname': platform.node(),
                    'uptime': uptime
                }
            }
        except Exception as e:
            print(f"Error in get_system_stats: {e}")
            return {
                'cpu': {'total': 0, 'count': 0},
                'memory': {'percent': 0, 'used': 0, 'total': 0},
                'disk': {'percent': 0, 'used': 0, 'total': 0},
                'system': {'platform': 'Unknown', 'hostname': 'Unknown', 'uptime': 0}
            }
    
    @staticmethod
    def kill_process(pid):
        """Terminate a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except psutil.NoSuchProcess:
            return {'success': False, 'message': 'Process not found'}
        except psutil.AccessDenied:
            return {'success': False, 'message': 'Access denied. Run as Administrator'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def run_powershell_command(command):
        """Execute PowerShell command"""
        try:
            result = subprocess.run(['powershell', '-Command', command], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'success': True,
                'output': result.stdout[:2000] if result.stdout else 'No output',
                'error': result.stderr[:500] if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

monitor = SystemMonitor()

# Background thread for real-time updates
def background_monitor():
    """Background thread to push real-time updates"""
    global monitoring_active, connected_clients
    
    print("Background monitor thread started")
    
    while monitoring_active:
        try:
            if connected_clients > 0:
                # Get current data
                processes = monitor.get_processes()
                stats = monitor.get_system_stats()
                
                # Debug output
                if processes:
                    print(f"Sending {len(processes)} processes to {connected_clients} clients")
                
                # Emit to all connected clients
                socketio.emit('process_update', {
                    'processes': processes[:200],  # Limit to top 200
                    'stats': stats,
                    'timestamp': datetime.now().isoformat(),
                    'count': len(processes)
                })
            else:
                # Only print occasionally to avoid spam
                if int(time.time()) % 30 == 0:  # Print every 30 seconds
                    print("No connected clients, waiting for connection...")
                
            time.sleep(3)  # Update every 3 seconds
            
        except Exception as e:
            print(f"Monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

# Start background thread
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/processes')
def get_processes():
    """API endpoint to get processes"""
    try:
        processes = monitor.get_processes()
        return jsonify({'success': True, 'processes': processes[:200], 'count': len(processes)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def get_stats():
    """API endpoint to get system stats"""
    try:
        stats = monitor.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    """API endpoint to kill a process"""
    result = monitor.kill_process(pid)
    return jsonify(result)

@app.route('/api/powershell', methods=['POST'])
def powershell_command():
    """API endpoint to run PowerShell commands"""
    data = request.json
    command = data.get('command', '')
    if command:
        result = monitor.run_powershell_command(command)
        return jsonify(result)
    return jsonify({'success': False, 'error': 'No command provided'})

@app.route('/api/filter')
def filter_processes():
    """Filter processes by name"""
    name_filter = request.args.get('name', '').lower()
    try:
        processes = monitor.get_processes()
        if name_filter:
            processes = [p for p in processes if name_filter in p['name'].lower()]
        return jsonify({'success': True, 'processes': processes[:200], 'count': len(processes)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global connected_clients
    connected_clients += 1
    print(f'✅ Client connected. Total clients: {connected_clients}')
    emit('connected', {'message': 'Connected to monitor', 'clients': connected_clients})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global connected_clients
    connected_clients -= 1
    print(f'❌ Client disconnected. Total clients: {connected_clients}')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔒 Cybersecurity Process Monitor - Web Dashboard")
    print("="*60)
    
    # Get local IP address
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"📍 Local URL: http://localhost:5000")
        print(f"📍 Network URL: http://{local_ip}:5000")
    except Exception as e:
        print(f"📍 Local URL: http://localhost:5000")
        print(f"⚠️  Could not determine network IP: {e}")
    
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        monitoring_active = False
        sys.exit(0)