import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest

if __name__ == "__main__":
    sys.exit(pytest.main(["tests/test_goals.py"]))
