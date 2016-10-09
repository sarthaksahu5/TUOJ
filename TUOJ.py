from sqlalchemy import ForeignKey, Column, String, INTEGER, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

class Register(Base):
    __tablename__ = 'register'

    user_name = Column(String, primary_key=True)
    roll_no = Column(INTEGER, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    college = Column(String, nullable=False)
    email = Column(String, unique=True)

class Profile(Base):
    __tablename__ = 'profile'

    uid = Column(INTEGER, autoincrement=True, primary_key=True)
    user_name = Column(String, ForeignKey('register.user_name'))
    register = relationship('Register')
    city = Column(String)
    CTE = Column(INTEGER, default=0)
    TLE = Column(INTEGER, default=0)
    SIGSEGV = Column(INTEGER, default=0)
    WA = Column(INTEGER, default=0)
    Correct_Answer = Column(INTEGER, default=0)

class Problem(Base):
    __tablename__ = 'problem'

    problem_id = Column(String, primary_key=True)
    difficulty = Column(String, nullable=False)
    tags = Column(String, nullable=False)

class Submission(Base):
    __tablename__ = 'submission'

    submission_no = Column(INTEGER, autoincrement=True, primary_key=True)
    user_name = Column(String, ForeignKey('register.user_name'))
    register = relationship(Register)
    problem_id = Column(String, ForeignKey('problem.problem_id'))
    problem = relationship(Problem)
    status = Column(String, nullable=False)
    submission_time = Column(DateTime, nullable=False, default=datetime.now())
    memory_used = (Float)

engine = create_engine('sqlite:///tuoj1.db')
Base.metadata.create_all(engine)