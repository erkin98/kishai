#!/usr/bin/env python3
"""Verify that the development environment is set up correctly"""
import sys
import subprocess
from pathlib import Path


def check_command(cmd: str, name: str) -> bool:
    """Check if a command is available"""
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ {name} is installed: {result.stdout.split()[0] if result.stdout else 'OK'}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print(f"❌ {name} is not installed or not in PATH")
        return False


def check_file(path: Path, name: str) -> bool:
    """Check if a file exists"""
    if path.exists():
        print(f"✅ {name} exists")
        return True
    else:
        print(f"❌ {name} not found: {path}")
        return False


def check_venv() -> bool:
    """Check if virtual environment is active or exists"""
    venv_path = Path(".venv")
    if venv_path.exists():
        print(f"✅ Virtual environment exists at {venv_path}")
        return True
    else:
        print("⚠️  Virtual environment not found. Run 'just setup' to create one.")
        return False


def main():
    """Run all checks"""
    print("🔍 Verifying development environment setup...\n")
    
    checks = []
    
    # Check required commands
    print("📦 Checking required tools:")
    checks.append(check_command("python3", "Python 3"))
    checks.append(check_command("uv", "uv"))
    checks.append(check_command("just", "just"))
    
    print("\n📁 Checking required files:")
    checks.append(check_file(Path("pyproject.toml"), "pyproject.toml"))
    checks.append(check_file(Path("justfile"), "justfile"))
    checks.append(check_file(Path(".env.example"), ".env.example"))
    
    print("\n🐍 Checking Python environment:")
    checks.append(check_venv())
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found. Run 'just env' to create one.")
    
    print("\n" + "=" * 60)
    
    if all(checks):
        print("✅ All checks passed! Your environment is ready.")
        print("\n🚀 To start developing:")
        print("   source .venv/bin/activate  # Activate virtual environment")
        print("   just dev                    # Start development server")
        return 0
    else:
        print("❌ Some checks failed. Please install missing tools.")
        print("\n📚 Setup instructions:")
        print("   - uv: https://github.com/astral-sh/uv#installation")
        print("   - just: https://just.systems/man/en/chapter_4.html")
        print("\nOr see LOCAL_DEV.md for detailed instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

