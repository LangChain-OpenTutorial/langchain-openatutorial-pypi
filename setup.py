import re
from pathlib import Path
from setuptools import find_packages, setup    

# 패키지의 __init__.py 파일에서 __version__을 추출
def get_version():
    init_file = Path(__file__).parent / "langchain_opentutorial" / "__init__.py"
    with init_file.open() as f:
        for line in f:
            match = re.match(r"^__version__ = ['\"]([^'\"]+)['\"]", line)
            if match:
                return match.group(1)
    raise RuntimeError("Version information not found.")

setup(
    name="langchain_opentutorial",  # 패키지의 이름
    version=get_version(),  # 버전을 __init__.py에서 가져옴
    packages=find_packages(),  # 패키지 내의 모든 파이썬 패키지를 자동으로 찾아서 포함
    install_requires=[],  # 패키지의 의존성 목록
    description="LangChain-OpenTutorial(https://github.com/LangChain-OpenTutorial/LangChain-OpenTutorial) Packages",  # 패키지에 대한 간단한 설명
    author="LangChain-OpenTutorial",  # 패키지 작성자 이름
    author_email="langchain.opentutorial@gmail.com",  # 패키지 작성자 이메일
    url="https://github.com/LangChain-OpenTutorial/langchain-opentutorial-pypi",  # 패키지의 홈페이지 URL
    classifiers=[  # 패키지의 메타데이터를 분류하는 태그들
        "Programming Language :: Python :: 3",  # 지원하는 파이썬 버전
        "License :: OSI Approved :: MIT License",  # 라이선스 종류
        "Operating System :: OS Independent",  # 지원하는 운영체제
    ],
    python_requires=">=3.6",  # 필요한 최소 파이썬 버전
)
