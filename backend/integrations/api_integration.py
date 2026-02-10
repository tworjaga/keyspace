"""
API Integration
Provides REST API endpoints for remote control of the brute force tool
"""

import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, Callable
import socket

logger = logging.getLogger(__name__)


class APIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the API"""

    def __init__(self, *args, api_server=None, **kwargs):
        self.api_server = api_server
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path.split('?')[0]

            if path == '/status':
                self._send_json_response(self.api_server.get_status())
            elif path == '/attacks':
                self._send_json_response(self.api_server.get_attacks())
            elif path == '/integrations':
                self._send_json_response(self.api_server.get_integrations_status())
            elif path == '/wordlists':
                self._send_json_response(self.api_server.get_wordlists())
            else:
                self._send_error(404, "Endpoint not found")

        except Exception as e:
            logger.error(f"GET request failed: {e}")
            self._send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests"""
        try:
            path = self.path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                data = {}

            if path == '/attack/start':
                result = self.api_server.start_attack(data)
                self._send_json_response(result)
            elif path == '/attack/stop':
                result = self.api_server.stop_attack(data)
                self._send_json_response(result)
            elif path == '/wordlist/upload':
                result = self.api_server.upload_wordlist(data)
                self._send_json_response(result)
            elif path == '/wordlist/download':
                result = self.api_server.download_wordlist(data)
                self._send_json_response(result)
            elif path == '/export':
                result = self.api_server.export_results(data)
                self._send_json_response(result)
            else:
                self._send_error(404, "Endpoint not found")

        except Exception as e:
            logger.error(f"POST request failed: {e}")
            self._send_error(500, str(e))

    def do_PUT(self):
        """Handle PUT requests"""
        try:
            path = self.path
            content_length = int(self.headers.get('Content-Length', 0))
            put_data = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(put_data) if put_data else {}
            except json.JSONDecodeError:
                data = {}

            if path == '/config':
                result = self.api_server.update_config(data)
                self._send_json_response(result)
            else:
                self._send_error(404, "Endpoint not found")

        except Exception as e:
            logger.error(f"PUT request failed: {e}")
            self._send_error(500, str(e))

    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            path = self.path

            if path.startswith('/attack/'):
                attack_id = path.split('/')[-1]
                result = self.api_server.delete_attack(attack_id)
                self._send_json_response(result)
            else:
                self._send_error(404, "Endpoint not found")

        except Exception as e:
            logger.error(f"DELETE request failed: {e}")
            self._send_error(500, str(e))

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        json_response = json.dumps(data, default=str, indent=2)
        self.wfile.write(json_response.encode('utf-8'))

    def _send_error(self, code: int, message: str):
        """Send error response"""
        self._send_json_response({"error": message, "code": code}, code)

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.debug(format % args)


