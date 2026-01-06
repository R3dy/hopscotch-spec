import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_hopscotch.py"
FIXTURES = ROOT / "tests" / "fixtures"


def run_validator(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


class ValidateHopscotchTests(unittest.TestCase):
    def test_scene_validates(self) -> None:
        result = run_validator(FIXTURES / "scene-valid.hopscotch")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scene_missing_title_fails(self) -> None:
        result = run_validator(FIXTURES / "scene-invalid-missing-title.hopscotch")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scene missing required field 'title'", result.stderr)

    def test_scene_conditional_missing_conditions_fails(self) -> None:
        result = run_validator(FIXTURES / "scene-invalid-conditional.hopscotch")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conditional dialogue missing conditions", result.stderr)

    def test_scene_blocked_in_v02(self) -> None:
        result = run_validator(FIXTURES / "scene-v02-blocked.hopscotch")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scene blocks require hopscotchVersion >= 0.3.0", result.stderr)


if __name__ == "__main__":
    unittest.main()
