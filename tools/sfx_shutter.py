#!/usr/bin/env python3
"""폰 카메라 셔터 '찰칵' 합성(무료): 짧은 노이즈 클릭 두 번 + 고역 필터.
사용: python3 tools/sfx_shutter.py outputs/ep05/sfx/shutter.wav
"""
import sys, wave
import numpy as np

SR = 44100


def click(n_ms, decay_ms, seed):
    n = int(SR * n_ms / 1000); rng = np.random.default_rng(seed)
    x = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * decay_ms / 1000))
    return np.diff(x, prepend=0)  # 1차 미분 = 간단한 고역 강조


def main():
    out = np.zeros(int(SR * 0.25))
    a = click(30, 4, 1); b = click(40, 6, 2) * 0.8
    out[:len(a)] += a; s = int(SR * 0.07); out[s:s + len(b)] += b
    out = out / np.abs(out).max() * 0.8
    with wave.open(sys.argv[1], 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    print('saved', sys.argv[1])


if __name__ == '__main__':
    main()
