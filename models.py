from sqlalchemy import ForeignKey, Column, String, INTEGER, DateTime, Float, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
import bcrypt, re

Base = declarative_base()

class Register(Base):
    __tablename__ = 'register'

    user_name = Column(String, primary_key=True)
    roll_no = Column(INTEGER, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    college = Column(String, nullable=False)
    email = Column(String, unique=True)
    password = Column(String(60), nullable=False)

    def __init__(self, user_name, roll_no, first_name, last_name, college, email, password):

        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password, salt)

        self.user_name = user_name
        self.roll_no = roll_no
        self.first_name = first_name
        self.last_name = last_name
        self.college = college
        self.email = email
        self.password = hashed_pw

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
    problem_name = Column(String, unique=True)
    difficulty = Column(String, nullable=False)
    content = Column(TEXT, nullable=False)
    total_submissions = Column(INTEGER, default=0)
    correct_submissions = Column(INTEGER, default=0)
    tags = Column(String, nullable=False)

    def __init__(self, problem_id, problem_name, difficulty, content, tags):
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.difficulty = difficulty
        self.content = content
        self.tags = tags
        self.total_submissions = 0
        self.correct_submissions = 0

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
