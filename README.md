# LangChain-OpenTutorial PyPi  
- This is a package for LangChain-OpenTutorial.  

## Package File Creation  
1. Install Dependency Packages (First Time Only)  
- Ensure that `setuptools` and `wheel` are up-to-date.  
```bash
pip install --upgrade setuptools wheel
```  

2. Create Package  
- Move to the project root directory in the terminal and execute the following command:  
```bash
python setup.py sdist bdist_wheel
```  
- This command generates distribution-ready package files (.tar.gz and .whl) in the `dist/` directory.  

3. Test Package Installation  
- Install the generated package locally for testing.  
```bash
pip install dist/mypackage-0.1.0-py3-none-any.whl
```  
- After local testing, upload the package to PyPI using `twine`.  

4. Install `twine`  
- Install `twine` to upload the package to PyPI.  
```bash
pip install twine
```  

5. Upload to PyPI  
- Use `twine` to upload the package to PyPI.  
```bash
twine upload dist/*
```  
- A PyPI account is required, and login credentials will be needed.
