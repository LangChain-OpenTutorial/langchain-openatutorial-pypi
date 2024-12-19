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

class PackageVersions:
    """Class for managing package version information."""
    # Dictionary containing version information for different environments and release types
    VERSIONS = {
        'windows-py3.12': {
            "stable": {
                "langchain":"0.3.13",
                "langchain-community":"0.3.13", 
                "langchain-core":"0.3.27",
                "langchain-openai":"0.2.13",
                "langchain-text-splitters":"0.3.4",
                "langsmith":"0.2.4"
            },
            "nightly": {
                "langchain":"0.3.13",
                "langchain-community":"0.3.13",
                "langchain-core":"0.3.27", 
                "langchain-openai":"0.2.13",
                "langchain-text-splitters":"0.3.4",
                "langsmith":"0.2.4"
            },
            "2024-12-19": {
                "langchain":"0.3.13",
                "langchain-community":"0.3.13",
                "langchain-core":"0.3.27",
                "langchain-openai":"0.2.13",
                "langchain-text-splitters":"0.3.4", 
                "langsmith":"0.2.4"
            },
        },
        # 'mac-py3.9': {
        #     "stable": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        #     "nightly": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        #     "2024-12-19": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        # },
        # 'linux-py3.9': {
        #     "stable": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        #     "nightly": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        #     "2024-12-19": {
        #         'langchain-core': '0.0.0',
        #         'langchain-openai': '0.0.0',
        #     },
        # }
    }

    @classmethod
    def get_version(cls, package: str, env_key: str,
                    release_type_or_date: Optional[str] = None) -> Optional[str]:
        """
        Returns the package version for a specific date or release type.
        If release_type_or_date is None, returns the stable version by default.
        If it's a date format, returns the version for that date.
        """
        if release_type_or_date:
            # Check if it's a date format
            if release_type_or_date in cls.VERSIONS[env_key]:
                return cls.VERSIONS[env_key][release_type_or_date].get(package)
            else:
                # Consider it as release_type
                release_versions = cls.VERSIONS[env_key].get(release_type_or_date, {})
                return release_versions.get(package)
        else:
            # Return stable by default
            release_versions = cls.VERSIONS[env_key].get(ReleaseType.STABLE.value, {})
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