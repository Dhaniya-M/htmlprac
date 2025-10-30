import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool = None

def init_pool(app=None):
    global _pool
    cfg = app.config if app is not None else current_app.config
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name=cfg.get('MYSQL_POOL_NAME', 'agri_pool'),
            pool_size=cfg.get('MYSQL_POOL_SIZE', 5),
            host=cfg.get('MYSQL_HOST'),
            user=cfg.get('MYSQL_USER'),
            password=cfg.get('MYSQL_PASSWORD'),
            database=cfg.get('MYSQL_DB'),
            autocommit=True,
        )

def get_conn():
    global _pool
    if _pool is None:
        # attempt to initialize from current_app if available
        try:
            init_pool()
        except Exception:
            raise RuntimeError('DB pool not initialized')
    return _pool.get_connection()
