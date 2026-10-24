#!/usr/bin/env python3
"""Materialize the existing root skills in the workspace layout used by the agent."""
import argparse
import shutil
import tempfile
from pathlib import Path


def setup(root: Path, refresh: bool = False) -> int:
    sources = sorted(p.parent for p in root.glob('*/SKILL.md'))
    target = root / 'Application_System' / 'skills'
    marker = target / '.generated-by-setup'
    if target.exists():
        identical = all((target / p.relative_to(root)).is_file() and
                        (target / p.relative_to(root)).read_bytes() == p.read_bytes()
                        for s in sources for p in s.rglob('*') if p.is_file()
                        and '__pycache__' not in p.parts and p.name != '.DS_Store')
        if identical and sorted(p.name for p in target.iterdir() if p.is_dir()) == [s.name for s in sources]:
            print(f'Workspace ready: {len(sources)} skills (unchanged).')
            return 0
        if not refresh or not marker.exists():
            raise SystemExit('Existing skills differ or are not a generated copy. No files changed. '
                             'For a previously generated workspace, use --refresh to back it up and regenerate.')
        backup = Path(tempfile.mkdtemp(prefix='application-msc-skills-backup-')) / 'skills'
        shutil.move(str(target), backup)
        print(f'Previous generated skills backed up to {backup}')
    target.mkdir(parents=True, exist_ok=True)
    for source in sources:
        shutil.copytree(source, target / source.name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store', '.git'))
    marker.write_text('Generated from repository root skill directories. Edit those sources, then run setup_workspace.py --refresh.\n')
    for name in ('reports', 'indexes'):
        (root / 'Application_System' / name).mkdir(exist_ok=True)
    print(f'Workspace ready: {len(sources)} skills.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Back up and regenerate an existing generated skills copy')
    args = parser.parse_args()
    raise SystemExit(setup(Path(__file__).resolve().parent, args.refresh))
