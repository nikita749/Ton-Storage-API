# TON Storage API Reference

## Table of Contents
- [Core API Class](#core-api-class)
- [Storage Operations](#storage-operations)
- [Bag Management](#bag-management)
- [Transfer Control](#transfer-control)
- [Bag Operations](#bag-operations)
- [Other Operations](#other-operations)
- [Best Practices](#best-practices)

## Core API Class

### `TonStorageAPI`

The main class for interacting with TON Storage.

#### Constructor

```python
TonStorageAPI(startup_cmd: str)
```
## Parameters: :

startup_cmd (str): Complete command to start storage-daemon-cli with all ## Parameters: 

## Example: :

```python
from ton_storage_api import TonStorageAPI

storage_cli_startup = '/path/to/storage-daemon-cli -I 127.0.0.1:5555 -k /path/to/client -p /path/to/server.pub'
api = TonStorageAPI(storage_cli_startup)
Methods
start_cli_session()
```
Starts a persistent CLI session for multiple commands.

```python
def start_cli_session() -> bool
```
Returns: bool - True if session started successfully

## Example: :

```python
if api.start_cli_session():
    print("Session started successfully")
stop()
```
Stops the CLI session and cleans up resources.

```python
def stop() -> None
```
## Example: :

```python
api.stop()
check_daemon_alive()
```
Checks if storage-daemon process is running.

```python
def check_daemon_alive() -> bool
```
Returns: bool - True if daemon is running

## Example: :

```python
if api.check_daemon_alive():
    print("Storage daemon is running")
send_command()
Sends a raw command to storage-daemon-cli.
```
```python
def send_command(
    command: str, 
    command_id: str = None, 
    callback: callable = None
) -> str
```
## Parameters: :

- command (str): Raw CLI command to execute

- command_id (str, optional): Unique ID for tracking

- callback (callable, optional): Callback function for async handling

- Returns: str - Command execution status

## Example: :

```python
result = api.send_command("help")
send_command_async()
Sends a command asynchronously to storage-daemon-cli.

python
def send_command_async(
    command: str, 
    command_id: str = None, 
    callback: callable = None
) -> str
```
## Parameters: :

- command (str): Raw CLI command to execute

- command_id (str, optional): Unique ID for tracking

- callback (callable, optional): Callback function for async handling

- Returns: str - Command ID for tracking

## Example: :

```python
command_id = api.send_command_async("help")
Storage Operations
create()
```
Creates a new storage bag from files or directories.

```python
def create(
    path: str,
    description: str = None,
    no_upload: bool = False,
    copy: bool = False,
    json_output: bool = False
) -> str
```
## Parameters: :

- path (str): Path to file or directory

- description (str, optional): Bag description

- no_upload (bool): Don't share with peers (default: False)

- copy (bool): Copy files to internal directory (default: False)

- json_output (bool): Return JSON format (default: False)

- Returns: str - Command execution status

## Example: :


# Create bag from directory
```python
result = api.create(
    "/path/to/files",
    description="My project files"
)
```

# Create bag without uploading
````
result = api.create(
    "/path/to/private/file",
    no_upload=True
)
add_by_hash()
````
Adds a bag using its hash identifier.

```python
def add_by_hash(
    bag_id: str,
    root_dir: str = None,
    paused: bool = False,
    no_upload: bool = False,
    json_output: bool = False,
    partial: list = None
) -> str
```
## Parameters: :

- bag_id (str): Bag hash identifier

- root_dir (str, optional): Target directory for files

- paused (bool): Don't start download immediately (default: False)

- no_upload (bool): Don't share with peers (default: False)

- json_output (bool): Return JSON format (default: False)

- partial (list): List of specific files to download

- Returns: str - Command execution status

## Example: :

```python
# Add complete bag
result = api.add_by_hash(
    "abc123def456...",
    root_dir="/downloads"
)

# Add only specific files
result = api.add_by_hash(
    "abc123def456...",
    partial=["file1.txt", "file2.jpg"],
    paused=True
)
add_by_meta()
```
Adds a bag using a meta file.

```python
def add_by_meta(
    meta_file: str,
    root_dir: str = None,
    paused: bool = False,
    no_upload: bool = False,
    json_output: bool = False,
    partial: list = None
) -> str
```
## Parameters: :

- meta_file (str): Path to meta file

- root_dir (str, optional): Target directory for files

- paused (bool): Don't start download immediately (default: False)

- no_upload (bool): Don't share with peers (default: False)

- json_output (bool): Return JSON format (default: False)

- partial (list): List of specific files to download

- Returns: str - Command execution status

## Example: :

```python
result = api.add_by_meta(
    "/path/to/meta.bin",
    root_dir="/downloads"
)
```


## Parameters: :

- hashes (bool): Show full BagIDs (default: False)

- json_output (bool): Return JSON format (default: False)

- Returns: str - Command execution status with bag list

Gets detailed information about a specific bag.

```python
def get_bag_info(
    bag: str,
    json_output: bool = False
) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- json_output (bool): Return JSON format (default: False)

- Returns: str - Command execution status with bag information

## Example: :

```python
info = api.get_bag_info("abc123")
get_meta()
```
Saves bag meta information to a file.

```python
def get_meta(bag: str, output_file: str) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- output_file (str): Path to save meta file

- Returns: str - Command execution status

## Example: :

```python
api.get_meta("abc123", "/path/to/meta.bin")
get_peers()
```
Gets list of peers for a bag.

```python
def get_peers(bag: str, json_output: bool = False) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- json_output (bool): Return JSON format (default: False)

- Returns: str - Command execution status with peers list

## Example: :

```python
peers = api.get_peers("abc123")
Transfer Control
download_pause()
```
Pauses download of a bag.

```python
def download_pause(bag: str) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- Returns: str - Command execution status

## Example: :

```python
api.download_pause("abc123")
download_resume()
```
Resumes download of a bag.

```python
def download_resume(bag: str) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- Returns: str - Command execution status

## Example: :

```python
api.download_resume("abc123")
upload_pause()
```
Pauses upload of a bag.

```python
def upload_pause(bag: str) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- Returns: str - Command execution status

## Example: :

```python
api.upload_pause("abc123")
upload_resume()
```
Resumes upload of a bag.

```python
def upload_resume(bag: str) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- Returns: str - Command execution status

## Example: :

```python
api.upload_resume("abc123")
Bag Operations
remove_bag()
```
Removes a bag from storage.

```python
def remove_bag(bag: str, remove_files: bool = False) -> str
```
## Parameters: :

- bag (str): Bag ID or index

- remove_files (bool): Also remove downloaded files (default: False)

- Returns: str - Command execution status

## Example: :

```python
# Remove bag but keep files
api.remove_bag("abc123")

# Remove bag and all files
api.remove_bag("abc123", remove_files=True)
Other Operations
help()
```
Displays help information about available commands.

```python
def help() -> str
```
- Returns: str - Command execution status with help text

## Example: :

```python
help_text = api.help()
deploy_provider()
```
Deploys a storage provider contract.

```python
def deploy_provider() -> str
```
- Returns: str - Command execution status with provider address

## Example: :

```python
provider_info = api.deploy_provider()
run_interactive_storage_cli()
```
Runs storage CLI in interactive mode (for debugging).

```python
def run_interactive_storage_cli() -> None
```
## Example: :

```python
api.run_interactive_storage_cli()
```
# Best Practices
- ### Always check daemon status before operations using check_daemon_alive()

- ### Start CLI session before sending commands using start_cli_session()

- ### Stop CLI session when done using stop()

- ### Handle timeouts for large file operations

- ### Monitor storage limits and clean up unused bags

- ### Use appropriate command timeouts based on operation type

# Response Format
### All methods return status messages in the format:

```text
[timestamp] STATUS: message
```
## Example:  responses:

```text
[2024-01-01 12:00:00] LOG: COMMAND help EXECUTED
[2024-01-01 12:00:00] ERROR: CLI SESSION IS NOT RUNNING
[2024-01-01 12:00:00] ERROR: TIMEOUT WAITING FOR RESPONSE
```
# Error Handling
## The API handles common errors:

- ### CLI session not running - when commands are sent without active session

- ### Timeout errors - when commands take too long to execute

- ### Process errors - when storage-daemon is not available

