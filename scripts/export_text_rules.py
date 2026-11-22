"""Write the five plain-text exports from an explicit current-rule allowlist."""
import argparse
import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = '01_video-prompt-template.txt'
SPECIALTY_ROOT = 'references/production-specialties'
COMBAT_SPECIALTY_APPENDICES = {
    'realistic-fight': 'choreography',
    'vfx-fight': 'effect-profiles',
    'impact-frame': 'frame-construction',
}


def combat_specialty_sources():
    for name, appendix in COMBAT_SPECIALTY_APPENDICES.items():
        yield f'{SPECIALTY_ROOT}/{name}/guide.md'
        yield f'{SPECIALTY_ROOT}/{name}/references/{appendix}.md'


EXPORTS = {
    TEMPLATE: ('references/video-prompt-template.txt',),
    '02_core-contracts-and-precreation.md': (
        'references/portable-text-usage.md',
        'SKILL.md',
        'references/routing.md',
        'references/project-contract.md',
        'references/specialty-selection.md',
        'references/creation-preparation.md',
        f'{SPECIALTY_ROOT}/director-handoff/prepare.md',
        'references/design-boundaries.md',
        'references/coverage-contract.md',
        'references/narrative-event-design.md',
        'references/dialogue-relationship-design.md',
        'references/character-prop-design.md',
        'references/scene-space-design.md',
        'references/art-style-material-design.md',
        'references/lighting-color-design.md',
    ),
    '03_rhythm-emotion-sound.md': (
        'references/scene-rhythm-planning.md',
        'references/shot-rhythm-planning.md',
        'references/emotion-performance-design.md',
        'references/microexpression-cues.md',
        'references/performance-camera-methods.md',
        f'{SPECIALTY_ROOT}/director-handoff/guide.md',
        f'{SPECIALTY_ROOT}/scene-storyboard/guide.md',
        f'{SPECIALTY_ROOT}/scene-storyboard/references/view-reconstruction.md',
        f'{SPECIALTY_ROOT}/emotion-expression/guide.md',
        f'{SPECIALTY_ROOT}/emotion-expression/references/cue-selection.md',
        'references/layered-sound-design.md',
    ),
    '04_combat-vfx-rules.md': (
        'references/move-vfx-design.md',
        'references/visual-fulfillment-examples.md',
        'references/vfx-techniques.md',
        'references/visual-impact-design.md',
        'references/combat-choice-and-speed.md',
        *combat_specialty_sources(),
        'references/打斗编排库/调用规则.md',
        'references/打斗编排库/索引.md',
        'references/招式特效库/调用规则.md',
        'references/招式特效库/表现与爽感规则.md',
        'references/招式特效库/索引.md',
    ),
    '05_modules-and-compile.md': (
        'references/modules/source.md',
        'references/modules/assets.md',
        'references/modules/action.md',
        'references/modules/camera.md',
        'references/modules/performance.md',
        'references/modules/vfx.md',
        'references/modules/sound.md',
        'references/modules/compile.md',
        'references/modules/validate.md',
        f'{SPECIALTY_ROOT}/director-handoff/compile-bridge.md',
        f'{SPECIALTY_ROOT}/director-handoff/review.md',
        'references/model-delivery.md',
        'references/prompt-backstage-checks.md',
    ),
}
DISALLOWED = {'_archive', 'archive', 'assets', 'scripts', 'tests', 'maintenance',
              'release-v8.2.0', 'examples', 'storyboard-prompter-v2.9'}
LEGACY = {'director-output-contract.md', 'shot-and-segment.md', 'emotion-closeup-conversion.md',
          'microexpression-prompt-templates.md', 'storyboard-generation.md', 'debugging-and-ui.md'}


# These nonessential references are explained in portable-text-usage.md.
# A new unclassified local link fails the export instead of silently assuming
# the reader has the repository.
OPTIONAL_DOCS = {
    'maintenance/change-control.md',
    'references/workbench-v8.md',
    'references/tool-interface.md',
    'references/method-evidence.md',
    'references/combat-vfx-evidence.md',
    'references/招式特效库/来源资料/小说战斗与宏大画面爽感执行规则_V1.0.md',
    f'{SPECIALTY_ROOT}/README.md',
}
OPTIONAL_INDEX = {
    'references/打斗编排库/索引.md': r'0[1-9]_.+\.md',
    'references/招式特效库/索引.md': r'(?:0[1-9]|1[0-8])_.+\.md',
}


def check_dependencies(sources):
    for source, data in sources.items():
        for url in re.findall(r'\]\(([^)]+)\)', data.decode('utf-8-sig')):
            if '://' in url or url.startswith('#'):
                continue
            path = url.split('#', 1)[0]
            target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
            if target in sources or target in OPTIONAL_DOCS:
                continue
            if (source in OPTIONAL_INDEX
                    and posixpath.dirname(target) == posixpath.dirname(source)
                    and re.fullmatch(OPTIONAL_INDEX[source], posixpath.basename(target))
                    and (ROOT / target).is_file()):
                continue
            raise ValueError(f'unclassified export dependency: {source} -> {target}')


def load(relative):
    rel = Path(relative)
    if (rel.is_absolute() or '..' in rel.parts or set(rel.parts) & DISALLOWED
            or rel.name in LEGACY | {'CHANGELOG.md', '9pic.md'} or rel.name.startswith('9宫')
            or rel.suffix not in {'.md', '.txt'}
            or (relative != 'SKILL.md' and rel.parts[0] != 'references')):
        raise ValueError(f'excluded export source: {relative}')
    path = ROOT / rel
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError(f'not a regular source in the current workspace: {relative}')
    data = path.read_bytes()
    text = data.decode('utf-8-sig', errors='strict')
    if text.startswith('> 历史资料：退出v8默认运行'):
        raise ValueError(f'archived source can not be exported: {relative}')
    if re.search(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]|data:[^\r\n;,]*;base64,'
                 rb'|[A-Za-z0-9+/_-]{120,}={0,2}|!\[[^\]\r\n]*\]\s*[\[(]|<(?:img|picture|svg)\b', data, re.I):
        raise ValueError(f'non-text or embedded payload: {relative}')
    return data


def assemble():
    sources = {path: load(path) for paths in EXPORTS.values() for path in paths}
    check_dependencies(sources)
    files = {}
    for name, paths in EXPORTS.items():
        if name == TEMPLATE:
            files[name] = sources[paths[0]]
        else:
            files[name] = b'\n\n'.join(f'===== {path} =====\n'.encode('utf-8') + sources[path] for path in paths)
    return files


def export(destination):
    payload = assemble()
    destination.mkdir()
    for name, data in payload.items():
        with (destination / name).open('xb') as f:
            f.write(data)
    verify(destination)


def verify(destination):
    payload = assemble()
    if {p.name for p in destination.iterdir()} != set(payload):
        raise ValueError(f'not exactly the five export files: {destination}')
    for name, data in payload.items():
        p = destination / name
        if not p.is_file() or p.is_symlink() or p.read_bytes() != data:
            raise ValueError(f'export differs from current source blocks: {p}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    (verify if args.verify else export)(args.destination)
    for name in EXPORTS:
        print(f'{(args.destination / name).resolve()} | {(args.destination / name).stat().st_size} bytes')


if __name__ == '__main__':
    main()
