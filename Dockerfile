# 使用官方 Python 镜像
FROM python:3.10-slim

# 安装编译工具（某些库依赖）
RUN apt-get update && apt-get install -y build-essential gcc

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 拷贝所有项目代码
COPY . .

# 默认运行命令（会被 Railway 的 Start Command 覆盖）
CMD ["python", "PythonProject/my_project/ai_service/ai_server.py"]
