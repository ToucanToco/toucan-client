import os

import pycodestyle

BASE_DIRS = [
    'toucanclient',
    'tests'
]


def test_conformance():
    """Test that we conform to PEP-8."""
    python_files = []
    for base_dir in BASE_DIRS:
        for root, dirs, files in os.walk(base_dir):
            files = [f for f in files
                     if not f.startswith('__') and f.endswith('.py')]
            python_files.extend([os.path.join(root, f) for f in files])
    style = pycodestyle.StyleGuide(quiet=True)
    result = style.check_files(python_files)
    assert result.total_errors == 0
