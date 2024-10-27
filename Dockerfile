# 使用 Python 3.9 Alpine 版本作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到容器中
COPY requirements.txt .

# 安装依赖，添加 `--no-cache` 避免缓存
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录下的所有文件复制到容器的工作目录
COPY . /app

# 暴露应用运行时的端口
EXPOSE 34568


# 设置容器启动时执行的命令
CMD ["python", "app.py"]
