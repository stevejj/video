#!/usr/bin/env python3
"""무료 누끼: ISNet(onnx)으로 이미지의 지정 영역에서 피사체 알파를 뽑는다.
사용: python3 tools/cutout.py --img IN.png --box x0 y0 x1 y1 --out OUT.png [--model isnet.onnx] [--mask-out MASK.png]
OUT = 원본 크기 RGBA(박스 밖 투명). 모델: rembg isnet-general-use.onnx(스크래치패드에 받아둠).
"""
import argparse
import numpy as np
import onnxruntime as ort
from PIL import Image


def alpha(img, model):
    s = ort.InferenceSession(model, providers=['CPUExecutionProvider'])
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
    a = ap.parse_args()
    im = Image.open(a.img).convert('RGBA')
    x0, y0, x1, y1 = a.box
    m = alpha(im.crop((x0, y0, x1, y1)), a.model)
    full = Image.new('L', im.size, 0); full.paste(m, (x0, y0))
    out = im.copy(); out.putalpha(full); out.save(a.out)
    if a.mask_out: full.save(a.mask_out)
    print('saved', a.out)


if __name__ == '__main__':
    main()
