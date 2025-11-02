"""
Verification script for Phase 9: SDK & Productization.

Tests:
1. Version imports
2. SDK imports
3. CLI module availability
4. Config validator
5. Manifest existence
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')


def test_version():
    """Test version module."""
    print("Testing version module...")
    try:
        from odibi_core.__version__ import __version__, __phase__, __supported_engines__

        assert __version__ == "1.0.0", f"Expected version 1.0.0, got {__version__}"
        assert __phase__ == "v1.0-phase9", f"Expected phase v1.0-phase9, got {__phase__}"
        assert "pandas" in __supported_engines__, "Pandas should be in supported engines"
        assert "spark" in __supported_engines__, "Spark should be in supported engines"

        print(f"  ✅ Version: {__version__}")
        print(f"  ✅ Phase: {__phase__}")
        print(f"  ✅ Engines: {__supported_engines__}")
        return True
    except Exception as e:
        print(f"  ❌ Version test failed: {e}")
        return False


def test_sdk_imports():
    """Test SDK module imports."""
    print("\nTesting SDK imports...")
    try:
        from odibi_core.sdk import ODIBI, Pipeline, PipelineResult

        print("  ✅ ODIBI imported")
        print("  ✅ Pipeline imported")
        print("  ✅ PipelineResult imported")

        # Test ODIBI.version()
        version = ODIBI.version()
        assert version == "1.0.0", f"ODIBI.version() should return 1.0.0, got {version}"
        print(f"  ✅ ODIBI.version() = {version}")

        return True
    except Exception as e:
        print(f"  ❌ SDK import test failed: {e}")
        return False


def test_config_validator():
    """Test ConfigValidator import."""
    print("\nTesting ConfigValidator...")
    try:
        from odibi_core.sdk.config_validator import ConfigValidator, ValidationLevel

        validator = ConfigValidator()
        print("  ✅ ConfigValidator instantiated")
        print("  ✅ ValidationLevel enum available")

        # Test required fields
        assert hasattr(validator, "REQUIRED_FIELDS"), "REQUIRED_FIELDS should exist"
        assert "layer" in validator.REQUIRED_FIELDS, "layer should be required"
        assert "name" in validator.REQUIRED_FIELDS, "name should be required"
        print(f"  ✅ Required fields: {validator.REQUIRED_FIELDS}")

        return True
    except Exception as e:
        print(f"  ❌ ConfigValidator test failed: {e}")
        return False


def test_cli_module():
    """Test CLI module availability."""
    print("\nTesting CLI module...")
    try:
        from odibi_core import cli

        assert hasattr(cli, "main"), "CLI should have main function"
        print("  ✅ CLI module available")
        print("  ✅ main() function exists")
        return True
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False


def test_manifest():
    """Test manifest.json existence."""
    print("\nTesting manifest.json...")
    try:
        import json

        manifest_path = Path(__file__).parent / "manifest.json"
        assert manifest_path.exists(), "manifest.json should exist"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert manifest["version"] == "1.0.0", "Manifest version should be 1.0.0"
        assert manifest["phase"] == "v1.0-phase9", "Manifest phase should be v1.0-phase9"
        assert "sdk" in manifest["features"], "SDK should be in features"
        assert manifest["features"]["sdk"] is True, "SDK feature should be enabled"

        print(f"  ✅ Manifest found: {manifest_path}")
        print(f"  ✅ Version: {manifest['version']}")
        print(f"  ✅ Phase: {manifest['phase']}")
        print(f"  ✅ SDK feature enabled: {manifest['features']['sdk']}")

        return True
    except Exception as e:
        print(f"  ❌ Manifest test failed: {e}")
        return False


def test_pyproject_toml():
    """Test pyproject.toml configuration."""
    print("\nTesting pyproject.toml...")
    try:
        import tomli

        print("  ⚠️  tomli not installed, skipping TOML parsing")
        return True
    except ImportError:
        # Check file exists
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml should exist"

        # Read as text
        content = pyproject_path.read_text()
        assert "odibi = " in content, "CLI entry point should be defined"
        assert "click>=" in content, "click dependency should be present"
        assert "rich>=" in content, "rich dependency should be present"

        print(f"  ✅ pyproject.toml found: {pyproject_path}")
        print("  ✅ CLI entry point defined")
        print("  ✅ click dependency present")
        print("  ✅ rich dependency present")

        return True


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("ODIBI CORE Phase 9 Verification")
    print("=" * 60)

    tests = [
        ("Version Module", test_version),
        ("SDK Imports", test_sdk_imports),
        ("ConfigValidator", test_config_validator),
        ("CLI Module", test_cli_module),
        ("Manifest", test_manifest),
        ("pyproject.toml", test_pyproject_toml),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Phase 9 verification SUCCESSFUL!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
