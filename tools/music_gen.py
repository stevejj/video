#!/usr/bin/env python3
"""ElevenLabs 음악 생성(배경음). 실제 곡은 저작권 때문에 쓰지 않고, 빠르기·분위기만 글로 설명해 새로 만든다.
사용: python3 tools/music_gen.py --out outputs/ep10/bgm/beat112.mp3 --seconds 22 --prompt "..."
결과는 같은 폴더 generated.json 에 기록. 이미 파일이 있으면 --force 없이는 건너뜀.
"""
import argparse, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.elevenlabs.io/v1/music'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--prompt', required=True); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    out = os.path.join(ROOT, a.out); os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and not a.force:
        print('있음, 건너뜀', a.out); return
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import keys
    body = {'prompt': a.prompt, 'music_length_ms': int(a.seconds * 1000), 'model_id': 'music_v1'}
    r = urllib.request.Request(API + '?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                               headers={'xi-api-key': keys.get('ELEVENLABS_API_KEY'), 'Content-Type': 'application/json'})
    try:
        data = urllib.request.urlopen(r, timeout=300).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f'실패 {e.code}: {e.read()[:300].decode()}')
    open(out, 'wb').write(data)
    gp = os.path.join(os.path.dirname(out), 'generated.json')
    G = json.load(open(gp)) if os.path.exists(gp) else []
    G = [g for g in G if g['file'] != a.out] + [{'file': a.out, 'seconds': a.seconds, 'prompt': a.prompt, 'result': f'ok {len(data)}B'}]
    json.dump(G, open(gp, 'w'), ensure_ascii=False, indent=1)
    print(f'ok {len(data)}B → {a.out}')


if __name__ == '__main__':
    main()
