import pexpect
import time
import datetime
import sys
import subprocess
import queue
import threading

# Released under MIT License

# Copyright (c) 2025 StarkGtsk.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



class TonStorageAPI:
    def __init__(self, startup_cmd: str):
        self.startup_cmd = startup_cmd
        self.child = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.output_buffer = ""


    def check_daemon_alive(self) -> bool:
        try:
            result = subprocess.run(
                ["pgrep", "-f", "storage-daemon"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

    def _collect_output(self):
        """Collect output from CLI to console"""
        while self.is_running and self.child and self.child.isalive():
            try:

                char = self.child.read(1)
                if char:
                    self.output_buffer += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
            except:
                break

    def _extract_command_output(self, command: str) -> str:
        """Extract output from specific CLI command"""
        if not self.output_buffer:
            return ""

        lines = self.output_buffer.split('\n')
        command_output = []
        found_command = False

        for line in lines:
            if command in line:
                found_command = True
                continue
            if found_command:

                if line.strip() and not line.startswith('['):
                    command_output.append(line)
                else:
                    break

        return '\n'.join(command_output).strip()

    # def start_cli_session(self) -> bool:
    #     if not self.check_daemon_alive():
    #         print(f'[{datetime.datetime.now()}] ERROR: STORAGE-DAEMON IA NOT RUNNING')
    #
    #         return False
    #
    #     try:
    #         self.child = pexpect.spawn(self.startup_cmd, encoding='utf-8', timeout=1)
    #         # self.child.logfile = sys.stdout
    #
    #         # Init collect output in another thread
    #         self.output_collector = threading.Thread(target=self._collect_output, daemon=True)
    #
    #
    #         self.child.expect(pexpect.EOF, timeout=1)
    #     except pexpect.TIMEOUT:
    #         self.is_running = True
    #         self.worker_thread = threading.Thread(target=self._command_worker, daemon=True)
    #         self.worker_thread.start()
    #
    #         print(f'[{datetime.datetime.now()}] LOG: STORAGE-CLI SESSION STARTED\n')
    #
    #         return True
    #     except Exception as e:
    #         print(f'[{datetime.datetime.now()}] ERROR: {e}')
    #         return False

    def start_cli_session(self) -> bool:
        if not self.check_daemon_alive():
            print(f'[{datetime.datetime.now()}] ERROR: STORAGE-DAEMON IS NOT RUNNING')
            return False

        try:
            self.child = pexpect.spawn(self.startup_cmd, encoding='utf-8', timeout=10)

            # Init collect output in another thread
            self.output_collector = threading.Thread(target=self._collect_output, daemon=True)

            self.is_running = True
            self.output_collector.start()

            # Wait...
            time.sleep(2)

            if not self.child.isalive():
                return False

            print(f'[{datetime.datetime.now()}] LOG: STORAGE-CLI SESSION STARTED')

            # Init command handler
            self.worker_thread = threading.Thread(target=self._command_worker, daemon=True)
            self.worker_thread.start()

            return True

        except Exception as e:
            print(f'[{datetime.datetime.now()}] ERROR: {e}')
            return False

    def _command_worker(self):
        while self.is_running:
            try:
                command_data = self.command_queue.get(timeout=1.0)
                command_id, command, callback = command_data

                # clear the buffer before cmd exec
                self.output_buffer = ""
                self.last_command = command

                self.child.sendline(command)

                time.sleep(self._get_command_timeout(command))

                response = f'[{datetime.datetime.now()}] LOG: COMMAND {command} EXECUTED'

                if callback:
                    callback(command_id, response)

                self.response_queue.put((command_id, response))

            except queue.Empty:
                continue
            except Exception as e:
                print(f'[{datetime.datetime.now()}] ERROR: {e}')
                self.response_queue.put(("ERROR", str(e)))

    def _get_command_timeout(self, command: str) -> float:
        if any(cmd in command for cmd in ['list', 'get-peers', 'get-pieces-info']):
            return 3.0
        elif 'create' in command:
            return 4.0
        else:
            return 2.0

    def send_command(self, command: str, command_id: str = None, callback: callable = None):
        if not self.is_running:
            raise RuntimeError(f'[{datetime.datetime.now()}] ERROR: CLI SESSION IS NOT RUNNING')

        if command_id is None:
            command_id = str(datetime.datetime.now().timestamp())

        self.command_queue.put((command_id, command, callback))

        try:
            response_id, response = self.response_queue.get(timeout=3.0)
            if response_id == command_id:
                return response
        except queue.Empty:
            return f'[{datetime.datetime.now()}] ERROR: TIMEOUT WAITING FOR RESPONSE'

        return f'[{datetime.datetime.now()}] ERROR: UNKNOWN RESPONSE'

    def send_command_async(self, command: str, command_id: str = None, callback: callable = None):
        if not self.is_running():
            raise RuntimeError(f'[{datetime.datetime.now()}] ERROR: CLI SESSION IS NOT RUNNING')

        if command_id is None:
            command_id = str(datetime.datetime.now().timestamp())

        self.command_queue.put((command_id, command, callback))

        return command_id

    def create(self, path: str, description: str = None, no_upload: bool = False, copy: bool = False, json_output: bool = False) -> str:
        """Create bag of files from path"""

        cmd = f"create {path}"
        if description:
            cmd += f" -d {description}"
        if no_upload:
            cmd += f" --no-upload"
        if copy:
            cmd += f" --copy"
        if json_output:
            cmd += f" --json"
        return self.send_command(cmd)

    def add_by_hash(self, bag_id: str, root_dir: str = None, paused: bool = False, no_upload: bool = False, json_output: bool = False, partial: list = None) -> str:
        """Add bag with given BagID"""

        cmd = f"add-by-hash {bag_id}"
        if root_dir:
            cmd += f" -d {root_dir}"
        if paused:
            cmd += f" --paused"
        if no_upload:
            cmd += f" --no-upload"
        if json_output:
            cmd += f" --json"
        if partial:
            cmd += " --partial" + "".join(partial)
        return self.send_command(cmd)

    def add_by_meta(self, meta_file: str, root_dir: str = None, paused: bool = False, no_upload: bool = False, json_output: bool = False, partial: list = None) -> str:
        """Load meta from file and add bag"""
        cmd = f"add-by-meta {meta_file}"
        if root_dir:
            cmd += f" -d {root_dir}"
        if paused:
            cmd += f" --paused"
        if no_upload:
            cmd += f" --no-upload"
        if json_output:
            cmd += f" --json"
        if partial:
            cmd += f" --partial" + "".join(partial)
        return self.send_command(cmd)

    def list_bags(self, hashes: bool = False, json_output: bool = False) -> str:
        """Print list of bags"""

        cmd = "list"
        if hashes:
            cmd += " --hashes"
        if json_output:
            cmd += " --json"
        return self.send_command(cmd)

    def get_bag_info(self, bag: str, json_output: bool = False) -> str:
        """Print info about bag"""

        cmd = f"get {bag}"
        if json_output:
            cmd += " --json"
        return self.send_command(cmd)

    def get_meta(self, bag: str, output_file: str) -> str:
        """Save bag meta to file"""

        return self.send_command(f"get-meta {bag} {output_file}")

    def get_peers(self, bag: str, json_output: bool = False) -> str:
        """Print list of peers"""

        cmd = f"get-peers {bag}"
        if json_output:
            cmd += " --json"
        return self.send_command(cmd)

    def download_pause(self, bag: str) -> str:
        return self.send_command(f"download-pause {bag}")

    def download_resume(self, bag: str) -> str:
        return self.send_command(f"download-resume {bag}")

    def upload_pause(self, bag: str) -> str:
        return self.send_command(f"upload-pause {bag}")

    def upload_resume(self, bag:str) -> str:
        return self.send_command(f"upload-resume {bag}")

    def remove_bag(self, bag:str, remove_files: bool = False) -> str:
        cmd = f"remove {bag}"
        if remove_files:
            cmd += " --remove-files"
        return self.send_command(cmd)

    def stop(self):
        """Stop CLI Session"""

        self.is_running = False
        if self.child and self.child.isalive():
            self.child.sendline("exit")
            self.child.close()
        print(f'[{datetime.datetime.now()}] LOG: STORAGE-CLI SESSION STOPPED')

    def help(self):
        return self.send_command("help")

    def deploy_provider(self):
        return self.send_command("deploy-provider")

    def run_interactive_storage_cli(self):
        try:

            child = pexpect.spawn(self.startup_cmd, encoding='utf-8', timeout=10)
            child.logfile = sys.stdout
            child.expect(pexpect.EOF, timeout=1)


        except pexpect.TIMEOUT:
            while True:
                try:
                    child.expect(pexpect.EOF, timeout=1)
                except pexpect.TIMEOUT:
                    print(f'[{datetime.datetime.now()}] LOG: STORAGE-DAEMON-CLI IS WORKING')
                    uinput = input(">>> ")
                    if uinput.lower() in ['exit', 'close', 'quit']:
                        print(f'[{datetime.datetime.now()}] LOG: STORAGE-DAEMON-CLI STOP')

                        child.sendline("exit")
                    if not child.isalive():
                        print(f'[{datetime.datetime.now()}] ERROR: PROCESS UNEXPECTEDLY STOPPED')
                        break
                    else:
                        child.sendline(uinput)
                except Exception as e:
                    print(f'[{datetime.datetime.now()}] ERROR: {e}')



if __name__ == "__main__":
    storage_cli_startup = '/Users/gtsk/ton/build/storage/storage-daemon/storage-daemon-cli -I 127.0.0.1:5555 -k /Users/gtsk/ton/build/storage/storage-daemon/ton-storage-db/cli-keys/client -p /Users/gtsk/ton/build/storage/storage-daemon/ton-storage-db/cli-keys/server.pub'

    api = TonStorageAPI(storage_cli_startup)

    if api.start_cli_session():
        print(api.help())
        time.sleep(3)
        print(api.help())
        time.sleep(2)
        print(api.deploy_provider())

        api.stop()

