from datetime import datetime
import re
from pydantic import BaseModel, validator


class Nasabah(BaseModel):
    nama: str
    nik: str
    no_hp: str

    class Config:
        from_attributes = True

    @validator("nama")
    def check_non_empty_fields(cls, v):
        if not v.strip():
            raise ValueError('username must not be an empty string')
        return v

    @validator("nik")
    def validate_nik(cls, v):
        # Check if the NIK is exactly 16 digits long
        if len(v) != 16:
            raise ValueError("NIK must be exactly 16 digits long")

        # Check if the NIK is numeric
        if not v.isdigit():
            raise ValueError("NIK must contain only digits")

        # Validate regional code (digits 1-6)
        region_code = v[:6]
        if not re.match(r"^\d{6}$", region_code):
            raise ValueError("Invalid regional code in NIK")

        # Validate date of birth (digits 7-12)
        date_of_birth = v[6:12]
        day = int(date_of_birth[:2])
        month = int(date_of_birth[2:4])
        year = int(date_of_birth[4:])

        # Check if the month and day are within valid ranges
        if not (1 <= month <= 12):
            raise ValueError("Invalid month in NIK")
        if not (1 <= day <= 31):
            raise ValueError("Invalid day in NIK")

        # Adjust day for female NIKs (day >= 41 is valid)
        if day > 40:
            day -= 40  # Correct the day for female NIKs

        # Validate the corrected date
        try:
            datetime(year=year, month=month, day=day)
        except ValueError:
            raise ValueError("Invalid date of birth in NIK")

        # Validate serial number (digits 13-16)
        serial_number = v[12:]
        if not re.match(r"^\d{4}$", serial_number):
            raise ValueError("Invalid serial number in NIK")

        return v

    @validator("no_hp")
    def validate_phone_number(cls, v):
        if not v.strip():
            return v

        # Regular expression to match various phone number formats
        pattern = re.compile(
            r"^\+?[1-9]\d{1,14}$"  # E.164 format: +[country_code][number], with optional '+' and up to 15 digits
        )

        if not pattern.match(v):
            raise ValueError("Invalid phone number format")

        return v

class Transaksi(BaseModel):
    no_rekening: str
    nominal: int

    class Config:
        from_attributes = True