class APIServer:
    """API server for remote control"""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

        # Request handlers
        self.attack_handlers = {}
        self.current_attacks = {}

    def start(self):
        """Start the API server"""
        if self.running:
            return True

        try:
            # Create server with custom handler
            def handler_class(*args, **kwargs):
                return APIRequestHandler(*args, api_server=self, **kwargs)

            self.server = HTTPServer((self.host, self.port), handler_class)
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()

            self.running = True
            logger.info(f"API server started on http://{self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False

    def stop(self):
        """Stop the API server"""
        if not self.running:
            return True

        try:
            self.running = False
            if self.server:
                self.server.shutdown()
                self.server.server_close()

            if self.thread:
                self.thread.join(timeout=5)

            logger.info("API server stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop API server: {e}")
            return False

    def _run_server(self):
        """Run the server loop"""
        try:
            while self.running:
                self.server.serve_forever()
        except Exception as e:
            if self.running:  # Only log if not intentionally stopped
                logger.error(f"API server error: {e}")

    def register_attack_handler(self, handler_name: str, handler: Callable):
        """Register an attack handler"""
        self.attack_handlers[handler_name] = handler

    def get_status(self) -> Dict[str, Any]:
        """Get API server status"""
        return {
            "status": "running" if self.running else "stopped",
            "host": self.host,
            "port": self.port,
            "uptime": time.time() - getattr(self, 'start_time', time.time()),
            "active_attacks": len(self.current_attacks)
        }

    def get_attacks(self) -> Dict[str, Any]:
        """Get current attacks"""
        return {
            "attacks": list(self.current_attacks.values()),
            "count": len(self.current_attacks)
        }

    def get_integrations_status(self) -> Dict[str, Any]:
        """Get integrations status (to be overridden by main app)"""
        return {"integrations": "not_available"}

    def get_wordlists(self) -> Dict[str, Any]:
        """Get available wordlists (to be overridden by main app)"""
        return {"wordlists": []}

    def start_attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new attack"""
        try:
            attack_type = data.get('attack_type')
            target = data.get('target')
            config = data.get('config', {})

            if not attack_type or not target:
                return {"error": "Missing attack_type or target"}

            # Generate attack ID
            attack_id = f"attack_{int(time.time())}_{len(self.current_attacks)}"

            # Store attack info
            self.current_attacks[attack_id] = {
                "id": attack_id,
                "type": attack_type,
                "target": target,
                "status": "starting",
                "start_time": time.time(),
                "config": config
            }

            # Here you would actually start the attack using the registered handlers
            # For now, just simulate
            logger.info(f"API: Starting attack {attack_id} ({attack_type}) on {target}")

            return {
                "success": True,
                "attack_id": attack_id,
                "message": f"Attack {attack_id} started"
            }

        except Exception as e:
            logger.error(f"Failed to start attack via API: {e}")
            return {"error": str(e)}

    def stop_attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop an attack"""
        try:
            attack_id = data.get('attack_id')
            if not attack_id or attack_id not in self.current_attacks:
                return {"error": "Invalid or unknown attack ID"}

            # Update status
            self.current_attacks[attack_id]["status"] = "stopping"
            logger.info(f"API: Stopping attack {attack_id}")

            # Here you would actually stop the attack
            # For now, just mark as stopped
            self.current_attacks[attack_id]["status"] = "stopped"
            self.current_attacks[attack_id]["end_time"] = time.time()

            return {"success": True, "message": f"Attack {attack_id} stopped"}

        except Exception as e:
            logger.error(f"Failed to stop attack via API: {e}")
            return {"error": str(e)}

    def delete_attack(self, attack_id: str) -> Dict[str, Any]:
        """Delete attack record"""
        if attack_id in self.current_attacks:
            del self.current_attacks[attack_id]
            return {"success": True, "message": f"Attack {attack_id} deleted"}
        else:
            return {"error": "Attack not found"}

    def upload_wordlist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload wordlist (placeholder)"""
        return {"error": "Wordlist upload not implemented"}

    def download_wordlist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Download wordlist (placeholder)"""
        return {"error": "Wordlist download not implemented"}

    def export_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export results (placeholder)"""
        return {"error": "Results export not implemented"}

    def update_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration (placeholder)"""
        return {"error": "Configuration update not implemented"}


class APIIntegration:
    """Main API integration class"""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.server = APIServer(host, port)
        self.start_time = time.time()

    def start(self) -> bool:
        """Start the API server"""
        self.start_time = time.time()
        return self.server.start()

    def stop(self) -> bool:
        """Stop the API server"""
        return self.server.stop()

    def is_running(self) -> bool:
        """Check if API server is running"""
        return self.server.running

    def get_status(self) -> Dict[str, Any]:
        """Get API server status"""
        return self.server.get_status()

    def register_attack_handler(self, handler_name: str, handler: Callable):
        """Register an attack handler with the API server"""
        self.server.register_attack_handler(handler_name, handler)

    # Delegate other methods to server
    def __getattr__(self, name):
        if hasattr(self.server, name):
            return getattr(self.server, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
