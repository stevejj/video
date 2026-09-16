"""Nano Banana(Gemini 이미지 API) 한 장 생성 + 비용 기록.

사용:
  python3 tools/nb_generate.py --id P-1 --out assets/characters/parts/feet_sheet.png \
      --prompt-file /path/prompt.txt --ref a.png --ref b.png --ratio 3:1 --size 1K [--model gemini-3.1-flash-image]

- API 키는 환경변수 GEMINI_API_KEY 또는 저장소 루트 .env(GEMINI_API_KEY=...)에서 읽는다. 키를 코드·문서에 넣지 않는다.
- 호출마다 outputs/nb_log.jsonl 에 id, model, size, ratio, refs, prompt, usage, 추정 비용(USD·KRW)을 기록한다.
- 한 번 실행 = 이미지 1장. 배치는 이 스크립트를 여러 번 부른다(사용자 승인 후).
"""
import argparse, base64, json, os, sys, time, pathlib, datetime

PRICE_USD = {  # 출력 이미지 1장 단가 (ai.google.dev/gemini-api/docs/pricing, 2026-09-16 확인)
    "gemini-3.1-flash-image": {"0.5K": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151},
    "gemini-3.1-flash-lite-image": {"1K": 0.0336},
    "gemini-3-pro-image": {"1K": 0.134, "2K": 0.134, "4K": 0.24},
}
INPUT_USD_PER_MTOK = {"gemini-3.1-flash-image": 0.50, "gemini-3.1-flash-lite-image": 0.25, "gemini-3-pro-image": 2.00}
KRW_PER_USD = float(os.environ.get("KRW_PER_USD", "1400"))


def load_key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        env = pathlib.Path(__file__).resolve().parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("GEMINI_API_KEY 가 없습니다 (환경변수 또는 .env)")
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--ratio", default="9:16")
    ap.add_argument("--size", default="2K")
    ap.add_argument("--model", default="gemini-3.1-flash-image")
    a = ap.parse_args()

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=load_key())
    prompt = pathlib.Path(a.prompt_file).read_text()
    parts = [types.Part.from_text(text=prompt)]
    for r in a.ref:
        data = pathlib.Path(r).read_bytes()
        mime = "image/png" if r.lower().endswith(".png") else "image/jpeg"
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))

    cfg = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=a.ratio, image_size=a.size),
    )
    t0 = time.time()
    resp = client.models.generate_content(model=a.model, contents=parts, config=cfg)
    dt = time.time() - t0

    img_bytes = None
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            img_bytes = p.inline_data.data
            break
    if img_bytes is None:
        sys.exit("응답에 이미지가 없습니다: " + str(resp)[:500])
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img_bytes)

    usage = getattr(resp, "usage_metadata", None)
    in_tok = getattr(usage, "prompt_token_count", None) if usage else None
    out_usd = PRICE_USD.get(a.model, {}).get(a.size)
    in_usd = (in_tok or 0) / 1e6 * INPUT_USD_PER_MTOK.get(a.model, 0)
    total_usd = (out_usd or 0) + in_usd
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"), "id": a.id, "model": a.model,
        "size": a.size, "ratio": a.ratio, "refs": a.ref, "out": str(out), "prompt_file": a.prompt_file,
        "input_tokens": in_tok, "cost_usd": round(total_usd, 4), "cost_krw": round(total_usd * KRW_PER_USD),
        "seconds": round(dt, 1),
    }
    log = pathlib.Path("outputs/nb_log.jsonl"); log.parent.mkdir(exist_ok=True)
    with log.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    cum = sum(json.loads(l)["cost_krw"] for l in log.read_text().splitlines() if l.strip())
    print(json.dumps(rec, ensure_ascii=False))
    print(f"누적 비용: 약 {cum}원")


if __name__ == "__main__":
    main()
