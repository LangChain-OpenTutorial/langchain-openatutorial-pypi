import os

def set_env(config: dict):
    """
    Set environment variables for the langchain_opentutorial package.

    Args:
        config (dict): A dictionary containing key-value pairs for configuration.
    """
    for key, value in config.items():
        os.environ[key] = str(value)
    print("Environment variables have been set successfully.")
