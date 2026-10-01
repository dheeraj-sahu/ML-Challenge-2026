import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "utils"))
import validate_submission


class ValidateSubmissionTests(unittest.TestCase):
    def write_file(self, directory, relative_path, content):
        path = Path(directory, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_accepts_complete_matching_and_candidate_files(self):
        with tempfile.TemporaryDirectory() as directory:
            test_dir = Path(directory, "dataset", "test")
            self.write_file(
                test_dir,
                "test_source1.tsv",
                "entity_id\tbusiness_name\nS1-1\tAlpha\nS1-2\tBeta\n",
            )
            matching = self.write_file(
                directory,
                "matching.tsv",
                "source1_entity_id\tmatched_entity_ids\nS1-1\tS2-1\nS1-2\t\n",
            )
            candidate = self.write_file(
                directory,
                "candidate.tsv",
                "source1_entity_id\tcandidate_entity_ids\nS1-1\tS2-1\nS1-2\t\n",
            )

            errors, warnings = validate_submission.validate(
                str(matching), str(candidate), str(test_dir)
            )

            self.assertEqual(errors, [])
            self.assertEqual(len(warnings), 1)

    def test_rejects_duplicate_source_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            test_dir = Path(directory, "dataset", "test")
            self.write_file(test_dir, "test_source1.tsv", "entity_id\nS1-1\n")
            matching = self.write_file(
                directory,
                "matching.tsv",
                "source1_entity_id\tmatched_entity_ids\nS1-1\t\nS1-1\tS2-1\n",
            )

            errors, _ = validate_submission.validate(
                str(matching), None, str(test_dir)
            )

            self.assertTrue(any("duplicate source1_entity_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
