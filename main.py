"""
Informes IA — Servidor principal
"""
import os, hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pipeline import run_pipeline

load_dotenv()
app = FastAPI(title="Informes IA", version="1.0.0")
FLOW_SECRET = os.getenv("FLOW_SECRET", "")

@app.post("/webhook/flow")
async def webhook_flow(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    data = await request.json()
    if data.get("status") != "paid":
        return JSONResponse({"ok": True})
    pedido = {
        "email": data["payer_email"],
        "nombre": data.get("payer_name", ""),
        "tipo": data["metadata"]["tipo"],
        "objetivo": data["metadata"]["objetivo"],
        "datos_extra": data["metadata"].get("datos_extra", ""),
        "flow_order": data["flowOrder"],
    }
    background_tasks.add_task(run_pipeline, pedido)
    return JSONResponse({"ok": True})

@app.get("/")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
