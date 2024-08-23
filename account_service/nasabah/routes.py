from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database import db
from logger import logger
from .models import TransactionType
from .models import Nasabah as NasabahModel
from .models import Rekening as RekeningModel
from .models import Transaksi as TransaksiModel

from .schema import Nasabah as NasabahSchema
from .schema import Transaksi as TransaksiSchema

router = APIRouter()


@router.post("/daftar")
async def register(data: NasabahSchema):
    transaction = await db.transaction()
    try:
        nasabah_id = await NasabahModel.create(**data.dict())
        no_rekening = await RekeningModel.create(nasabah_id=nasabah_id)
        await transaction.commit()
        return {"no_rekening": no_rekening}
    except Exception as e:
        logger.error(f"{e}")
        await transaction.rollback()
        return JSONResponse(status_code=400, content={"remark": f"{e}"})


@router.post("/tabung")
async def tabung(data: TransaksiSchema):
    transaction = await db.transaction()
    try:
        rekening_sebelum = await RekeningModel.get(data.no_rekening)

        transaksi = {
            "rekening_id": rekening_sebelum["id"],
            "no_rekening": rekening_sebelum["no_rekening"],
            "nominal": data.nominal,
            "tipe_transaksi": TransactionType.TABUNG,
        }
        await TransaksiModel.create(**transaksi)

        await RekeningModel.update(
            no_rekening=data.no_rekening, saldo=rekening_sebelum["saldo"] + data.nominal
        )
        rekening_sesudah = await RekeningModel.get(data.no_rekening)
        await transaction.commit()
        return {"saldo": rekening_sesudah["saldo"]}

    except Exception as e:
        logger.error(f"{e}")
        await transaction.rollback()
        return JSONResponse(status_code=400, content={"remark": f"{e}"})


@router.post("/tarik")
async def tarik(data: TransaksiSchema):
    transaction = await db.transaction()
    try:
        rekening_sebelum = await RekeningModel.get(data.no_rekening)

        transaksi = {
            "rekening_id": rekening_sebelum["id"],
            "no_rekening": rekening_sebelum["no_rekening"],
            "nominal": data.nominal,
            "tipe_transaksi": TransactionType.TARIK,
        }
        await TransaksiModel.create(**transaksi)

        await RekeningModel.update(
            no_rekening=data.no_rekening, saldo=rekening_sebelum["saldo"] - data.nominal
        )
        rekening_sesudah = await RekeningModel.get(data.no_rekening)
        await transaction.commit()
        return {"saldo": rekening_sesudah["saldo"]}

    except Exception as e:
        logger.error(f"{e}")
        await transaction.rollback()
        return JSONResponse(status_code=400, content={"remark": f"{e}"})


@router.get("/saldo/{no_rekening}")
async def cek_saldo(no_rekening):
    try:
        rekening = await RekeningModel.get(no_rekening)
        return {"saldo": rekening.saldo}
    except Exception as e:
        return JSONResponse(status_code=400, content={"remark": f"{e}"})
