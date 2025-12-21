import subprocess
import json
import os
from typing import List, Tuple, Union, Optional, Dict

class ShellHelper():
    def runHostCommand(self,command: Union[str, List[str]], timeout: int = 60) -> Tuple[int, str, str]:
        """
        Run a command on the host without invoking a shell.
        - command: list[str] (recommended) or str (will be naively split)
        - timeout: seconds to wait before killing the process

        Returns: (exit_code, stdout, stderr)
        """
        if isinstance(command, str):
            cmd_args = command.split() # caller should prefer list to avoid splitting issues
        else:
            cmd_args = list(command)

        try:
            proc = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            return -1, e.stdout or "", (e.stderr or "") + f"\nTimeout after {timeout}s"
        except Exception as e:
            return -1, "", str(e)
