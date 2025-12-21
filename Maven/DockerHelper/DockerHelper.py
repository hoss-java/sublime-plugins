import subprocess
import json
import os
from typing import List, Tuple, Union, Optional, Dict

class DockerHelper():
    containerName: str

    def __init__(self, containerName: str):
        self.containerName = containerName

    @staticmethod
    def isDockerAvailable() -> bool:
        """
        Return True if the `docker` CLI is available and runs successfully, otherwise False.
        """
        try:
            subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def isContainerStateRunning(self) -> bool:
        """
        Return True if the given container state is 'running' , otherwise False.
        """
        # Check container exists and is at least created
        try:
            # inspect returns non-zero if container not found
            proc = subprocess.run(["docker", "inspect", self.containerName, "--format", "{{json .}}"],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            inspect_json = proc.stdout.decode()
            data = json.loads(inspect_json)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

        # Check container state: require it to be running (up)
        state = data.get("State", {})
        if not state.get("Running", False):
            # If the state is not 'Running'.
            return False
        return True

    def runContainerCommand(self,command: Union[str, List[str]], timeout: int = 60) -> Tuple[int, str, str]:
        """
        Run a command inside a running Docker container without invoking a shell.
        - command: either a list of args (recommended) or a single string (will be split on spaces)
        - timeout: seconds to wait before killing the process

        Returns: (exit_code, stdout, stderr)
        """
        if isinstance(command, str):
            # naive split for convenience; caller should pass list to avoid splitting issues
            cmd_args = command.split()
        else:
            cmd_args = list(command)

        cmd = ["docker", "exec", "-i", self.containerName] + cmd_args

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            return -1, e.stdout or "", (e.stderr or "") + f"\nTimeout after {timeout}s"
        except Exception as e:
            return -1, "", str(e)

    def extractContainerMounts(self) -> []:
        """
        Extract mounts/volumes if the container (name or ID) exists and is running (docker inspect succeeds), otherwise an empty [].
        """
        result = []

        # Check container exists and is at least created
        try:
            # inspect returns non-zero if container not found
            proc = subprocess.run(["docker", "inspect", self.containerName, "--format", "{{json .}}"],
                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            inspect_json = proc.stdout.decode()
            data = json.loads(inspect_json)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return result

        # Check container state: require it to be running (up)
        state = data.get("State", {})
        if not state.get("Running", False):
            # If the state is not 'Running'.
            return result

        # Extract mounts/volumes
        mounts = data.get("Mounts", [])
        for m in mounts:
            host_path = m.get("Source") or m.get("HostPath") or ""
            container_path = m.get("Destination") or m.get("Destination") or m.get("Target") or ""
            mode = m.get("Mode", "") or m.get("RW", "")
            # Normalize mode to common representation
            if isinstance(mode, bool):
                mode = "rw" if mode else "ro"
            result.append({
                "HostPath": host_path,
                "ContainerPath": container_path,
                "Mode": mode
            })

        return result

    """
    Returns a list of mapped folders for the given Docker container name (or ID).
    Each item is a dict: {"HostPath": "...", "ContainerPath": "...", "Mode": "..."}.
    Return an empty list on failures.
    """
    def getContainerMounts(self) -> []:
        if self.isDockerAvailable():
            return self.extractContainerMounts()

    """
    Returns a list of mapped folders for the given Docker container name (or ID).
    Each item is a dict: {"HostPath": "...", "ContainerPath": "...", "Mode": "..."}.
    Return an empty list on failures.
    """
    def getExchangePath(self,hostPath: str) -> Tuple[str, Optional[Dict[str, str]]]:
        mappings = self.getContainerMounts()

        best_match = None
        best_host_path = ""
        for m in mappings:
            host_base = m.get("HostPath") or ""
            if not host_base:
                continue
            host_base = os.path.abspath(host_base.rstrip(os.sep))
            # Ensure host_base is a prefix of hostPath and separated by path boundary
            if hostPath == host_base or hostPath.startswith(host_base + os.sep):
                # prefer longest (most specific) host_base
                if len(host_base) > len(best_host_path):
                    best_match = m
                    best_host_path = host_base

        if not best_match:
            return hostPath, None

        # compute relative path inside the mount and map to container path
        rel = os.path.relpath(hostPath, best_host_path)
        cont_base = best_match.get("ContainerPath") or best_match.get("Destination") or ""
        cont_base = cont_base.rstrip(os.sep)
        # If relative is '.' then mapped path is exactly the container base
        if rel == ".":
            result = cont_base
        else:
            result = cont_base + os.sep + rel
        return result, best_match
