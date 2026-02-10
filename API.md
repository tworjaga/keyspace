# API Documentation

Complete API reference for Keyspace developers and integrators.

## REST API

Keyspace provides a REST API for remote control and integration.

### Base URL
```
http://localhost:8080/api/v1
```

### Authentication
All API requests require authentication via API key:
```bash
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### Status
```http
GET /status
```
Returns application status and version.

**Response:**
```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": 3600,
  "attacks_running": 2
}
```

#### Start Attack
```http
POST /attacks/start
```
Start a new password cracking attack.

**Request Body:**
```json
{
  "target": "demo_target",
  "attack_type": "Dictionary Attack (WPA2)",
  "wordlist_path": "/path/to/wordlist.txt",
  "min_length": 8,
  "max_length": 16,
  "charset": "abcdefghijklmnopqrstuvwxyz0123456789"
}
```

**Response:**
```json
{
  "attack_id": "atk_1234567890",
  "status": "started",
  "message": "Attack started successfully"
}
```

#### Stop Attack
```http
POST /attacks/{attack_id}/stop
```
Stop a running attack.

**Response:**
```json
{
  "attack_id": "atk_1234567890",
  "status": "stopped",
  "message": "Attack stopped successfully"
}
```

#### Get Attack Status
```http
GET /attacks/{attack_id}/status
```
Get detailed status of an attack.

**Response:**
```json
{
  "attack_id": "atk_1234567890",
  "status": "running",
  "progress": 45.5,
  "speed": 1250.5,
  "eta": "00:15:30",
  "attempts": 56789,
  "found_password": null
}
```

#### List Attacks
```http
GET /attacks
```
List all attacks (running and completed).

**Response:**
```json
{
  "attacks": [
    {
      "attack_id": "atk_1234567890",
      "target": "demo_target",
      "attack_type": "Dictionary Attack (WPA2)",
      "status": "running",
      "start_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Results
```http
GET /attacks/{attack_id}/results
```
Get results of a completed attack.

**Response:**
```json
{
  "attack_id": "atk_1234567890",
  "found_password": "secret123",
  "attempts": 123456,
  "duration": 3600,
  "speed_avg": 34.3
}
```

## WebSocket API

Real-time updates via WebSocket connection.

### Connection
```
ws://localhost:8080/ws
```

### Events

#### Subscribe to Attack Updates
```json
{
  "action": "subscribe",
  "attack_id": "atk_1234567890"
}
```

#### Progress Update (Server → Client)
```json
{
  "type": "progress",
  "attack_id": "atk_1234567890",
  "data": {
    "progress": 45.5,
    "speed": 1250.5,
    "eta": "00:15:30",
    "attempts": 56789
  }
}
```

#### Attack Completed (Server → Client)
```json
{
  "type": "completed",
  "attack_id": "atk_1234567890",
  "data": {
    "found_password": "secret123",
    "attempts": 123456,
    "duration": 3600
  }
}
```

## Python SDK

### Installation
```bash
pip install keyspace-sdk
```

### Usage

#### Initialize Client
```python
from keyspace import Client

client = Client(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)
```

#### Start Attack
```python
attack = client.attacks.start(
    target="demo_target",
    attack_type="Dictionary Attack (WPA2)",
    wordlist_path="/path/to/wordlist.txt"
)
print(f"Attack ID: {attack.id}")
```

#### Monitor Progress
```python
import time

while True:
    status = client.attacks.get_status(attack.id)
    print(f"Progress: {status.progress}%")
    print(f"Speed: {status.speed} attempts/sec")
    
    if status.status in ["completed", "stopped"]:
        break
    
    time.sleep(1)
```

#### Get Results
```python
results = client.attacks.get_results(attack.id)
if results.found_password:
    print(f"Password found: {results.found_password}")
else:
    print("Password not found")
```

## Integration Examples

### Hashcat Integration
```python
from keyspace.integrations import HashcatIntegration

hashcat = HashcatIntegration(
    hashcat_path="/usr/bin/hashcat",
    hash_type=2500  # WPA2
)

result = hashcat.run(
    hash_file="hashes.txt",
    wordlist="wordlist.txt"
)
```

### John the Ripper Integration
```python
from keyspace.integrations import JohnIntegration

john = JohnIntegration(
    john_path="/usr/bin/john"
)

result = john.run(
    hash_file="hashes.txt",
    wordlist="wordlist.txt",
    format="wpapsk"
)
```

## Data Models

### Attack Configuration
```python
class AttackConfig:
    target: str
    attack_type: str
    wordlist_path: Optional[str]
    min_length: int
    max_length: int
    charset: str
    mutation_rules: List[str]
    mask_pattern: Optional[str]
```

### Attack Status
```python
class AttackStatus:
    attack_id: str
    status: str  # "running", "paused", "completed", "stopped"
    progress: float
    speed: float
    eta: str
    attempts: int
    found_password: Optional[str]
```

### Attack Results
```python
class AttackResults:
    attack_id: str
    found_password: Optional[str]
    attempts: int
    duration: int
    speed_avg: float
    speed_max: float
```

## Security

### API Key Management
- Store API keys securely
- Rotate keys regularly
- Use environment variables
- Never commit keys to version control

### Rate Limiting
- 100 requests per minute per API key
- WebSocket: 10 connections per API key
- Burst allowance: 20 requests

### SSL/TLS
Enable HTTPS in production:
```python
client = Client(
    base_url="https://api.example.com",
    api_key="your_api_key",
    verify_ssl=True
)
```

## Testing

### Unit Tests
```bash
pytest tests/api/
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### API Test Example
```python
import requests

def test_start_attack():
    response = requests.post(
        "http://localhost:8080/api/v1/attacks/start",
        headers={"Authorization": "Bearer test_key"},
        json={
            "target": "test",
            "attack_type": "Brute Force Attack",
            "min_length": 4,
            "max_length": 6
        }
    )
    assert response.status_code == 200
    assert "attack_id" in response.json()
```

## Additional Resources

- [User Guide](USER_GUIDE.md) - End-user documentation
- [Contributing Guide](CONTRIBUTING.md) - Developer contribution guidelines
- [GitHub Repository](https://github.com/tworjaga/keyspace)

---

**Questions?** → [Support](SUPPORT.md)
