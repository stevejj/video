#!/usr/bin/env python3
"""ElevenLabs 대사 생성 — outputs/voice_profile.json 프로필로만 생성한다(에피소드 간 일관성).
사용: python3 tools/voice_gen.py --ep ep01 [--regen 9-02,9-03] [--candidates 3]
- 대사마다 seed 후보를 순서대로 생성해 길이가 max_len 안에 들어오는 첫 결과를 채택하고 seed를 프로필에 기록
- seed가 이미 기록된 대사는 그 seed로 1회만 생성(--regen 으로 지정한 컷만 다시 후보 탐색)
- dialogue_group 이 같은 대사들은 Text to Dialogue 로 한 번에 생성(주고받는 흐름 유지)
- 결과: outputs/<ep>/voice/lines/<cut>.mp3 (loudnorm 적용), 프로필의 lines[*].seed / .len 갱신
"""
import argparse, json, os, subprocess, sys, tempfile, urllib.request
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
PROF = os.path.join(ROOT, 'outputs/voice_profile.json')
API = 'https://api.elevenlabs.io'


def key():
    for l in open(os.path.join(ROOT, '.env')):
        if l.startswith('ELEVENLABS_API_KEY='):
            return l.split('=', 1)[1].strip()
    raise SystemExit('.env 에 ELEVENLABS_API_KEY 없음')


def post(path, body, out):
    r = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                               headers={'xi-api-key': key(), 'Content-Type': 'application/json'})
    for attempt in range(2):
        try:
            d = urllib.request.urlopen(r, timeout=120).read()
        except urllib.error.HTTPError as e:
            raise SystemExit(f'ElevenLabs {e.code}: {e.read()[:300].decode()}')
        if len(d) > 2000:
            break
        print('  빈 응답, 재시도')
    open(out, 'wb').write(d)


def duration(p):
    out = subprocess.run([FF, '-i', p], capture_output=True, text=True).stderr
    import re
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def trim(src, dst):
    """앞뒤 무음 제거(-45dB 기준, 앞 0.05s·뒤 0.15s 여유). v3 출력은 앞뒤에 0.2~0.5s 무음이 붙는다."""
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse")
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', src, '-af', af, '-c:a', 'libmp3lame', '-q:a', '2', dst], check=True)


MAX_TEMPO = 1.15


def loudnorm(src, dst, ln, pitch, tempo=1.0):
    af = f"loudnorm=I={ln['I']}:TP={ln['TP']}:LRA={ln['LRA']}"
    if tempo != 1.0:
        af = f"atempo={tempo:.4f}," + af
    if pitch:
        f = 2 ** (pitch / 12)
        af = f"asetrate=44100*{f:.5f},aresample=44100,atempo={1 / f:.5f}," + af
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', src, '-af', af, '-ar', '44100', '-c:a', 'libmp3lame', '-q:a', '2', dst], check=True)


def tts_text(P, line):
    if line.get('tag_override'):
        return line['tts']
    tag = P['tags'].get(line['expr'], '')
    return (tag + ' ' + line['tts']).strip()


