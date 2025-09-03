#!/usr/bin/env bash

set -e
PY_VERSION="3.11.0"

echo "[*] Installing build dependencies..."
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev git alsa-utils

echo "[*] Installing pyenv..."
if [ ! -d "$HOME/.pyenv" ]; then
  curl https://pyenv.run | bash
fi

SHELL_CONFIG="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
  SHELL_CONFIG="$HOME/.zshrc"
fi

if ! grep -q 'pyenv init' "$SHELL_CONFIG"; then
  cat <<'EOF' >>"$SHELL_CONFIG"

# >>> pyenv setup >>>
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
# <<< pyenv setup <<<
EOF
fi

echo "[*] Reloading shell config..."
source "$SHELL_CONFIG"

if ! pyenv versions --bare | grep -q "^$PY_VERSION$"; then
  echo "[*] Installing Python $PY_VERSION..."
  pyenv install "$PY_VERSION"
fi

echo "[*] Setting local Python $PY_VERSION..."
pyenv local "$PY_VERSION"

if [ ! -d ".venv" ]; then
  echo "[*] Creating virtual environment..."
  python -m venv .venv
fi

echo "[*] Activating virtual environment..."
source $HOME/'Project - ChronoLOG'/.venv/bin/activate

if [ -f "requirements.txt" ]; then
  echo "[*] Installing dependencies..."
  pip install --upgrade pip
  pip install -r requirements.txt
fi

echo ""
echo "🎉 Environment ready!"
python --version
pip list | grep -E 'mysql-connector-python|pydub|PySide6|pyttsx3|shiboken6'
echo ""
echo "👉 You are now inside the venv ('.venv')."
