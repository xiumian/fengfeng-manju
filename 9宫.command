#!/bin/zsh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
WEB_ROOT="$ROOT/assets/open-cowart-canvas"
PAGE="/nine-grid.html"
LOG_FILE="${TMPDIR:-/tmp}/nine-grid-workbench.log"
PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
URL="http://127.0.0.1:${PORT}${PAGE}"

cd "$WEB_ROOT"
python3 -m http.server "$PORT" --bind 127.0.0.1 >"$LOG_FILE" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
for _ in {1..50}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    if [ "${1:-}" != "--no-open" ]; then open "$URL"; fi
    echo "9宫工作台已启动：$URL"
    echo "关闭此终端窗口即可停止本地服务。"
    wait "$SERVER_PID"
    exit 0
  fi
  sleep 0.1
done

echo "启动失败，请查看日志：$LOG_FILE" >&2
exit 1
