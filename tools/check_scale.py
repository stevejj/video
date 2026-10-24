"""스케일 검수 보조: 그리드 오버레이 + 지정 열(x)의 세로 에지 위치 출력.

사용: python3 tools/check_scale.py <image> [--cols 390,110,560,610] [--grid 50]
- <image>_grid.png 를 scratch에 저장(50px 격자). 눈으로 좌표를 읽는다.
- 각 열에 대해 밝기 변화가 큰 y 좌표를 출력한다. 물체의 위/아래 경계 후보.
비율 계산은 사람이 한다: 대상 높이 / 캐릭터 키(털뭉치 끝~발바닥). 바닥 접점은 같은 물체의 접점끼리 비교.
"""
import sys, argparse, pathlib
import numpy as np
from PIL import Image

ap=argparse.ArgumentParser(); ap.add_argument('image'); ap.add_argument('--cols',default=''); ap.add_argument('--grid',type=int,default=50); ap.add_argument('--thr',type=int,default=12)
a=ap.parse_args()
im=Image.open(a.image).convert('RGB'); arr=np.array(im).astype(int); H,W,_=arr.shape
g=arr.copy()
for y in range(0,H,a.grid): g[y,:,:]=[255,0,0]
for x in range(0,W,a.grid): g[:,x,:]=[0,255,0]
out=pathlib.Path(a.image).with_name(pathlib.Path(a.image).stem+'_grid.png'); Image.fromarray(g.astype(np.uint8)).save(out)
print('grid saved:',out,'size',W,H)
for c in [int(v) for v in a.cols.split(',') if v.strip()]:
    col=arr[:,c]; d=np.abs(np.diff(col,axis=0)).sum(axis=1); ys=np.where(d>a.thr)[0]
    runs=[]
    for y in ys:
        if runs and y-runs[-1][-1]<=3: runs[-1].append(y)
        else: runs.append([y])
    print(f'x={c}: edges at', [(r[0],r[-1]) if r[0]!=r[-1] else r[0] for r in runs])
