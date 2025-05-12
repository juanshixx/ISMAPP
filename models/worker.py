"""
Modelo para representar a los trabajadores en ISMAPP.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Worker(Base):
    """Modelo que representa a un trabajador de la empresa."""
    
    __tablename__ = 'workers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    rut = Column(String(20), nullable=False, unique=True)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    position = Column(String(100))  # Cargo
    department = Column(String(100))  # Departamento
    contract_type = Column(String(50))  # NUEVO: Tipo de contrato (por día, producción o contrato)
    hire_date = Column(Date)  # Fecha de contratación
    salary = Column(Float)  # Salario o remuneración
    is_active = Column(Boolean, default=True)
    notes = Column(String(500))
    
    # Datos bancarios
    bank_name = Column(String(100))  # Mantener para compatibilidad con versiones anteriores
    account_type = Column(String(50))  # Mantener para compatibilidad con versiones anteriores
    account_number = Column(String(50))  # Mantener para compatibilidad con versiones anteriores
    account_holder = Column(String(100))  # Mantener para compatibilidad con versiones anteriores
    account_holder_rut = Column(String(20))  # Mantener para compatibilidad con versiones anteriores
    
    # Relación con cuentas bancarias
    bank_accounts = relationship("BankAccount", back_populates="worker", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Worker(name='{self.name}', position='{self.position}')>"


class BankAccount(Base):
    """Modelo que representa una cuenta bancaria de un trabajador."""
    
    __tablename__ = 'worker_bank_accounts'
    
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=False)
    worker = relationship("Worker", back_populates="bank_accounts")
    
    is_primary = Column(Boolean, default=False)  # Indica si es la cuenta principal
    bank_name = Column(String(100))
    account_type = Column(String(50))
    account_number = Column(String(50))
    account_holder = Column(String(100))
    account_holder_rut = Column(String(20))
    
    def __repr__(self):
        return f"<BankAccount(bank='{self.bank_name}', number='{self.account_number}')>"