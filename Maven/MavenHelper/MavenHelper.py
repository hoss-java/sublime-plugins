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

    def log(self,msg):
        print("[MavenHelper]", str(msg))

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
        # Normalize inputs to Path objects
        start = Path(path).resolve()
        if start.exists() and start.is_file():
            start = start.parent

        stop: Optional[Path] = None
        if stop_at is not None:
            stop = Path(stop_at).resolve()
            if not stop.is_dir():
                stop = stop.parent

        if stop is not None and stop not in (start, *start.parents):
            stop = start

        current = start
        while True:
            if (current / "pom.xml").is_file():
                #self.log(current)
                return current
            if current == stop or current.parent == current:
                break
            # defensive: ensure current stays a Path
            current = Path(current).parent
        return None
