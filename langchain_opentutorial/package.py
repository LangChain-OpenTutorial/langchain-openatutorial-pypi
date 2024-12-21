# langchain_opentutorial/package.py
import subprocess
import sys
from enum import Enum
from typing import Optional

class ReleaseType(Enum):
    """Enum class defining release types."""
    STABLE = "stable"
    NIGHTLY = "nightly"

def get_environment_key() -> str:
    """
    Returns a unique key combining the current environment's OS and Python version.
    """
    platform_map = {
        'win32': 'windows',
        'darwin': 'mac', 
        'linux': 'linux'
    }
    os_name = platform_map.get(sys.platform, 'unknown')
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"{os_name}-py{python_version}"

import requests
from typing import Optional

class PackageVersions:
    GITHUB_RAW_URL = (
        "https://raw.githubusercontent.com/LangChain-OpenTutorial/langchain-opentutorial-pypi/refs/heads/main/package_versions.json"
    )

    @classmethod
    def fetch_versions(cls) -> dict:
        try:
            response = requests.get(cls.GITHUB_RAW_URL)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to fetch versions: {e}")
            return {}

    @classmethod
    def get_version(cls, package: str, env_key: str,
                    release_type_or_date: Optional[str] = None) -> Optional[str]:
        versions = cls.fetch_versions()
        if not versions:
            print("No version data available.")
            return None

        if release_type_or_date:
            if release_type_or_date in versions.get(env_key, {}):
                return versions[env_key][release_type_or_date].get(package)
            else:
                release_versions = versions.get(env_key, {}).get(release_type_or_date, {})
                return release_versions.get(package)
        else:
            release_versions = versions.get(env_key, {}).get("stable", {})
            return release_versions.get(package)


def install(packages: list, verbose: bool = True, upgrade: bool = False,
            release_type_or_date: Optional[str] = ReleaseType.STABLE.value) -> None:
    """
    Installs specific versions of Python packages based on environment and release type.

    Args:
        packages (list): List of package names to install.
        verbose (bool): Whether to output installation messages.
        upgrade (bool): Whether to upgrade the packages.
        release_type_or_date (str, optional): Release type (stable or nightly) or specific date (format: YYYY-MM-DD).
    """
    # Validate input parameters
    if not isinstance(packages, list):
        raise ValueError("Packages must be provided as a list.")
    if not packages:
        print("No packages to install.")
        return
    
    try:
        # Get environment key and prepare installation
        env_key = get_environment_key()
        if verbose:
            print(f"Current environment: {env_key}")
            print(f"Release type or date: {release_type_or_date}")
            print(f"Installing packages: {', '.join(packages)}...")
        
        # Prepare pip command
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        
        # Get versioned package strings
        versioned_packages = []
        for package in packages:
            version = PackageVersions.get_version(
                package, env_key, release_type_or_date
            )
            if version:
                versioned_packages.append(f"{package}=={version}")
            else:
                versioned_packages.append(package)
                if verbose:
                    print(f"Warning: No specific version found for {package}, using latest")
        
        # Execute pip install command
        cmd.extend(versioned_packages)
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL if not verbose else None)
        
        if verbose:
            print(f"Successfully installed: {', '.join(versioned_packages)}")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"Failed to install packages: {', '.join(packages)}")
            print(f"Error: {e}")