import unittest

import os
import pycodestyle


BASE_DIRS = [
    'etl_utils',
    'sdk',
    'tests'
]


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        python_files = []
        for base_dir in BASE_DIRS:
            for root, dirs, files in os.walk(base_dir):
                files = [f for f in files if not f.startswith('__')]
                files = [f for f in files if f.endswith('.py')]
                python_files.extend([os.path.join(root, f) for f in files])

        style = pycodestyle.StyleGuide(quiet=True)
        result = style.check_files(python_files)
        self.assertEqual(result.total_errors, 0)
