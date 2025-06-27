import pytest
import sys

if __name__ == '__main__':
    sys.exit(pytest.main([
        '--maxfail=1',
        '--disable-warnings',
        '--tb=short',
        '--junitxml=report.xml'
    ]))
