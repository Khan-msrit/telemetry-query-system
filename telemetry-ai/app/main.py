from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db import TelemetryDB
from app.query_builder import QueryBuilder
from app.visualization import VisualizationRouter
from app.service.query_service import execute_nl_query

app = FastAPI(title="Telemetry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = TelemetryDB()


# ----------------------------
# Deterministic endpoints
# ----------------------------

@app.get("/metric")
def get_metric(parameter: str, agg: str):
    try:
        sql = QueryBuilder.metric(parameter, agg)
        df = db.query(sql)
        return VisualizationRouter.build_response(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/timeseries")
def get_timeseries(parameter: str, limit: int = 100):
    try:
        sql = QueryBuilder.timeseries(parameter, limit=limit)
        df = db.query(sql)
        return VisualizationRouter.build_response(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/compare")
def compare(parameters: str, limit: int = 100):
    try:
        param_list = [p.strip() for p in parameters.split(",")]
        sql = QueryBuilder.multi_timeseries(param_list, limit=limit)
        df = db.query(sql)
        return VisualizationRouter.build_response(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------
# Intelligent NL endpoint
# ----------------------------

class NLQuery(BaseModel):
    query: str


@app.post("/query")
def nl_query(body: NLQuery):
    try:
        return execute_nl_query(body.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
