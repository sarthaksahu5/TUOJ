from sqlalchemy import ForeignKey, Column, String, INTEGER, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
import re

Base = declarative_base()

class Register(Base):
    __tablename__ = 'register'

    user_name = Column(String, primary_key=True)
    roll_no = Column(INTEGER, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    college = Column(String, nullable=False)
    email = Column(String, unique=True)

    def __init__(self, user_name, roll_no, first_name, college, email):
        self.user_name = user_name
        self.roll_no = roll_no
        self.first_name = first_name
        self.last_name = last_name
        self.college = college
        self.email = email

    def valid_email(email):
        if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
            return False
        return True

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

    def __init__(self, user_name, city, CTE=0, TLE=0, SIGSEGV=0, WA=0, Correct_Answer=0):
        self.user_name = user_name
        self.city = city
        self.CTE = CTE
        self.TLE = TLE
        self.SIGSEGV = SIGSEGV
        self.WA = WA
        self.Correct_Answer = Correct_Answer

class Problem(Base):
    __tablename__ = 'problem'

    problem_id = Column(String, primary_key=True)
    difficulty = Column(String, nullable=False)
    tags = Column(String, nullable=False)

    def __init__(self):
        self.problem_id = problem_id
        self.difficulty = difficulty
        self.tags = tags

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

    def __init__(self, user_name, problem_id, status):
        self.user_name = user_name
        self.problem_id = problem_id
        self.status = status

engine = create_engine('sqlite:///tuoj.db')
Base.metadata.create_all(engine)
