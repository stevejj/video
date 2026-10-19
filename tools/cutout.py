#!/usr/bin/env python3
"""무료 누끼: ISNet(onnx)으로 이미지의 지정 영역에서 피사체 알파를 뽑는다.
사용: python3 tools/cutout.py --img IN.png --box x0 y0 x1 y1 --out OUT.png [--model isnet.onnx] [--mask-out MASK.png]
OUT = 원본 크기 RGBA(박스 밖 투명). 모델: rembg isnet-general-use.onnx(스크래치패드에 받아둠).
"""
import argparse
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_URL = 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx'


def ensure_model(path):
    """ISNet 모델이 없으면(컨테이너 초기화 등) 받아 둔다."""
    import os, urllib.request
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print('ISNet 모델 내려받는 중:', path); urllib.request.urlretrieve(MODEL_URL, path)
    return path


def alpha(img, model):
    s = ort.InferenceSession(ensure_model(model), providers=['CPUExecutionProvider'])
    x = np.asarray(img.convert('RGB').resize((1024, 1024), Image.LANCZOS)).astype(np.float32) / 255.0
    x = (x - 0.5) / 1.0
    o = s.run(None, {s.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-8)
    return Image.fromarray((o * 255).astype('uint8')).resize(img.size, Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--img'); ap.add_argument('--box', type=int, nargs=4); ap.add_argument('--out')
    ap.add_argument('--model', default='/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx')
    ap.add_argument('--mask-out')
    ap.add_argument('--gamma', type=float, default=1.0, help='추론용 이미지만 밝게(<1) — 어두운 털이 배경에 묻힐 때')
    ap.add_argument('--boost', type=float, default=1.0, help='알파 지수(<1이면 반투명 가장자리·날개를 진하게)')
    a = ap.parse_args()
    im = Image.open(a.img).convert('RGBA')
    x0, y0, x1, y1 = a.box
    crop = im.crop((x0, y0, x1, y1)).convert('RGB')
    if a.gamma != 1.0:
        crop = crop.point(lambda v: int(255 * (v / 255) ** a.gamma))
    m = alpha(crop, a.model)
    if a.boost != 1.0:
        m = m.point(lambda v: int(255 * (v / 255) ** a.boost))
    full = Image.new('L', im.size, 0); full.paste(m, (x0, y0))
    out = im.copy(); out.putalpha(full); out.save(a.out)
    if a.mask_out: full.save(a.mask_out)
    print('saved', a.out)


if __name__ == '__main__':
    main()
