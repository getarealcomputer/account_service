from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from logger import logger
from routers import Routers
from database import db


app = FastAPI(title="account-service")

routes = ["nasabah.routes.router"]

Routers(app, routes)()


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


@app.exception_handler(Exception)
async def handle_global_exception(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"remark": "An unexpected error occurred. Please try again later."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Aggregate errors into a single field
    errors = exc.errors()
    remark = "Validation failed: " + "; ".join(
        [f"{err['loc'][0]}: {err['msg']}" for err in errors]
    )

    return JSONResponse(
        status_code=400,
        content={"remark": remark},
    )


@app.exception_handler(404)
async def handle_404(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "remark": f"The requested URL {request.url.path} was not found on the server.",
            "method": request.method,
        },
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}
