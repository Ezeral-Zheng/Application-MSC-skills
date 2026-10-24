#!/usr/bin/env python3
"""Validate Application-MSC Agent, skill, directory, and tool consistency."""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_DIR = VAULT_ROOT / "Application_System"
SCHEMA_PATH = SYSTEM_DIR / "config" / "directory_schema.json"
REPORT_DIR = SYSTEM_DIR / "reports"
SKILLS_DIR = SYSTEM_DIR / "skills"
AGENTS_PATH = VAULT_ROOT / "AGENTS.md"
README_PATH = SYSTEM_DIR / "README.md"

SKILL_NAME_RE = re.compile(r"^\s*-\s+[^：:]+[：:]\s*`([^`/]+)`\s*$", re.MULTILINE)
VERSION_RE = re.compile(r"(?:^|[-_ ])V(\d+)(?=[._ -]|$)", re.IGNORECASE)


@dataclass
class Finding:
    severity: str
    area: str
    path: str
    message: str
    fix: str


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(VAULT_ROOT))
    except ValueError:
        return str(path)


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def is_student_dir(path: Path, schema: dict[str, object]) -> bool:
    ignored = set(schema.get("ignored_root_dirs", []))
    if not path.is_dir() or path.name.startswith(".") or path.name in ignored:
        return False
    output_dirs = list((schema.get("output_dirs") or {}).keys())
    source_dirs = list(schema.get("source_material_dirs", []))
    spreadsheet_dirs = list(schema.get("spreadsheet_material_dirs", []))
    return any((path / name).is_dir() for name in output_dirs + source_dirs + spreadsheet_dirs)


def collect_findings() -> list[Finding]:
    schema = load_schema()
    findings: list[Finding] = []
    findings.extend(check_required_system_files())
    findings.extend(check_agent_skill_registry())
    findings.extend(check_skill_files(schema))
    findings.extend(check_student_dirs(schema))
    findings.extend(check_system_noise())
    findings.extend(check_docs_consistency(schema))
    return findings


def check_required_system_files() -> list[Finding]:
    findings: list[Finding] = []
    for path in [AGENTS_PATH, README_PATH, SCHEMA_PATH]:
        if not path.exists():
            findings.append(
                Finding("Error", "System", rel(path), "关键系统文件缺失。", "恢复该文件或从模板重新创建。")
            )
    return findings


def check_agent_skill_registry() -> list[Finding]:
    findings: list[Finding] = []
    agents_text = read_text(AGENTS_PATH)
    registry_text = extract_skill_registry_text(agents_text)
    declared = set(re.findall(r"`([a-z][a-z0-9-]+)`", registry_text))
    for skill_name in declared:
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.exists():
            findings.append(
                Finding(
                    "Error",
                    "Skill Registry",
                    rel(skill_path),
                    f"`AGENTS.md` 声明了 skill `{skill_name}`，但对应 `SKILL.md` 不存在。",
                    "创建该 skill，或从 `AGENTS.md` 中移除声明。",
                )
            )
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        name = skill_file.parent.name
        if name not in declared:
            findings.append(
                Finding(
                    "Warning",
                    "Skill Registry",
                    rel(skill_file),
                    f"存在 skill `{name}`，但未在 `AGENTS.md` 总控列表中声明。",
                    "若这是正式入口，将其加入 `AGENTS.md`；若只是实验 skill，移到非生产目录。",
                )
            )
    return findings


def extract_skill_registry_text(agents_text: str) -> str:
    marker = "根据任务调用对应专项 skill："
    start = agents_text.find(marker)
    if start == -1:
        return ""
    tail = agents_text[start:]
    end_match = re.search(r"\n\d+\.\s", tail)
    if not end_match:
        return tail
    return tail[: end_match.start()]


