# langchain_opentutorial/package.py
import subprocess
import sys
from enum import Enum
from typing import Optional

class ReleaseType(Enum):
    """릴리스 유형을 정의하는 열거형 클래스."""
    STABLE = "stable"
    NIGHTLY = "nightly"

def get_environment_key() -> str:
    """현재 환경의 OS와 Python 버전을 조합하여 고유 키를 반환합니다."""
    platform_map = {
        'win32': 'windows',
        'darwin': 'mac',
        'linux': 'linux'
    }
    os_name = platform_map.get(sys.platform, 'unknown')
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"{os_name}-py{python_version}"

class PackageVersions:
    """패키지 버전 정보를 관리하는 클래스."""
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
        특정 날짜 또는 릴리스 유형에 맞는 패키지 버전을 반환합니다.
        release_type_or_date가 None이면 기본적으로 stable 버전을 반환하고,
        날짜 형식이면 해당 날짜의 버전을 반환합니다.
        """
        if release_type_or_date:
            # 날짜 형식인지 확인
            if release_type_or_date in cls.VERSIONS[env_key]:
                return cls.VERSIONS[env_key][release_type_or_date].get(package)
            else:
                # release_type으로 간주
                release_versions = cls.VERSIONS[env_key].get(release_type_or_date, {})
                return release_versions.get(package)
        else:
            # 기본적으로 stable 반환
            release_versions = cls.VERSIONS[env_key].get(ReleaseType.STABLE.value, {})
            return release_versions.get(package)
        
def install(packages: list, verbose: bool = True, upgrade: bool = False, 
            release_type_or_date: Optional[str] = ReleaseType.STABLE.value) -> None:
    """
    환경 및 릴리스 유형에 따라 특정 버전의 Python 패키지를 설치합니다.

    Args:
        packages (list): 설치할 패키지 이름의 리스트.
        verbose (bool): 설치 메시지를 출력할지 여부.
        upgrade (bool): 패키지를 업그레이드할지 여부.
        release_type_or_date (str, optional): 설치할 릴리스 유형 (stable 또는 nightly) 또는 특정 날짜 (형식: YYYY-MM-DD).
    """
    if not isinstance(packages, list):
        raise ValueError("Packages must be provided as a list.")
    if not packages:
        print("No packages to install.")
        return
    
    try:
        env_key = get_environment_key()
        if verbose:
            print(f"Current environment: {env_key}")
            print(f"Release type or date: {release_type_or_date}")
            print(f"Installing packages: {', '.join(packages)}...")
        
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        
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
        
        cmd.extend(versioned_packages)
        
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL if not verbose else None)
        
        if verbose:
            print(f"Successfully installed: {', '.join(versioned_packages)}")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"Failed to install packages: {', '.join(packages)}")
            print(f"Error: {e}")