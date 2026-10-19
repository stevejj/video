#!/usr/bin/env python3
"""박수 '짝' 합성(무료): 여러 겹의 짧은 노이즈 버스트 + 대역 강조.
사용: python3 tools/sfx_clap.py outputs/ep06/sfx/clap.wav
"""
import sys, wave
import numpy as np

SR = 44100


def main():
    rng = np.random.default_rng(7); out = np.zeros(int(SR * 0.3))
    for k, ofs in enumerate([0, 0.006, 0.011, 0.018]):  # 손바닥이 겹쳐 닿는 미세한 시차
        n = int(SR * 0.12); x = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * (0.012 if k < 3 else 0.04)))
        s = int(SR * ofs); out[s:s + n] += x * (1.0 if k < 3 else 0.6)
    # 1~3 kHz 강조: 간단한 2차 차분 + 원본 혼합
    out = 0.6 * out + 0.4 * np.diff(out, prepend=0) * 4
    out = out / np.abs(out).max() * 0.8
    with wave.open(sys.argv[1], 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    print('saved', sys.argv[1])


if __name__ == '__main__':
    main()
