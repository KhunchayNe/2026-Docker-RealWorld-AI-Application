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


# 1. สร้างข้อมูลตัวอย่าง
curl -X POST "http://localhost:8000/generate-sample-data"

# 2. Train model
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "retrain": true}'

# 3. ทำนายราคา 7 วัน
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "horizon": 7}'

# 4. ค้นหาราคาใกล้เคียง
curl "http://localhost:8000/search?price=32.5&fuel_type=diesel&limit=5"

# 5. ดูราคาล่าสุด
curl "http://localhost:8000/prices/latest"



# 1. โหลดข้อมูลจาก EPPO
curl -X POST "http://localhost:8000/upload-csv-url?url=https://catalog.eppo.go.th/dataset/b15f2fe3-14f0-4de5-b90e-2a5b63b4e717/resource/7d56918d-adbf-42b7-bd36-e4b33d425027/download/dataset_11_86.csv"

curl -X POST "http://localhost:8000/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@oil_prices.csv"

# 2. ตรวจสอบว่ามีข้อมูลแล้ว
curl "http://localhost:8000/prices/latest"

# 3. Train model
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "retrain": false
  }'

# 4. ทำนายราคา
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "horizon": 7
  }'
