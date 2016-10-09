from sqlalchemy import ForeignKey, Column, String, INTEGER, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


class Register(Base):
    __tablename__ = 'register'

    user_name = Column(String(50), primary_key=True)
    roll_no = Column(INTEGER, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    college = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)


class Profile(Base):
    __tablename__ = 'profile'

    uid = Column(INTEGER, autoincrement=True, primary_key=True)
    user_name = Column(String(50), ForeignKey('register.user_name'))
    register = relationship('Register')
    city = Column(String(50))
    CTE = Column(INTEGER, default=0)
    TLE = Column(INTEGER, default=0)
    SIGSEGV = Column(INTEGER, default=0)
    WA = Column(INTEGER, default=0)
    Correct_Answer = Column(INTEGER, default=0)


class Problem(Base):
    __tablename__ = 'problem'

    problem_id = Column(String(50), primary_key=True)
    difficulty = Column(String(50), nullable=False)
    tags = Column(String(50), nullable=False)


class Submission(Base):
    __tablename__ = 'submission'

    submission_no = Column(INTEGER, autoincrement=True, primary_key=True)
    user_name = Column(String(50), ForeignKey('register.user_name'))
    register = relationship(Register)
    problem_id = Column(String(50), ForeignKey('problem.problem_id'))
    problem = relationship(Problem)
    status = Column(String(50), nullable=False)
    submission_time = Column(DateTime, nullable=False, default=datetime.now())
    memory_used = (Float)


engine = create_engine('mysql+pymysql://root:@localhost/tuoj')
Base.metadata.create_all(engine)