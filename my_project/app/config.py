import os
from dotenv import load_dotenv

load_dotenv()

# # AWS RDS PostgreSQL配置
# DB_CONFIG = {
#     "dbname": "test_db",
#     "user": "keyili",      # Make sure this matches the user you created
#     "password": "991030",  # Make sure this matches the password you set
#     "host": "localhost",
#     "port": "5432"
# }

# AI服务URL（在AWS上运行）
AI_SERVER_URL = os.getenv('AI_SERVER_URL', 'http://ai-server-production-b3f3.up.railway.app')

# Redis配置（用于Celery）
REDIS_URL = os.getenv('REDIS_URL', 'redis://yamabiko.proxy.rlwy.net:28289')



