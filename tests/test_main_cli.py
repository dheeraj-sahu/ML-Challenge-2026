import subprocess
import sys
import unittest
from pathlib import Path


MAIN = Path(__file__).parents[1] / "code" / "business_entity_resolution" / "src" / "main.py"


class MainCliTests(unittest.TestCase):
    def run_main(self, *arguments):
        return subprocess.run(
            [sys.executable, str(MAIN), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_rejects_threshold_outside_probability_range(self):
        result = self.run_main("--threshold", "1.1")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--threshold must be between 0 and 1", result.stderr)

    def test_reports_missing_dataset_root(self):
        result = self.run_main("--root", str(Path(__file__).parent / "missing"))

        self.assertEqual(result.returncode, 2)
        self.assertIn("missing dataset directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
