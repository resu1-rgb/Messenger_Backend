import os
from dotenv import load_dotenv
from authx import AuthX, AuthXConfig

load_dotenv()

config = AuthXConfig(
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
    JWT_ALGORITHM=os.getenv("JWT_ALGORITHM"),
    JWT_TOKEN_LOCATION=["headers", "query"],
    JWT_QUERY_STRING_NAME="token",
)

auth = AuthX(config=config)