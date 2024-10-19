from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3
import schedule
import time
from multiprocessing import Process
from exchange import update_exchange_rate2, update_exchange_rate as update_exchange_task 


# Crear instancia de FastAPI
app = FastAPI()

# Conectar a la base de datos SQLite
db_path = 'exchange_rates.db'


def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Security scheme
security = HTTPBearer()

# Dummy token for authorization (replace with your actual implementation)
API_TOKEN = "a1b2c3d4e5f6g7h8i9j0"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing token")

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to tasaBCVAPI!"}

# Endpoint para consultar la tasa activa según la moneda
@app.get("/exchange_rate/active/")
def get_active_exchange_rate(currency: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exchanges WHERE currency = ? AND is_active = 1", (currency.upper(),))
        exchange_rate = cursor.fetchone()

    if exchange_rate is None:
        raise HTTPException(status_code=404, detail="Active exchange rate not found for the specified currency.")

    return {
        "id": exchange_rate["id"],
        "currency": exchange_rate["currency"],
        "date_exchange": exchange_rate["date_exchange"],
        "amount": exchange_rate["amount"],
        "is_active": exchange_rate["is_active"]
    }

# Endpoint para consultar las últimas 30 tasas de cambio según la moneda
@app.get("/exchange_rate/history/")
def get_exchange_rate_history(currency: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exchanges WHERE currency = ? ORDER BY date_exchange DESC LIMIT 30", (currency.upper(),))
        exchange_rates = cursor.fetchall()

    if not exchange_rates:
        raise HTTPException(status_code=404, detail="No exchange rate history found for the specified currency.")

    return [
        {
            "id": rate["id"],
            "currency": rate["currency"],
            "date_exchange": rate["date_exchange"],
            "amount": rate["amount"],
            "is_active": rate["is_active"]
        }
        for rate in exchange_rates
    ]

# Endpoint para ejecutar la actualización de la tasa de cambio
@app.post("/exchange_rate/update/", dependencies=[Depends(verify_token)])
def update_exchange_rate_endpoint():
    try:
        with get_db_connection() as conn:
            update_exchange_rate2(conn)
        return {"detail": "Exchange rate updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the exchange rate: {str(e)}")

# Endpoint para actualizar la tasa de cambio manualmente
@app.put("/exchange_rate/update_manual/", dependencies=[Depends(verify_token)])
def update_manual_exchange_rate(
    id: str,
    currency: str,
    date_exchange: str = Body(...),
    amount: float = Body(...),
    is_active: bool = Body(...)
):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Actualizar la tasa de cambio especificada
        cursor.execute('''
            UPDATE exchanges
            SET date_exchange = ?, amount = ?, is_active = ?, currency = ?
            WHERE id = ?
        ''', (date_exchange, amount, is_active, currency.upper(), id))

        # Si se activa una nueva tasa, desactivar las anteriores
        if is_active:
            cursor.execute('''
                UPDATE exchanges
                SET is_active = 0
                WHERE currency = ? AND date_exchange != ?
            ''', (currency.upper(), date_exchange))

        conn.commit()

    return {"detail": "Exchange rate updated manually successfully."}

# Endpoint para eliminar un registro de la tasa de cambio
@app.delete("/exchange_rate/delete/", dependencies=[Depends(verify_token)])
def delete_exchange_rate(id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Eliminar el registro especificado
        cursor.execute("DELETE FROM exchanges WHERE id = ?", (id,))
        conn.commit()

    return {"detail": "Exchange rate deleted successfully."}

# Endpoint para crear una nueva tasa de cambio
@app.post("/exchange_rate/create/", dependencies=[Depends(verify_token)])
def create_exchange_rate(
    id: str = Body(...),
    currency: str = Body(...),
    date_exchange: str = Body(...),
    amount: float = Body(...),
    is_active: bool = Body(...)
):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insertar la nueva tasa de cambio
        try:
            cursor.execute('''
                INSERT INTO exchanges (id, currency, date_exchange, amount, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (id, currency.upper(), date_exchange, amount, is_active))

            # Si se activa una nueva tasa, desactivar las anteriores
            if is_active:
                cursor.execute('''
                    UPDATE exchanges
                    SET is_active = 0
                    WHERE currency = ? AND id != ?
                ''', (currency.upper(), id))

            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Exchange rate with this ID already exists.")

    return {"detail": "Exchange rate created successfully."}

# Programar la ejecución diaria a las 12 AM
schedule.every().day.at("00:00").do(update_exchange_task)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Ejecutar el scheduler en un proceso separado
if __name__ == "__main__":
    Process(target=run_schedule, daemon=True).start()

# Para correr el servidor, usa el siguiente comando:
# uvicorn exchange_rates_fastapi:app --reload

# Archivo requirements.txt
# fastapi
# uvicorn
# schedule

