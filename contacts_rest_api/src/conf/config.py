# from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str  
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

# import os
# print("Environment variables:", dict(os.environ))
settings = Settings()

# from pydantic import BaseSettings


# class Settings(BaseSettings):
#     sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@localhost:5432/postgres'
#     secret_key: str = 'secret_key'
#     algorithm: str = 'HS256'
#     mail_username: str = 'example@meta.ua'
#     mail_password: str = 'password'
#     mail_from: str = 'example@meta.ua'
#     mail_port: int = 465
#     mail_server: str = 'smtp.meta.ua'
#     redis_host: str = 'localhost'
#     redis_port: int = 6379
#     cloudinary_name: str = 'name'
#     cloudinary_api_key: int = 326488457974591
#     cloudinary_api_secret: str = 'secret'

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"


# settings = Settings()
