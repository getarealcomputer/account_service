import random
from enum import Enum as PyEnum
from datetime import datetime
from uuid import uuid4
from database import db, metadata

from sqlalchemy import Table, Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID


nasabah = Table(
    "nasabah",
    metadata,
    Column("id", UUID, primary_key=True, default=uuid4),
    Column("nama", String, nullable=False),
    Column("nik", String, nullable=False),
    Column("no_hp", String),
    Column("created_at", DateTime, nullable=False),
    UniqueConstraint("nik", name="nik_unique"),
    UniqueConstraint("no_hp", name="no_hp_unique")
)

rekening = Table(
    "rekening",
    metadata,
    Column("id", UUID, primary_key=True, default=uuid4),
    Column("nasabah_id", UUID, ForeignKey("nasabah.id"), nullable=False),
    Column("no_rekening", String, nullable=False),
    Column("saldo", Float, server_default="0"),
    Column("created_at", DateTime, nullable=False),
)


class TransactionType(PyEnum):
    TABUNG = "tabung"
    TARIK = "tarik"


transaksi = Table(
    "transaksi",
    metadata,
    Column("id", UUID, primary_key=True, default=uuid4),
    Column("rekening_id", UUID, ForeignKey("rekening.id"), nullable=False),
    Column("no_rekening", String, nullable=False),
    Column("nominal", Float, nullable=False),
    Column(
        "tipe_transaksi",
        Enum(TransactionType, name="tipe_transaksi"),
        nullable=False,
    ),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
)


class Nasabah:
    @classmethod
    async def get(self, id):
        query = nasabah.select().where(nasabah.c.id == id)
        return await db.fetch_one(query)

    @classmethod
    async def get_by_nik(self, nik):
        query = nasabah.select().where(nasabah.c.nik == nik)
        return await db.fetch_one(query)

    @classmethod
    async def get_by_no_hp(self, no_hp):
        query = nasabah.select().where(nasabah.c.no_hp == no_hp)
        return await db.fetch_one(query)

    @classmethod
    async def create(self, **data):
        data["id"] = uuid4()
        data["created_at"] = datetime.now()
        query = nasabah.insert().values(**data)
        await db.execute(query)
        return data["id"]


class Rekening:
    @classmethod
    async def get(self, no_rekening):
        query = rekening.select().where(rekening.c.no_rekening == no_rekening)
        return await db.fetch_one(query)

    @classmethod
    async def create(self, nasabah_id):
        print(nasabah_id)
        data = {
            "id": uuid4(),
            "nasabah_id": nasabah_id,
            "no_rekening": self().generate_valid_bank_account_number(length=12),
            "created_at": datetime.now(),
        }
        query = rekening.insert().values(**data)
        await db.execute(query)
        return data["no_rekening"]

    @classmethod
    async def update(self, no_rekening, **updates):
        query = rekening.update().where(rekening.c.no_rekening == no_rekening).values(**updates)
        result = await db.execute(query)
        return result

    def generate_bank_account_number(self, length=10):
        """Generate a random bank account number with a specified length."""
        if length < 10:  # Ensure length is reasonable for a bank account number
            raise ValueError("Bank account number length should be at least 10 digits")

        # Ensure the first digit is non-zero (for account number validity)
        first_digit = str(random.randint(1, 9))

        # Generate the remaining digits
        remaining_digits = "".join(random.choices("0123456789", k=length - 1))

        # Combine them to form the full account number
        account_number = first_digit + remaining_digits

        return account_number

    def luhn_checksum(self, number):
        """Calculate the Luhn checksum for a given number."""

        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    def generate_valid_bank_account_number(self, length=10):
        """Generate a bank account number with a valid Luhn checksum."""
        account_number = self.generate_bank_account_number(length - 1)
        checksum_digit = self.luhn_checksum(account_number + "0")
        return account_number + str((10 - checksum_digit) % 10)


class Transaksi:
    @classmethod
    async def get(self, id):
        query = transaksi.select().where(transaksi.c.id == id)
        return await db.fetch_one(query)

    @classmethod
    async def create(self, **data):
        data["id"] = uuid4()
        data["created_at"] = datetime.now()
        query = transaksi.insert().values(**data)
        await db.execute(query)
        return data["id"]
