#!/usr/bin/env python3
"""유튜브 영상 분석(장면·자막·대사·소리): Gemini가 URL을 직접 시청. 유료 키(GEMINI_API_KEY) 사용, 영상 30~60초 기준 몇십 원.
yt-dlp가 봇 확인에 막힐 때 쓴다. 사용: python3 tools/watch_youtube.py <youtube_url> <out.md>
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import keys
url, out = sys.argv[1], sys.argv[2]
Q = """이 유튜브 쇼츠를 영상 연출가처럼 분석해 주세요. 한국어로, 타임스탬프(초)를 붙여 빠짐없이.
1. 장면 표: 시작~끝 초 | 장소(구체적으로) | 등장인물·옷차림 | 카메라(와이드/클로즈업, 고정/이동) | 무슨 행동.
2. 화면 자막·대사 전체를 원문 그대로: 초 | 화자 | 대사(자막 글자 그대로). 괄호 속 상황 자막(예: (준비시간 30분 남음))도 따로 줄로.
3. 상단 고정 제목 글자, 하단 채널명 글자.
4. 음성: 실제 목소리가 있는지(TTS·성우), 화자별 목소리 인상, 말 속도.
5. 효과음·배경음악: 초, 종류, 분위기, 템포.
6. 웃음 포인트(펀치라인)가 어디인지, 왜 공감되는지.
불확실하면 "불확실"이라고 표시하세요."""
body = {"contents": [{"parts": [{"file_data": {"file_uri": url}}, {"text": Q}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192}}
for model in ["gemini-3.1-flash", "gemini-3-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
    r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                               data=json.dumps(body).encode(), headers={"x-goog-api-key": keys.get('GEMINI_API_KEY'), "Content-Type": "application/json"})
    try:
        t = time.time(); j = json.load(urllib.request.urlopen(r, timeout=600))
    except urllib.error.HTTPError as e:
        print(model, 'HTTP', e.code, e.read()[:200].decode()); continue
    txt = ''.join(p.get('text', '') for p in j['candidates'][0]['content']['parts'])
    u = j.get('usageMetadata', {})
    open(out, 'w').write(f"# model: {model}\n# url: {url}\n# usage: {json.dumps(u)}\n\n" + txt)
    print(f"ok {model} {len(txt)} chars {time.time() - t:.0f}s usage {u.get('promptTokenCount')} in / {u.get('candidatesTokenCount')} out"); break
