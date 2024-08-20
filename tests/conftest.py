import time
from dotenv import load_dotenv

load_dotenv()


def pytest_runtest_teardown():
    """Add a delay between each test."""
    time.sleep(1)
