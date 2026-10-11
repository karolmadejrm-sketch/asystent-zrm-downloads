#!/usr/bin/env python3
"""Build update manifests from verified GitHub Release assets."""
import datetime
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

REPO = 'karolmadejrm-sketch/asystent-zrm-downloads'
BASE = 'https://pomoc-w-zrm.netlify.app'
OUTPUT = Path('updates')
HEX_SHA256 = re.compile(r'^sha256:([a-f0-9]{64})$', re.I)
VERSION = re.compile(r'(?<!\d)(\d+\.\d+\.\d+(?:-r\d+)?)', re.I)
PATTERNS = {
    'windows': re.compile(r'^Asystent[_-]ZRM[_-]Windows[_-].+\.zip$', re.I),
    'android': re.compile(r'^Asystent[_-]ZRM[_-]Android[_-].+\.apk$', re.I),
}

def github_releases():
    request = Request(
        f'https://api.github.com/repos/{REPO}/releases?per_page=100',
        headers={'Accept': 'application/vnd.github+json',
                 'User-Agent': 'Asystent-ZRM-releases-manifest/1.0'},
    )
    token = os.environ.get('GH_TOKEN', '')
    if token:
        request.add_header('Authorization', f'Bearer {token}')
    with urlopen(request, timeout=30) as response:
        values = json.load(response)
    if not isinstance(values, list):
        raise RuntimeError('Unexpected GitHub releases response')
    values = [x for x in values if not x.get('draft') and x.get('published_at')]
    return sorted(values, key=lambda x: x['published_at'], reverse=True)

def asset_for(releases, platform):
    for release in releases:
        tag = release.get('tag_name', '')
        if not re.fullmatch(r'v?\d+\.\d+\.\d+(?:[-.][\w.-]+)?', tag):
            continue
        candidates = []
        for a in release.get('assets', []):
            name, url = a.get('name', ''), a.get('browser_download_url', '')
            digest = HEX_SHA256.fullmatch(a.get('digest') or '')
            parsed = urlparse(url)
            if (not PATTERNS[platform].fullmatch(name) or
                a.get('state') != 'uploaded' or not digest or
                not isinstance(a.get('size'), int) or a['size'] <= 0 or
                parsed.scheme != 'https' or parsed.netloc != 'github.com' or
                not parsed.path.startswith(f'/{REPO}/releases/download/{tag}/')):
                continue
            version = VERSION.search(name)
            if version:
                candidates.append((a, version.group(1), digest.group(1).lower()))
        if candidates:
            a, version, digest = sorted(
                candidates, key=lambda x: x[0].get('updated_at', ''), reverse=True
            )[0]
            details = {
                'version': version,
                'build': tag,
                'description': release.get('name') or f'Asystent ZRM {tag}',
                'downloadUrl': f'{BASE}/updates/download/{quote(tag, safe="")}/{quote(a["name"], safe="")}',
                'sha256': digest,
                'bytes': a['size'],
                'prerelease': bool(release.get('prerelease')),
            }
            if platform == 'android':
                details['signature'] = 'verify-before-install'
            return details, release
    return None, None

def build_manifest(releases, channel):
    subset = releases if channel == 'beta' else [
        r for r in releases if not r.get('prerelease')
    ]
    windows, wr = asset_for(subset, 'windows')
    android, ar = asset_for(subset, 'android')
    if not windows and not android:
        return None
    newest = max((r for r in (wr, ar) if r), key=lambda x: x['published_at'])
    return {
        'schema': 'asystent-zrm-update-v1',
        'channel': channel,
        'publishedAt': datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec='seconds'),
        'releasePage': newest['html_url'],
        'channels': {'stable': {
            k: v for k, v in [('windows', windows), ('android', android)] if v
        }},
    }

def main():
    releases = github_releases()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for channel in ('stable', 'beta'):
        data = build_manifest(releases, channel)
        path = OUTPUT / f'{channel}.json'
        if not data:
            print(f'{channel}: no verified assets; not advertising downloads')
            continue
        if path.exists():
            try:
                old = json.loads(path.read_text(encoding='utf-8'))
                if ({k: v for k, v in old.items() if k != 'publishedAt'} ==
                    {k: v for k, v in data.items() if k != 'publishedAt'}):
                    print(f'{channel}: unchanged')
                    continue
            except (OSError, json.JSONDecodeError):
                pass
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8')
        print(f'{channel}: generated')

if __name__ == '__main__':
    main()