def speed_for(P, line):
    long = len(line['tts'].split()) >= 2 or line['expr'] in ('04', '05', '06', '10', '11', '12')
    return P['speed']['long_or_sleepy'] if long else P['speed']['short']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True)
    ap.add_argument('--regen', default='')
    ap.add_argument('--candidates', type=int, default=3)
    a = ap.parse_args()
    P = json.load(open(PROF))
    lines = P['episodes'][a.ep]['lines']
    regen = set(x for x in a.regen.split(',') if x)
    outdir = os.path.join(ROOT, f'outputs/{a.ep}/voice/lines'); os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='voice_')
    seeds_all = P['candidate_seeds']

    # 1) 대화 그룹 먼저(Text to Dialogue)
    groups = {}
    for l in lines:
        if l.get('dialogue_group'):
            groups.setdefault(l['dialogue_group'], []).append(l)
    for g, ls in groups.items():
        fixed = all('seed' in l for l in ls) and not any(l['cut'] in regen for l in ls)
        seeds = [ls[0]['seed']] if fixed else seeds_all[:a.candidates]
        for seed in seeds:
            raw = os.path.join(tmp, f'{g}_{seed}.mp3')
            post(f'/v1/text-to-dialogue?output_format=mp3_44100_128',
                 {'inputs': [{'text': tts_text(P, l), 'voice_id': P['voices'][l['speaker']]} for l in ls],
                  'model_id': P['model_id'], 'seed': seed,
                  'settings': {'stability': P['voice_settings']['stability'], 'use_speaker_boost': True}}, raw)
            if duration(raw) <= 0:
                print(f'[{g}] seed {seed}: 빈 응답, 다음 seed'); continue
            trim(raw, raw + '.t.mp3'); raw = raw + '.t.mp3'
            d = duration(raw); limit = sum(l['max_len'] for l in ls)
            print(f'[{g}] seed {seed}: {d:.2f}s (한도 {limit:.1f}s)')
            if d <= limit or seed == seeds[-1]:
                dst = os.path.join(outdir, f'{"+".join(l["cut"] for l in ls)}.mp3')
                loudnorm(raw, dst, P['loudnorm'], P['pitch_semitones'])
                for l in ls:
                    l['seed'] = seed; l['len'] = round(d, 2); l['file'] = os.path.relpath(dst, ROOT)
                break

    # 2) 단독 대사: 후보 중 한도 안 첫 결과, 없으면 가장 짧은 결과. 한도 초과는 atempo(≤1.15)로 맞춤
    for l in lines:
        if l.get('dialogue_group'):
            continue
        fixed = 'seed' in l and l['cut'] not in regen
        if fixed and l.get('file') and os.path.exists(os.path.join(ROOT, l['file'])) and not l.get('over'):
            continue
        seeds = [l['seed']] if fixed else seeds_all[:a.candidates]
        best = None
        for seed in seeds:
            raw = os.path.join(tmp, f'{l["cut"]}_{seed}.mp3')
            post(f'/v1/text-to-speech/{P["voices"][l["speaker"]]}?output_format=mp3_44100_128',
                 {'text': tts_text(P, l), 'model_id': P['model_id'], 'language_code': 'ko', 'seed': seed,
                  'voice_settings': dict(P['voice_settings'], speed=speed_for(P, l))}, raw)
            if duration(raw) <= 0:
                print(f'[{l["cut"]}] seed {seed}: 빈 응답, 다음 seed'); continue
            trim(raw, raw + '.t.mp3'); raw = raw + '.t.mp3'
            d = duration(raw)
            print(f'[{l["cut"]}] {tts_text(P, l)!r} seed {seed}: {d:.2f}s (한도 {l["max_len"]}s)')
            if best is None or d < best[1]:
                best = (seed, d, raw)
            if d <= l['max_len']:
                break
        if best is None:
            print(f'[{l["cut"]}] 실패: 유효한 응답 없음'); continue
        seed, d, raw = best
        tempo = 1.0
        if d > l['max_len']:
            tempo = min(d / l['max_len'], MAX_TEMPO)
        dst = os.path.join(outdir, f'{l["cut"]}.mp3')
        loudnorm(raw, dst, P['loudnorm'], P['pitch_semitones'], tempo)
        l['seed'] = seed; l['len_raw'] = round(d, 2); l['tempo'] = round(tempo, 3)
        l['len'] = round(duration(dst), 2); l['file'] = os.path.relpath(dst, ROOT)
        l['over'] = l['len'] > l['max_len'] + 0.05
        if tempo > 1.0:
            print(f'    → atempo {tempo:.3f} 적용, 최종 {l["len"]:.2f}s' + (' (여전히 초과: 컷 길이 조정 필요)' if l['over'] else ''))
    json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)
    print('프로필 갱신:', PROF)


if __name__ == '__main__':
    main()
