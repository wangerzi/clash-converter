FROM python:3.11.11-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . .

EXPOSE 8501  # Streamlit UI port
EXPOSE 8000  # API port

CMD ["python3", "main.py"] 