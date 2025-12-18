import subprocess
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union, Optional, Dict

class MavenHelper():
    def __init__(self, runner):
        """
        runner must provide a call(command: Union[str, List[str]], timeout: int) -> (code, out, err)
        e.g. self.runHostCommand or self.runContainerCommand bound to the same signature.
        """
        self.runner = runner

    # -------------------------
    # Command builders
    # -------------------------
    def mvnCommandBase(self, goals: List[str], flags: List[str] = None, file: str = None) -> List[str]:
        cmd = ["mvn"]
        if file:
            cmd += ["-f", file]
        if flags:
            cmd += flags
        cmd += goals
        return cmd

    def mvnCommandClean(self, file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(["clean"], flags=flags, file=file)

    def mvnCommandPackage(self, file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(["package"], flags=flags, file=file)

    def mvnCommandInstall(self, file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(["install"], flags=flags, file=file)

    def mvnCommandTest(self, file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(["test"], flags=flags, file=file)

    def mvnCommandExec(self, plugin_goal: str, file: str = None, flags: List[str] = None) -> List[str]:
        # plugin_goal like "exec:java" or "exec:exec@some-id"
        return self.mvn_base([plugin_goal], flags=flags, file=file)

    def mvnCommandVerify(self, file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(["verify"], flags=flags, file=file)

    def mvnCommandCustom(self, goals: List[str], file: str = None, flags: List[str] = None) -> List[str]:
        return self.mvn_base(goals, flags=flags, file=file)

    # -------------------------
    # Maven availability checks
    # -------------------------
    def isMavenAvailable(self, timeout: int = 10) -> bool:
        code, out, err = self.runner(["mvn", "-v"], timeout=timeout)
        return code == 0 and ("Apache Maven" in out or "Maven home:" in out or "Maven" in out.splitlines()[0] if out else False)

    # -------------------------
    # Convenience high-level helpers
    # -------------------------
    '''
    def run_mvn(self, goals: List[str], file: str = None, flags: List[str] = None, timeout: int = 300) -> Tuple[int, str, str]:
        cmd = self.mvn_custom(goals, file=file, flags=flags)
        return self.runner(cmd, timeout=timeout)

    def run_clean_install(self, file: str = None, flags: List[str] = None, timeout: int = 600) -> Tuple[int, str, str]:
        cmd = self.mvn_install(file=file, flags=flags)
        return self.runner(cmd, timeout=timeout)

    def run_test(self, file: str = None, flags: List[str] = None, timeout: int = 300) -> Tuple[int, str, str]:
        cmd = self.mvn_test(file=file, flags=flags)
        return self.runner(cmd, timeout=timeout)

    def run_exec(self, plugin_goal: str, file: str = None, flags: List[str] = None, timeout: int = 300) -> Tuple[int, str, str]:
        cmd = self.mvn_exec(plugin_goal, file=file, flags=flags)
        return self.runner(cmd, timeout=timeout)
    '''

    def isMavenPom(path):
        """Return True if path points to a pom.xml that looks like a Maven POM."""
        if not os.path.isfile(path):
            return False
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception:
            return False

        # Check root tag name (may include namespace)
        tag = root.tag
        # handle namespace: "{namespace}project" -> get local name
        local = tag.split("}")[-1]
        if local != "project":
            return False

        # Check for Maven namespace or common child elements
        ns = None
        if tag.startswith("{"):
            ns = tag[1:].split("}")[0]

        has_maven_ns = ns and ("maven" in ns or "apache.org" in ns)
        has_core_elems = any(root.find(x) is not None for x in ("groupId", "artifactId", "modelVersion"))

        return has_maven_ns or has_core_elems

    def isMavenProject(
        self,
        path: Union[str, Path],
        stop_at: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """
        Return the Path to the Maven project root (directory containing pom.xml)
        if `path` is inside a Maven project. `path` may be a file, the project
        root, or any subdirectory.

        Parameters:
        - path: starting file or directory to check.
        - stop_at: optional directory path (inclusive). Walking upward will not
            go above this directory. If stop_at is None, walk up to the filesystem root.

        Behavior:
        - If `path` is a file, the search starts from its parent directory.
        - The function checks the start directory and each ancestor up to and
            including `stop_at` (if provided) or the filesystem root.
        - Returns the Path containing pom.xml, or None if none found.
        """
        start = Path(path).resolve()
        if start.exists() and start.is_file():
            start = start.parent

        stop = Path(stop_at).resolve() if stop_at is not None else None
        # If stop is provided but not a directory, use its parent
        if stop is not None and not stop.is_dir():
            stop = stop.parent

        print(start+","+stop)
        # If stop is provided, ensure it's an ancestor of start; if not, do nothing
        if stop is not None and stop not in (start, *start.parents):
            # stop is not an ancestor of start so no upward search allowed beyond start
            # we'll still check start itself
            stop = start

        current = start
        while True:
            if (current / "pom.xml").is_file():
                if (self.isMavenPom(current / "pom.xml"))
                    return current
            if current == stop or current.parent == current:
                # reached the provided stop directory or filesystem root
                break
            current = current.parent
        return None
