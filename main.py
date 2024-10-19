from fastapi import FastAPI, HTTPException
import sqlite3

# Crear instancia de FastAPI
app = FastAPI()

# Conectar a la base de datos SQLite
db_path = 'exchange_rates.db'

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint para consultar la tasa activa según la moneda
@app.get("/exchange_rate/active/")
def get_active_exchange_rate(currency: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exchanges WHERE currency = ? AND is_active = 1", (currency.upper(),))
    exchange_rate = cursor.fetchone()
    conn.close()

    if exchange_rate is None:
        raise HTTPException(status_code=404, detail="Active exchange rate not found for the specified currency.")

    return {
        "currency": exchange_rate["currency"],
        "date_exchange": exchange_rate["date_exchange"],
        "amount": exchange_rate["amount"],
        "is_active": exchange_rate["is_active"]
    }

# Endpoint para consultar las últimas 30 tasas de cambio según la moneda
@app.get("/exchange_rate/history/")
def get_exchange_rate_history(currency: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exchanges WHERE currency = ? ORDER BY date_exchange DESC LIMIT 30", (currency.upper(),))
    exchange_rates = cursor.fetchall()
    conn.close()

    if not exchange_rates:
        raise HTTPException(status_code=404, detail="No exchange rate history found for the specified currency.")

    return [
        {
            "currency": rate["currency"],
            "date_exchange": rate["date_exchange"],
            "amount": rate["amount"],
            "is_active": rate["is_active"]
        }
        for rate in exchange_rates
    ]

# Para correr el servidor, usa el siguiente comando:
# uvicorn exchange_rates_fastapi:app --reload

# Archivo requirements.txt
# fastapi
# uvicorn
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc
