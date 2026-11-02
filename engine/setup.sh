#!/bin/bash
# Prepara el entorno: voz gratis (edge-tts) y confianza en el proxy.
set -e
if ! command -v edge-tts >/dev/null; then
  NO_PROXY= no_proxy= pip install --break-system-packages -q edge-tts
fi
C=$(python3 -c "import certifi;print(certifi.where())")
if [ -f /root/.ccr/ca-bundle.crt ] && ! grep -q "AGENTPROXY-CA-ADDED" "$C"; then
  { echo "# AGENTPROXY-CA-ADDED"; cat /root/.ccr/ca-bundle.crt; } >> "$C"
fi
node -e "require('playwright')" && echo "setup ok"
