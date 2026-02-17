python --version
# TensorFlow 2.18 รองรับ Python 3.9-3.12 เท่านั้น
# ถ้าใช้ Python 3.13+ จะติดตั้งไม่ได้


``` bash
brew install pyenv
```

``` bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc
# For zsh, also add this line for the virtualenv plugin (recommended)
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
```


## สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# อัพเดต pip
pip install --upgrade pip

# ติดตั้ง (เลือกอย่างใดอย่างหนึ่ง)
pip install -r requirements.txt          # TensorFlow version
pip install -r requirements-lite.txt    # Alternative version

# หรือติดตั้งทีละตัว
pip install fastapi uvicorn qdrant-client
pip install tensorflow==2.18.0
pip install sentence-transformers pandas scikit-learn

