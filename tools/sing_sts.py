#!/usr/bin/env python3
"""원곡 노래 목소리를 캐릭터 목소리로 바꾸기(ep15 v2, 사용자 선택 2026-10-23: "원곡 노래 목소리만 바꾸기").
v1(sing.py: 말하기 녹음 + WORLD로 음정 입히기)은 사용자: "괴물이 말하는 것도 아니고" → 기계음이라 버림.
분리한 원곡 목소리를 줄마다 잘라 ElevenLabs Speech-to-Speech로 미순·창수 목소리로 바꾸고 같은 시각에 다시 놓는다.
음정·박자·숨은 원곡 그대로 남는다. 결과는 원곡 가수 노래를 바꾼 것이라 로컬에만(outputs/<ep>/sing/, gitignore).
사용: python3 tools/sing_sts.py --ep ep15 [--only 01,07] [--denoise]  → sing/sts/<id>_<sp>.wav, sing/sts_<sp>.wav, sing/sts_preview*.mp3
"""
import argparse, json, os, subprocess, sys, uuid, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import voice_gen as vg
import keys

SR = 44100
PAD = 0.15


def pcm(p, sr=SR):
    return np.frombuffer(subprocess.run([vg.FF, '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).copy()


def write_wav(p, y, sr=SR):
    import wave
    with wave.open(p, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())


def sts(src_wav, voice_id, out_mp3, denoise):
    b = '----' + uuid.uuid4().hex
    parts = [('audio', 'a.wav', open(src_wav, 'rb').read()), ('model_id', None, b'eleven_multilingual_sts_v2'),
             ('remove_background_noise', None, b'true' if denoise else b'false'),
             ('voice_settings', None, json.dumps({'stability': 0.5, 'similarity_boost': 0.9, 'style': 0.0, 'use_speaker_boost': True}).encode())]
    body = b''
    for name, fn, data in parts:
        body += f'--{b}\r\nContent-Disposition: form-data; name="{name}"'.encode()
        body += (f'; filename="{fn}"\r\nContent-Type: audio/wav\r\n\r\n' if fn else '\r\n\r\n').encode() + data + b'\r\n'
    body += f'--{b}--\r\n'.encode()
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128', data=body,
                               headers={'xi-api-key': keys.get('ELEVENLABS_API_KEY'), 'Content-Type': f'multipart/form-data; boundary={b}'})
    for k in range(4):
        try:
            open(out_mp3, 'wb').write(urllib.request.urlopen(r, timeout=180).read()); return
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503) or k == 3:
                raise SystemExit(f'STS {e.code}: {e.read()[:300]}')
            import time; time.sleep(4 + 4 * k)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--only', default=''); ap.add_argument('--denoise', action='store_true')
    a = ap.parse_args(); only = set(x for x in a.only.split(',') if x)
    B = os.path.join(ROOT, f'outputs/{a.ep}')
    P = json.load(open(vg.PROF))
    L = json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']
    SC = {l['id']: l for l in json.load(open(os.path.join(B, 'ref/score_best.json')))['lines']}
    voc = pcm(os.path.join(B, 'ref/sep/htdemucs/ref_audio/vocals.wav'))
    d = os.path.join(B, 'sing/sts'); os.makedirs(d, exist_ok=True)
    total = len(voc)
    tracks = {sp: np.zeros(total, np.float32) for sp in ('misun', 'changsu')}
    for i, l in enumerate(L):
        # 줄 구간: 악보의 첫 음절 ~ 마지막 음절 끝(없으면 가사 시각), 앞뒤 0.15s 여유. 다음 줄 시작을 넘지 않게
        s0 = SC[l['id']]['syl'][0]['on'] if l['id'] in SC else l['t'][0]
        s1 = SC[l['id']]['syl'][-1]['off'] if l['id'] in SC else l['t'][1]
        nxt = (SC[L[i + 1]['id']]['syl'][0]['on'] if L[i + 1]['id'] in SC else L[i + 1]['t'][0]) if i + 1 < len(L) else total / SR
        t0 = max(0.0, s0 - PAD); t1 = min(total / SR, s1 + 0.4, nxt - 0.02)
        seg = voc[int(t0 * SR):int(t1 * SR)]
        src = os.path.join(d, f'{l["id"]}_src.wav'); write_wav(src, seg)
        for sp in (['misun', 'changsu'] if l['sp'] == 'both' else [l['sp']]):
            out = os.path.join(d, f'{l["id"]}_{sp}.mp3')
            if (not only or l['id'] in only) and (not os.path.exists(out) or only):
                sts(src, P['voices'][sp], out, a.denoise)
                print('변환', l['id'], sp, f'{t0:.2f}~{t1:.2f}s')
            y = pcm(out)
            n = min(len(y), len(seg))
            f = int(0.03 * SR); env = np.ones(n); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
            i0 = int(t0 * SR); tracks[sp][i0:i0 + n] += y[:n] * env
            if abs(len(y) - len(seg)) > SR * 0.05:
                print(f'  ⚠ 길이 차이 {l["id"]} {sp}: 원곡 {len(seg) / SR:.2f}s → 변환 {len(y) / SR:.2f}s')
    for sp, y in tracks.items():
        write_wav(os.path.join(B, f'sing/sts_{sp}.wav'), y)
    print('트랙', [os.path.relpath(os.path.join(B, f'sing/sts_{sp}.wav'), ROOT) for sp in tracks])


if __name__ == '__main__':
    main()
