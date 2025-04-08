FROM python:3.10-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "fursphere_data_processing/PythonProject/my_project/ai_service/ai_server.py"]
