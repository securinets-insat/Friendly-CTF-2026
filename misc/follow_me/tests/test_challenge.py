import base64
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


CHALL = Path(__file__).resolve().parents[1] / "chall.py"


def make_tar(name, content=None, target=None):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        item = tarfile.TarInfo(name)
        if target is not None:
            item.type = tarfile.SYMTYPE
            item.linkname = target
            archive.addfile(item)
        else:
            content = content or b""
            item.size = len(content)
            archive.addfile(item, io.BytesIO(content))
    return output.getvalue()


def run_challenge(archive):
    result = subprocess.run(
        [sys.executable, str(CHALL)],
        input=base64.b64encode(archive) + b"\n",
        stdout=subprocess.PIPE,
        timeout=5,
        check=True,
    )
    return result.stdout


class ChallengeTests(unittest.TestCase):
    def test_regular_report(self):
        output = run_challenge(make_tar("report.txt", b"hello"))
        self.assertIn(b"Report:\nhello", output)

    def test_other_names_are_rejected(self):
        output = run_challenge(make_tar("../report.txt", b"hello"))
        self.assertIn(b"Invalid archive.", output)

    def test_symlink_is_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            flag = Path(folder) / "flag.txt"
            flag.write_text("Securinets{test_flag}")
            archive = make_tar("report.txt", target=str(flag))
            self.assertIn(b"Securinets{test_flag}", run_challenge(archive))


if __name__ == "__main__":
    unittest.main()
