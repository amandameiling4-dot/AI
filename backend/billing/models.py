from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class StripeCustomer(Base):
    __tablename__ = 'stripe_customers'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=False)
    user = relationship('User')


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=False)
    plan = Column(String)
    status = Column(String)
    current_period_end = Column(DateTime)


class UsageRecord(Base):
    __tablename__ = 'usage_records'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    tokens = Column(Integer, nullable=False)
    request_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class InvoiceRecord(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    stripe_invoice_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id'))
    amount_due = Column(Numeric)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)