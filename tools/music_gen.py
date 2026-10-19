#!/usr/bin/env python3
"""ElevenLabs Music으로 BGM 후보 생성(유료 — 사용자 "진행" 후에만).
사용: python3 tools/music_gen.py --ep ep06 [--only name]
outputs/<ep>/bgm/requests.json: {"items":[{"name","prompt","length_ms"}]} → outputs/<ep>/bgm/<name>.mp3, 결과는 candidates.json.
이미 파일이 있으면 건너뜀(--only로 지정한 것만 다시 만듦). 자동 재시도 없음.
"""
import argparse, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--only', default='')
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import keys
    d = os.path.join(ROOT, f'outputs/{a.ep}/bgm'); R = json.load(open(os.path.join(d, 'requests.json')))
    only = set(x for x in a.only.split(',') if x)
    cp = os.path.join(d, 'candidates.json'); C = json.load(open(cp)) if os.path.exists(cp) else []
    for it in R['items']:
        if only and it['name'] not in only: continue
        out = os.path.join(d, f"{it['name']}.mp3")
        if os.path.exists(out) and it['name'] not in only:
            print(f"[{it['name']}] 있음, 건너뜀"); continue
        body = {'prompt': it['prompt'], 'music_length_ms': it['length_ms'], 'model_id': 'music_v1'}
        r = urllib.request.Request(API, data=json.dumps(body).encode(), headers={'xi-api-key': keys.get('ELEVENLABS_API_KEY'), 'Content-Type': 'application/json'})
        try:
            data = urllib.request.urlopen(r, timeout=300).read()
        except urllib.error.HTTPError as e:
            print(f"[{it['name']}] 실패 {e.code}: {e.read()[:300].decode()}"); continue
        open(out, 'wb').write(data)
        C = [c for c in C if c['name'] != it['name']] + [dict(it, result=f'ok {len(data)}B')]
        print(f"[{it['name']}] ok {len(data)}B")
    json.dump(C, open(cp, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
