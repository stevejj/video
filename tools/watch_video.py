#!/usr/bin/env python3
"""유튜브 영상 소리 분석: Gemini가 URL을 직접 시청. 무료 등급 키(GEMINI_API_KEY_FREE)만 사용 → 0원.
사용: python3 tools/watch_video.py <youtube_url> <out.md>"""
import json,urllib.request,sys,time
k=[l.split('=',1)[1].strip() for l in open('/home/user/video/.env') if l.startswith('GEMINI_API_KEY_FREE=')][0]
url,out=sys.argv[1],sys.argv[2]
Q="""이 유튜브 쇼츠의 **소리**를 전문 사운드 디자이너처럼 분석해 주세요. 영상 비율·화면 구성은 다루지 말고 음성·효과음·배경음만 다룹니다. 한국어로, 아래 번호 순서대로, 타임스탬프(초)를 붙여 구체적으로 답하세요.

1. 대사 전체 스크립트: 시작 초, 화자(캐릭터 구분: 예 햄찌/팀장/동료), 대사 원문. 비명·한숨·웃음 같은 목소리 리액션도 [비명] 식으로 별도 줄로.
2. 음성 특징(화자별): 음높이 인상(매우 높음/높음/보통/낮음), 배속·피치업한 흔적이 있는지(목소리가 빨라지고 얇아진 "칩멍크" 질감), 말 속도(빠름/보통/느림), 전달 방식(무표정 낭독인지 감정 연기인지), 문장 끝 억양(올림/내림/툭 떨어짐), 발음 또렷함, TTS(합성음) 느낌 정도, 화자들 사이 음색 대비.
3. 감정 표현 방법: 목소리 톤을 바꿔서인지, 말버릇(반복·추임새·늘리기·더듬기)으로인지, 효과음으로인지. 예시를 타임스탬프와 함께.
4. 효과음 목록: 초, 종류(예: 띠용/쿵/반짝/삐/발소리/문/알림음), 만화적인지 사실적인지, 상대 음량(크다/보통/작다), 어떤 순간(표정 변화/컷 전환/펀치라인)에 붙었는지. 총 개수와 평균 간격.
5. 배경음악: 있는지, 어떤 장르·분위기·템포(BPM 추정), 보컬 유무, 시작·끝 초, 대사가 나올 때 음악이 작아지는지(더킹), 대사 대비 음량 인상, 곡이 바뀌는지.
6. 환경음(방·거리·사무실 소리)이 있는지와 음량.
7. 믹스 균형: 대사 : 효과음 : 음악 : 환경음의 상대적 크기를 1~10으로.
8. 무대사 구간(2초 이상): 시작~끝 초와 그 동안 무슨 소리가 채우는지.
9. 이 영상의 소리에서 "이 채널답다"고 느껴지는 규칙 5가지.
확실하지 않은 항목은 "불확실"이라고 표시하세요."""
body={"contents":[{"parts":[{"file_data":{"file_uri":url}},{"text":Q}]}],
      "generationConfig":{"temperature":0.2,"maxOutputTokens":8192}}
for model in ["gemini-3.7-flash","gemini-3.8-flash","gemini-2.5-pro","gemini-2.5-flash"]:
    r=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),headers={"x-goog-api-key":k,"Content-Type":"application/json"})
    try:
        t=time.time(); j=json.load(urllib.request.urlopen(r,timeout=600))
        txt=''.join(p.get('text','') for p in j['candidates'][0]['content']['parts'])
        open(out,'w').write(f"# model: {model}\n# url: {url}\n\n"+txt)
        print(f"ok {model} {len(txt)} chars {time.time()-t:.0f}s"); break
    except urllib.error.HTTPError as e:
        print(model,'HTTP',e.code,e.read()[:300].decode()); continue
    except Exception as e:
        print(model,'err',str(e)[:200]); continue
