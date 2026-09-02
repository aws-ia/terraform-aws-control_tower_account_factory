#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

BUILDSPECS = (
    "modules/aft-code-repositories/buildspecs/ct-aft-account-provisioning-customizations.yml",
    "modules/aft-code-repositories/buildspecs/ct-aft-account-request.yml",
    "modules/aft-customizations/buildspecs/aft-account-customizations-terraform.yml",
    "modules/aft-customizations/buildspecs/aft-create-pipeline.yml",
    "modules/aft-customizations/buildspecs/aft-global-customizations-terraform.yml",
)

BACKEND_TEMPLATES = (
    "examples/multiple-account-customizations/account-customization-dev/terraform/backend.jinja",
    "examples/multiple-account-customizations/account-customization-prod/terraform/backend.jinja",
    "examples/multiple-regions-customization/multiple-regions/terraform/backend.jinja",
    "sources/aft-customizations-repos/aft-account-customizations/ACCOUNT_TEMPLATE/terraform/backend.jinja",
    "sources/aft-customizations-repos/aft-account-provisioning-customizations/terraform/backend.jinja",
    "sources/aft-customizations-repos/aft-account-request/terraform/backend.jinja",
    "sources/aft-customizations-repos/aft-global-customizations/terraform/backend.jinja",
)


def extract_tofu_install_branch(buildspec: Path) -> str:
    lines = buildspec.read_text().splitlines()
    marker = 'if [ $TF_DISTRIBUTION = "tofu" ]; then'
    start = next(index for index, line in enumerate(lines) if line.strip() == marker)
    indentation = len(lines[start]) - len(lines[start].lstrip())

    for end in range(start + 1, len(lines)):
        line = lines[end]
        if line.strip() == "else" and len(line) - len(line.lstrip()) == indentation:
            return textwrap.dedent("\n".join(lines[start + 1 : end]))

    raise AssertionError(f"OpenTofu install branch has no matching else: {buildspec}")


def extract_variable_block(variable_name: str) -> str:
    source = (REPOSITORY_ROOT / "variables.tf").read_text()
    start = source.index(f'variable "{variable_name}" {{')
    depth = 0

    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]

    raise AssertionError(f"Variable block is not balanced: {variable_name}")


class OpenTofuSupportTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.temporary_path = Path(self.temporary_directory.name)

    def create_fake_curl(self, checksum_matches: bool) -> Path:
        fake_bin = self.temporary_path / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        fake_curl = fake_bin / "curl"
        fake_curl.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env python3
                import hashlib
                from pathlib import Path
                import sys
                import zipfile

                arguments = sys.argv[1:]
                output = Path(arguments[arguments.index("-o") + 1])

                if output.name.endswith("_SHA256SUMS"):
                    archive = next(Path.cwd().glob("tofu_*_linux_amd64.zip"))
                    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
                    if {not checksum_matches!r}:
                        digest = "0" * 64
                    output.write_text(f"{{digest}}  {{archive.name}}\\n")
                else:
                    tofu = zipfile.ZipInfo("tofu")
                    tofu.external_attr = 0o755 << 16
                    with zipfile.ZipFile(output, "w") as archive:
                        archive.writestr(tofu, "#!/bin/sh\\necho OpenTofu v1.12.6\\n")
                """
            )
        )
        fake_curl.chmod(0o755)
        return fake_bin

    def run_install_branch(self, buildspec: str, checksum_matches: bool):
        fake_bin = self.create_fake_curl(checksum_matches)
        install_directory = self.temporary_path / "install"
        install_directory.mkdir(exist_ok=True)

        script = extract_tofu_install_branch(REPOSITORY_ROOT / buildspec)
        script = script.replace("/usr/bin", str(install_directory))
        script = script.replace("/opt/aft/bin", str(install_directory))
        script += '\n"$TF_BINARY" --version\n'

        environment = os.environ.copy()
        environment["PATH"] = (
            f"{fake_bin}{os.pathsep}{install_directory}{os.pathsep}{environment['PATH']}"
        )
        environment["TF_VERSION"] = "1.12.6"

        return subprocess.run(
            ["/bin/bash", "-u", "-o", "pipefail", "-c", script],
            cwd=self.temporary_path,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_all_buildspecs_install_an_archive_with_a_matching_checksum(self):
        for buildspec in BUILDSPECS:
            with self.subTest(buildspec=buildspec):
                result = self.run_install_branch(buildspec, checksum_matches=True)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("OpenTofu v1.12.6", result.stdout)

    def test_all_buildspecs_reject_an_archive_with_a_mismatched_checksum(self):
        for buildspec in BUILDSPECS:
            with self.subTest(buildspec=buildspec):
                result = self.run_install_branch(buildspec, checksum_matches=False)
                self.assertNotEqual(0, result.returncode, result.stdout)

    def test_backend_templates_route_tofu_to_the_s3_backend(self):
        expected_condition = '{% if tf_distribution_type in ["oss", "tofu"] -%}'
        for template in BACKEND_TEMPLATES:
            with self.subTest(template=template):
                source = (REPOSITORY_ROOT / template).read_text()
                self.assertIn(expected_condition, source)
                self.assertLess(source.index(expected_condition), source.index('backend "s3"'))

    def test_terraform_distribution_accepts_tofu(self):
        (self.temporary_path / "variables.tf").write_text(
            extract_variable_block("terraform_distribution")
        )

        result = subprocess.run(
            [
                "tofu",
                f"-chdir={self.temporary_path}",
                "plan",
                "-input=false",
                "-no-color",
                "-var=terraform_distribution=tofu",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_terraform_version_rejects_a_leading_v(self):
        (self.temporary_path / "variables.tf").write_text(
            extract_variable_block("terraform_version")
        )

        valid = subprocess.run(
            [
                "tofu",
                f"-chdir={self.temporary_path}",
                "plan",
                "-input=false",
                "-no-color",
                "-var=terraform_version=1.12.6",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, valid.returncode, valid.stderr)

        invalid = subprocess.run(
            [
                "tofu",
                f"-chdir={self.temporary_path}",
                "plan",
                "-input=false",
                "-no-color",
                "-var=terraform_version=v1.12.6",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, invalid.returncode, invalid.stdout)
        self.assertIn("Invalid value for var: terraform_version.", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
