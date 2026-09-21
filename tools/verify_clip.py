"""Kling 클립 검수(06 B0~B4 수치 부분).
사용: python3 tools/verify_clip.py --cut 4-01 --clip outputs/ep01/4-01/clip_v1.mp4 [--start start_v1.png] [--end end_v1.png] [--beak x0,y0,x1,y1]
출력: outputs/ep01/<cut>/verify_v<n>/ 에 첫·끝·0.25s 샘플 프레임 + 대조 시트, 수치는 meta.json 'verify'에 기록.
"""
import argparse, json, os, pathlib, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
import imageio_ffmpeg

def frames_of(path, step=0.25):
    cap=cv2.VideoCapture(path); fps=cap.get(cv2.CAP_PROP_FPS) or 30; n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    allf=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        allf.append(f)
    cap.release()
    return allf, fps, (W,H)

def gray(im): return cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.int16)

def load_ref(p, size):
    im=cv2.cvtColor(np.array(Image.open(p).convert('RGB')),cv2.COLOR_RGB2BGR)
    return cv2.resize(im,size,interpolation=cv2.INTER_AREA)

def cam_motion(g0,g1):
    """배경 특징점 이동 중앙값(px). 캐릭터 영역 포함이라 상한 지표로만."""
    p0=cv2.goodFeaturesToTrack(g0.astype(np.uint8),300,0.01,8)
    if p0 is None: return None
    p1,st,_=cv2.calcOpticalFlowPyrLK(g0.astype(np.uint8),g1.astype(np.uint8),p0,None)
    d=np.linalg.norm((p1-p0).reshape(-1,2),axis=1)[st.ravel()==1]
    return float(np.median(d)) if len(d) else None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--cut',required=True); ap.add_argument('--clip',required=True)
    ap.add_argument('--start'); ap.add_argument('--end'); ap.add_argument('--beak',help='x0,y0,x1,y1 (클립 해상도 기준)'); ap.add_argument('--tag',default='v1')
    a=ap.parse_args()
    out=pathlib.Path(f'outputs/ep01/{a.cut}/verify_{a.tag}'); out.mkdir(parents=True,exist_ok=True)
    fr,fps,size=frames_of(a.clip); n=len(fr); dur=n/fps
    res={'fps':round(fps,2),'frames':n,'duration_s':round(dur,2),'size':size}
    step=max(1,int(round(fps*0.25))); idx=list(range(0,n,step));
    if idx[-1]!=n-1: idx.append(n-1)
    for i in idx: cv2.imwrite(str(out/f'f{i:04d}_{i/fps:.2f}s.png'),fr[i])
    # 1) 첫 프레임 vs 시작 이미지 / 끝 프레임 vs 끝 이미지
    for key,ref,fi in (('start',a.start,0),('end',a.end,n-1)):
        if ref and os.path.exists(ref):
            r=load_ref(ref,size); d=np.abs(gray(r)-gray(fr[fi]))
            res[f'{key}_vs_ref_meandiff']=round(float(d.mean()),2)
            res[f'{key}_vs_ref_bg_meandiff']=round(float(np.concatenate([d[:int(size[1]*0.12)].ravel(),d[int(size[1]*0.85):].ravel()]).mean()),2)
    # 2) 프레임 간 변화·배경 드리프트·카메라
    g=[gray(f) for f in fr]
    interframe=[float(np.abs(g[i]-g[i-1]).mean()) for i in range(1,n)]
    res['interframe_mean']=round(float(np.mean(interframe)),2); res['interframe_max']=round(float(np.max(interframe)),2)
    res['interframe_max_at_s']=round(float((int(np.argmax(interframe))+1)/fps),2)
    res['first_vs_last_meandiff']=round(float(np.abs(g[0]-g[-1]).mean()),2)
    bg=lambda x: np.concatenate([x[:int(size[1]*0.12)].ravel(),x[int(size[1]*0.85):].ravel()])
    res['bg_drift_first_last']=round(float(np.abs(bg(g[0])-bg(g[-1])).mean()),2)
    cm=[cam_motion(g[i-1],g[i]) for i in range(1,n,max(1,step))]
    cm=[c for c in cm if c is not None]; res['cam_motion_px_median']=round(float(np.median(cm)),2) if cm else None; res['cam_motion_px_max']=round(float(np.max(cm)),2) if cm else None
    # 3) 부리 영역 변화(지정 시)
    if a.beak:
        x0,y0,x1,y1=map(int,a.beak.split(','))
        series=[float(np.abs(g[i][y0:y1,x0:x1]-g[0][y0:y1,x0:x1]).mean()) for i in range(n)]
        res['beak_region_change_max']=round(max(series),2); res['beak_region_change_mean']=round(float(np.mean(series)),2)
    # 4) 대조 시트
    tiles=[cv2.resize(fr[i],(size[0]//4,size[1]//4)) for i in idx]
    cols=min(8,len(tiles)); rows=(len(tiles)+cols-1)//cols; tw,th=size[0]//4,size[1]//4
    sheet=np.full((rows*(th+4),cols*(tw+4),3),255,np.uint8)
    for k,t in enumerate(tiles):
        r,c=divmod(k,cols); sheet[r*(th+4):r*(th+4)+th, c*(tw+4):c*(tw+4)+tw]=t
        cv2.putText(sheet,f'{idx[k]/fps:.2f}s',(c*(tw+4)+4,r*(th+4)+18),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    cv2.imwrite(str(out/'sheet.png'),sheet)
    # meta 기록
    mp=pathlib.Path(f'outputs/ep01/{a.cut}/meta.json')
    m=json.load(open(mp)) if mp.exists() else {}
    m.setdefault('verify',{})[a.tag]=res; json.dump(m,open(mp,'w'),ensure_ascii=False,indent=1)
    print(json.dumps(res,ensure_ascii=False,indent=1)); print('sheet:',out/'sheet.png')
if __name__=='__main__': main()
