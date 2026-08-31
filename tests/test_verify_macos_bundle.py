import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify_macos_bundle.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_macos_bundle", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_thin_macho(path: Path, cpu_type: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<II", 0xFEEDFACF, cpu_type) + b"\0" * 24)


def write_fat_macho(path: Path, cpu_types: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = struct.pack(">II", 0xCAFEBABE, len(cpu_types))
    entries = b"".join(
        struct.pack(">IIIII", cpu_type, 0, 0, 0, 0) for cpu_type in cpu_types
    )
    path.write_bytes(header + entries)


class VerifyMacOSBundleTests(unittest.TestCase):
    def test_accepts_bundle_when_every_macho_matches_expected_architecture(self):
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "EchoSmith.app"
            write_thin_macho(app / "Contents" / "MacOS" / "EchoSmith", 0x0100000C)
            write_thin_macho(
                app / "Contents" / "Resources" / "backend" / "backend",
                0x0100000C,
            )

            checked = verifier.verify_bundle(app, "arm64")

            self.assertEqual(checked, 2)

    def test_accepts_universal_macho_when_it_contains_expected_architecture(self):
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "EchoSmith.app"
            write_fat_macho(
                app / "Contents" / "MacOS" / "EchoSmith",
                [0x01000007, 0x0100000C],
            )

            self.assertEqual(verifier.verify_bundle(app, "arm64"), 1)
            self.assertEqual(verifier.verify_bundle(app, "x86_64"), 1)

    def test_rejects_single_arch_backend_that_does_not_match_app_target(self):
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "EchoSmith.app"
            write_thin_macho(app / "Contents" / "MacOS" / "EchoSmith", 0x0100000C)
            wrong_backend = app / "Contents" / "Resources" / "backend" / "backend"
            write_thin_macho(wrong_backend, 0x01000007)

            with self.assertRaisesRegex(
                ValueError,
                r"backend.*expected arm64.*found x86_64",
            ):
                verifier.verify_bundle(app, "arm64")


if __name__ == "__main__":
    unittest.main()
