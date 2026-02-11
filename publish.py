#!/usr/bin/env python3
"""
Skill 打包和发布脚本
用于将 awiki-info skill 打包并发布到 GitHub
"""

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional


def run_command(cmd: list[str], check: bool = True) -> tuple[bool, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, check=check, capture_output=True, text=True, cwd=Path(__file__).parent
        )
        output = result.stdout if result.stdout else result.stderr
        return result.returncode == 0, output
    except subprocess.CalledProcessError as e:
        return False, e.stderr or str(e)
    except FileNotFoundError:
        return False, f"命令未找到: {cmd[0]}"


def get_version() -> str:
    """从 pyproject.toml 获取版本号"""
    pyproject = Path(__file__).parent / "awiki-info" / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        for line in content.split("\n"):
            if line.startswith("version"):
                return line.split("=")[1].strip().strip('"')
    return "1.0.0"


def check_git_status() -> bool:
    """检查 git 状态"""
    success, output = run_command(["git", "status", "--porcelain"])
    if not success:
        print("❌ 无法检查 git 状态")
        return False

    if output.strip():
        print("⚠️  工作目录有未提交的更改：")
        print(output)
        response = input("是否继续？(y/N): ")
        if response.lower() != "y":
            return False

    return True


def create_package(version: str) -> Optional[Path]:
    """创建 skill 打包文件"""
    print(f"\n📦 创建 v{version} 打包文件...")

    # 创建 dist 目录
    dist_dir = Path(__file__).parent / "dist"
    dist_dir.mkdir(exist_ok=True)

    # 打包文件名
    package_name = f"awiki-info-v{version}.zip"
    package_path = dist_dir / package_name

    # 要打包的文件（源路径 → 包内路径）
    files_to_package = [
        ("awiki-info/SKILL.md", "awiki-info/SKILL.md"),
        ("awiki-info/pyproject.toml", "awiki-info/pyproject.toml"),
        ("awiki-info/install_dependencies.py", "awiki-info/install_dependencies.py"),
        ("awiki-info/uv.lock", "awiki-info/uv.lock"),
        ("awiki-info/scripts/__init__.py", "awiki-info/scripts/__init__.py"),
        ("awiki-info/scripts/mcp_client.py", "awiki-info/scripts/mcp_client.py"),
        ("awiki-info/scripts/get_daily_summary.py", "awiki-info/scripts/get_daily_summary.py"),
        ("awiki-info/scripts/search_activities.py", "awiki-info/scripts/search_activities.py"),
        ("awiki-info/references/mcp-api.md", "awiki-info/references/mcp-api.md"),
        ("README.md", "awiki-info/README.md"),
        ("LICENSE", "awiki-info/LICENSE"),
        ("INSTALL.md", "awiki-info/INSTALL.md"),
    ]

    # 创建 zip 文件
    root = Path(__file__).parent
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_path, arc_path in files_to_package:
            full_path = root / src_path
            if full_path.exists():
                zf.write(full_path, arc_path)
                print(f"  ✓ {arc_path}")
            else:
                print(f"  ⚠️  跳过不存在的文件: {src_path}")

    print(f"\n✅ 打包完成: {package_path}")
    return package_path


def create_git_tag(version: str) -> bool:
    """创建 git tag"""
    tag_name = f"v{version}"

    # 检查 tag 是否已存在
    success, output = run_command(["git", "tag", "-l", tag_name])
    if success and tag_name in output:
        print(f"⚠️  Tag {tag_name} 已存在")
        response = input("是否删除并重新创建？(y/N): ")
        if response.lower() == "y":
            run_command(["git", "tag", "-d", tag_name])
            run_command(["git", "push", "origin", f":refs/tags/{tag_name}"], check=False)
        else:
            return False

    # 创建 tag
    print(f"\n🏷️  创建 git tag: {tag_name}")
    success, output = run_command(
        ["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"]
    )

    if not success:
        print(f"❌ 创建 tag 失败: {output}")
        return False

    print(f"✅ Tag {tag_name} 创建成功")
    return True


def push_to_github(version: str, push_tag: bool = True) -> bool:
    """推送到 GitHub"""
    print("\n📤 推送到 GitHub...")

    # 推送代码
    success, output = run_command(["git", "push", "origin", "main"])
    if not success:
        print(f"❌ 推送失败: {output}")
        return False

    print("✅ 代码推送成功")

    # 推送 tag
    if push_tag:
        tag_name = f"v{version}"
        success, output = run_command(["git", "push", "origin", tag_name])
        if not success:
            print(f"❌ Tag 推送失败: {output}")
            return False
        print(f"✅ Tag {tag_name} 推送成功")

    return True


def create_github_release(version: str, package_path: Path) -> bool:
    """创建 GitHub release (需要 gh CLI)"""
    print("\n🚀 创建 GitHub Release...")

    # 检查 gh CLI 是否安装
    if not shutil.which("gh"):
        print("⚠️  未安装 gh CLI，跳过创建 release")
        print("提示：可通过 brew install gh 安装")
        return False

    tag_name = f"v{version}"
    release_notes = f"""# awiki-info Skill v{version}

AI 资讯聚合 Skill，通过 MCP 协议连接远程服务。

## 功能特性

- 获取 AI 领域每日新闻摘要
- 搜索 AI 相关活动和事件
- 基于 MCP Python SDK 实现
- 支持 streamable-http 传输协议

## 安装方法

1. 下载附件中的 zip 文件
2. 解压到 Claude Code skills 目录
3. 运行 `uv sync` 安装依赖

## 使用文档

详见 README.md 和 SKILL.md
"""

    # 创建 release
    cmd = [
        "gh",
        "release",
        "create",
        tag_name,
        str(package_path),
        "--title",
        f"awiki-info v{version}",
        "--notes",
        release_notes,
    ]

    success, output = run_command(cmd)
    if not success:
        print(f"❌ 创建 release 失败: {output}")
        return False

    print(f"✅ Release {tag_name} 创建成功")
    return True


def main():
    parser = argparse.ArgumentParser(description="打包并发布 awiki-info skill")
    parser.add_argument(
        "--skip-check", action="store_true", help="跳过 git 状态检查"
    )
    parser.add_argument(
        "--skip-tag", action="store_true", help="跳过创建 git tag"
    )
    parser.add_argument(
        "--skip-push", action="store_true", help="跳过推送到 GitHub"
    )
    parser.add_argument(
        "--skip-release", action="store_true", help="跳过创建 GitHub release"
    )
    parser.add_argument(
        "--version", type=str, help="指定版本号（默认从 pyproject.toml 读取）"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("awiki-info Skill 打包和发布工具")
    print("=" * 60)

    # 获取版本号
    version = args.version or get_version()
    print(f"\n📌 版本: {version}")

    # 检查 git 状态
    if not args.skip_check and not check_git_status():
        print("\n❌ 已取消")
        return 1

    # 创建打包文件
    package_path = create_package(version)
    if not package_path:
        return 1

    # 创建 git tag
    if not args.skip_tag:
        if not create_git_tag(version):
            print("\n⚠️  跳过 tag 创建")

    # 推送到 GitHub
    if not args.skip_push:
        if not push_to_github(version, push_tag=not args.skip_tag):
            return 1

    # 创建 GitHub release
    if not args.skip_release:
        create_github_release(version, package_path)

    print("\n" + "=" * 60)
    print("✅ 所有步骤完成！")
    print("=" * 60)
    print(f"\n打包文件位置: {package_path}")
    print(f"GitHub 仓库: https://github.com/AgentConnect/awiki-skills")

    return 0


if __name__ == "__main__":
    sys.exit(main())
