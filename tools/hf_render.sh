#!/usr/bin/env bash
# HyperFrames 렌더 + v10 오디오 mux. 사용: tools/hf_render.sh <ep> <tag>  (예: ep01 v11)
set -e
EP=${1:-ep01}; TAG=${2:-v11}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
HFN=${HF_NODE_MODULES:-/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/hf/node_modules}
# 2026-10-24: PATH에 ffmpeg가 있으면(윈도우 PC) 그걸 쓰고, 없으면 예전 리눅스 컨테이너 경로.
if command -v ffmpeg >/dev/null 2>&1; then
  export HYPERFRAMES_FFMPEG_PATH=${HYPERFRAMES_FFMPEG_PATH:-$(command -v ffmpeg)}
  export HYPERFRAMES_FFPROBE_PATH=${HYPERFRAMES_FFPROBE_PATH:-$(command -v ffprobe)}
else
  export HYPERFRAMES_FFMPEG_PATH=${HYPERFRAMES_FFMPEG_PATH:-$HFN/ffmpeg-static/ffmpeg}
  export HYPERFRAMES_FFPROBE_PATH=${HYPERFRAMES_FFPROBE_PATH:-$HFN/ffprobe-static/bin/linux/x64/ffprobe}
fi
# CLI: external/hf-cli에 설치된 것이 있으면 그걸(버전 고정), 없으면 npx 최신.
HF_BIN="$ROOT/external/hf-cli/node_modules/.bin/hyperframes"; [ -x "$HF_BIN" ] || HF_BIN="npx -y hyperframes@latest"
python3 "$ROOT/tools/ep_to_hyperframes.py" --ep "$EP" --out "$ROOT/outputs/$EP/hf"
cd "$ROOT/outputs/$EP/hf"
$HF_BIN lint . | grep -E "error\(s\)"
$HF_BIN render . --fps 24 -o "$ROOT/outputs/$EP/hf/render_${TAG}_video.mp4" --quiet
AUD=${AUDIO_FROM:-$ROOT/outputs/$EP/roughcut/${EP}_roughcut_v10.mp4}
"$HYPERFRAMES_FFMPEG_PATH" -y -loglevel error -i "$ROOT/outputs/$EP/hf/render_${TAG}_video.mp4" -i "$AUD" -map 0:v -map 1:a -c copy -shortest "$ROOT/outputs/$EP/roughcut/${EP}_roughcut_${TAG}_hf.mp4"
echo "→ outputs/$EP/roughcut/${EP}_roughcut_${TAG}_hf.mp4"
