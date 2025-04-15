from sqlalchemy.ext.declarative import declarative_base

# создаем базовый класс, от которого будут наследоваться все ORM-модели:
Base = declarative_base()

__all__ = ['Base']