def check_skill_files(schema: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    forbidden_dirs = set(schema.get("forbidden_dirs", []))
    output_dirs = list((schema.get("output_dirs") or {}).keys())
    writing_skill_names = {
        "recommendation-letter-writer",
        "personal-statement-writer",
        "resume-writer",
        "resume-experience-writer",
        "application-revision",
    }
    docx_exception_skill_names = {"ps-word-export", "ps-narrative-matrix-pdf"}
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = read_text(skill_file)
        name = skill_file.parent.name
        for forbidden in forbidden_dirs:
            if forbidden in text:
                findings.append(
                    Finding(
                        "Error",
                        "Skill Rule",
                        rel(skill_file),
                        f"skill 内容仍提到禁用目录 `{forbidden}`。",
                        "改为正式输出目录，例如 `Recommendation_Letters/`、`Personal_Statement/`、`Resume/` 或 `Resume_Experience/`。",
                    )
                )
        if name not in docx_exception_skill_names and re.search(r"生成\s*`?\\.docx|输出\s*`?\\.docx|保存.*docx", text, flags=re.IGNORECASE):
            findings.append(
                Finding(
                    "Error",
                    "Skill Rule",
                    rel(skill_file),
                    "skill 可能仍要求生成 `.docx` 输出。",
                    "改为只输出 `.md`；原始 Word/PDF 仅作为转换来源或附件。",
                )
            )
        if name in writing_skill_names:
            if "Vn" not in text and "版本" not in text:
                findings.append(
                    Finding("Warning", "Skill Rule", rel(skill_file), "写作/修改类 skill 未明确版本规则。", "补充 Vn 版本规则。")
                )
            if "application-review" not in text and name != "application-revision":
                findings.append(
                    Finding(
                        "Warning",
                        "Skill Rule",
                        rel(skill_file),
                        "写作类 skill 未明确生成后调用 `application-review`。",
                        "补充生成后审查、Needs Fix 自动修稿、Blocked 停止规则。",
                    )
                )
            if name != "application-revision" and not any(out_dir in text for out_dir in output_dirs):
                findings.append(
                    Finding("Warning", "Skill Rule", rel(skill_file), "未发现正式输出目录说明。", "补充保存目录。")
                )
            if "阻塞条件" not in text and "## Blocking conditions" not in text:
                findings.append(
                    Finding("Warning", "Skill Rule", rel(skill_file), "缺少统一的 `阻塞条件` 小节。", "补充缺资料、事实冲突、工具失败等停止条件。")
                )
            if "最小输出" not in text and "## Output contract" not in text:
                findings.append(
                    Finding("Warning", "Skill Rule", rel(skill_file), "缺少统一的 `最小输出` 小节。", "补充任务完成后必须产生或更新的文件。")
                )
    return findings


def check_student_dirs(schema: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    forbidden_dirs = set(schema.get("forbidden_dirs", []))
    source_dirs = list(schema.get("source_material_dirs", []))
    spreadsheet_dirs = list(schema.get("spreadsheet_material_dirs", []))
    memory_dirs = list(schema.get("memory_dirs", []))
    output_dirs = list((schema.get("output_dirs") or {}).keys())
    support_files = list(schema.get("support_files", []))
    students = sorted([p for p in VAULT_ROOT.iterdir() if is_student_dir(p, schema)], key=lambda p: p.name)
    for student in students:
        for forbidden in forbidden_dirs:
            if (student / forbidden).exists():
                findings.append(
                    Finding(
                        "Error",
                        "Student Directory",
                        rel(student / forbidden),
                        f"学生目录中仍存在禁用草稿目录 `{forbidden}`。",
                        "迁移其中正式文档到对应输出目录后移除该目录。",
                    )
                )
        for directory in source_dirs + spreadsheet_dirs + memory_dirs + output_dirs:
            if not (student / directory).exists():
                findings.append(
                    Finding(
                        "Warning",
                        "Student Directory",
                        rel(student / directory),
                        "学生目录缺少标准目录。",
                        "运行 `python3 Application_System/tools/normalize_materials.py --student '<学生名>'` 初始化。",
                    )
                )
        for support_file in support_files:
            if not (student / support_file).exists():
                findings.append(
                    Finding(
                        "Warning",
                        "Student Support File",
                        rel(student / support_file),
                        "学生支持文件缺失。",
                        "运行资料标准化工具初始化，或从模板创建。",
                    )
                )
        for output_dir in output_dirs:
            folder = student / output_dir
            if not folder.exists():
                continue
            for path in folder.glob("*"):
                if path.is_file() and path.suffix.lower() != ".md":
                    findings.append(
                        Finding(
                            "Warning",
                            "Output Format",
                            rel(path),
                            "正式输出目录中存在非 Markdown 文件。",
                            "确认它是否为原始附件；若是附件，迁移到资料或附件目录。正式成稿只保留 `.md`。",
                        )
                    )
                if path.is_file() and path.suffix.lower() == ".md" and not VERSION_RE.search(path.name):
                    findings.append(
                        Finding(
                            "Warning",
                            "Version",
                            rel(path),
                            "正式输出 Markdown 未带 Vn 版本号。",
                            "如为正式成稿，按版本规则重命名；如为参考资料，移出正式输出目录。",
                        )
                    )
    return findings


def check_system_noise() -> list[Finding]:
    findings: list[Finding] = []
    noisy_paths = [SYSTEM_DIR / "tools" / "__pycache__"]
    if "Application_System/skills" not in registered_submodule_paths():
        noisy_paths.append(SKILLS_DIR / ".git")
    for path in noisy_paths:
        if path.exists():
            findings.append(
                Finding(
                    "Warning",
                    "System Hygiene",
                    rel(path),
                    "系统目录中存在缓存、嵌套仓库或非知识库运行文件。",
                    "确认无用后清理；若必须保留，加入说明或忽略规则。",
                )
            )
    return findings


def registered_submodule_paths() -> set[str]:
    gitmodules = VAULT_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return set()
    parser = configparser.ConfigParser()
    parser.read(gitmodules, encoding="utf-8")
    return {
        parser.get(section, "path").strip()
        for section in parser.sections()
        if parser.has_option(section, "path")
    }


def check_docs_consistency(schema: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    reports_readme = SYSTEM_DIR / "reports" / "README.md"
    text = read_text(reports_readme)
    for output_dir in (schema.get("output_dirs") or {}).keys():
        if output_dir not in text:
            findings.append(
                Finding(
                    "Warning",
                    "Documentation",
                    rel(reports_readme),
                    f"报告 README 未提到输出扫描目录 `{output_dir}`。",
                    "更新 reports README 的扫描范围说明。",
                )
            )
    return findings


def render(findings: list[Finding]) -> str:
    counts = {severity: sum(1 for item in findings if item.severity == severity) for severity in ["Error", "Warning", "Info"]}
    lines = [
        "# Application System Validation Report",
        "",
        f"- 生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Error：{counts['Error']}",
        f"- Warning：{counts['Warning']}",
        f"- Info：{counts['Info']}",
        "",
        "## 结果概览",
        "",
    ]
    if not findings:
        lines.append("- Pass：未发现系统一致性问题。")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Severity | Area | Path | Finding | Suggested Fix |")
    lines.append("|---|---|---|---|---|")
    for item in findings:
        lines.append(
            "| "
            + " | ".join(
                escape_cell(value)
                for value in [item.severity, item.area, item.path, item.message, item.fix]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def report_path(report_dir: Path = REPORT_DIR) -> Path:
    return report_dir / "System-Validation.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write report to Application_System/reports")
    args = parser.parse_args()

    findings = collect_findings()
    content = render(findings)
    if args.write:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = report_path()
        path.write_text(content, encoding="utf-8")
        print(path)
    else:
        print(content)
    return 1 if any(item.severity == "Error" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
