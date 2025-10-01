# TON Storage API

The first comprehensive Python API for TON Storage - the decentralized storage solution on The Open Network blockchain.

## Features

- **Complete TON Storage Coverage** - Full implementation of all storage-daemon commands
- **Web-Ready Architecture** - Built for seamless web application integration
- **Async Support** - Non-blocking operations for high-performance applications
- **Real-time Output** - Live command output streaming
- **Session Management** - Persistent CLI sessions for multiple commands
- **Error Handling** - Comprehensive error handling and status reporting

## Installation

### Prerequisites

- Python 3.7+
- TON Storage Daemon ([Installation Guide](docs/INSTALLATION.md))

### Install from Source

```bash
git clone https://github.com/your-username/ton-storage-api.git
cd ton-storage-api
```
## Dependencies:
- pexpect>=4.8.0

##Quick start

###Basic Usage

```python
from ton_storage_api import TonStorageAPI

# Initialize the API
storage_cli_startup = '/path/to/storage-daemon-cli -I 127.0.0.1:5555 -k /path/to/client -p /path/to/server.pub'
api = TonStorageAPI(storage_cli_startup)

# Start CLI session
if api.start_cli_session():
    # Create a storage bag
    result = api.create("/path/to/your/file", description="My important file")
    print(result)
    
    # List all bags
    bags = api.list_bags()
    print(bags)
    
    # Stop session
    api.stop()
```



  
