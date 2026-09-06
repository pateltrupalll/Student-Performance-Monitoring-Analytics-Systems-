import os


class Config:
    SECRET_KEY = 'your-secret-key-here-12345'

    # PostgreSQL Configuration - CHANGE THESE!
    DB_USER = 'postgres'  # Your PostgreSQL username
    DB_PASSWORD = '1234'  # Your PostgreSQL password
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'student_performance'

    # Database connection string
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOGIN_VIEW = 'login'