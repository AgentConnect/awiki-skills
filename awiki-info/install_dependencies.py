#!/usr/bin/env python3
"""
依赖安装脚本
支持 uv、pip 等多种安装方式
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> bool:
    """运行命令"""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        return False


def find_installer() -> tuple[str, list[str]]:
    """查找可用的包安装器"""
    script_dir = Path(__file__).parent

    # 优先使用 uv
    if shutil.which("uv"):
        return "uv", ["uv", "sync", "--directory", str(script_dir)]

    # 其次使用 pip
    if shutil.which("pip"):
        return "pip", ["pip", "install", "mcp>=1.0.0"]

    # 尝试使用 python -m pip
    return "python-pip", [sys.executable, "-m", "pip", "install", "mcp>=1.0.0"]


def main() -> int:
    """主函数"""
    print("=" * 50)
    print("awiki-info Skill 依赖安装")
    print("=" * 50)

    installer_name, cmd = find_installer()
    print(f"\n使用 {installer_name} 安装依赖...")
    print(f"执行: {' '.join(cmd)}\n")

    if run_command(cmd):
        print("\n依赖安装成功!")
        print("\n可以开始使用了:")
        print("  python scripts/get_daily_summary.py")
        print("  python scripts/search_activities.py --keyword AI")
        return 0
    else:
        print("\n依赖安装失败，请手动安装:")
        print("  pip install mcp>=1.0.0")
        print("或:")
        print("  uv add mcp")
        return 1


if __name__ == "__main__":
    sys.exit(main())
