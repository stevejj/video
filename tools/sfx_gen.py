#!/usr/bin/env python3
"""ElevenLabs 효과음 생성 — outputs/<ep>/sfx/requests.json 의 항목을 생성해 outputs/<ep>/sfx/el/<name>.mp3 로 저장.
사용: python3 tools/sfx_gen.py --ep ep02 [--only name1,name2]
requests.json: {"items":[{"name","prompt","duration","loop":false}]} ; 이미 파일이 있으면 건너뜀. 결과는 generated.json 에 기록.
"""
import argparse, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.elevenlabs.io/v1/sound-generation'


def key():
    for l in open(os.path.join(ROOT, '.env')):
        if l.startswith('ELEVENLABS_API_KEY='):
            return l.split('=', 1)[1].strip()
    raise SystemExit('.env 에 ELEVENLABS_API_KEY 없음')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    d = os.path.join(ROOT, f'outputs/{a.ep}/sfx'); os.makedirs(os.path.join(d, 'el'), exist_ok=True)
    R = json.load(open(os.path.join(d, 'requests.json')))
    only = set(x for x in a.only.split(',') if x)
    gp = os.path.join(d, 'el/generated.json')
    G = json.load(open(gp)) if os.path.exists(gp) else []
    for it in R['items']:
        if only and it['name'] not in only:
            continue
        out = os.path.join(d, f"el/{it['name']}.mp3")
        if os.path.exists(out) and it['name'] not in only:
            print(f"[{it['name']}] 있음, 건너뜀"); continue
        body = {'text': it['prompt'], 'model_id': 'eleven_text_to_sound_v2', 'duration_seconds': it['duration'],
                'prompt_influence': it.get('prompt_influence', 0.5), 'loop': bool(it.get('loop'))}
        r = urllib.request.Request(API + '?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                   headers={'xi-api-key': key(), 'Content-Type': 'application/json'})
        try:
            data = urllib.request.urlopen(r, timeout=120).read()
        except urllib.error.HTTPError as e:
            print(f"[{it['name']}] 실패 {e.code}: {e.read()[:200].decode()}"); continue
        open(out, 'wb').write(data)
        rec = dict(it); rec['file'] = os.path.relpath(out, ROOT); rec['result'] = f'ok {len(data)}B'
        G = [g for g in G if g['name'] != it['name']] + [rec]
        print(f"[{it['name']}] ok {len(data)}B  {it['prompt'][:60]}")
    json.dump(G, open(gp, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
