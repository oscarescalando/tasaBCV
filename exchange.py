import sqlite3
import os
from datetime import datetime
from pyBCV import Currency

# Verificar si existe la base de datos, si no, crearla
if not os.path.exists('exchange_rates.db'):
    open('exchange_rates.db', 'w').close()

# Conectar o crear la base de datos
conn = sqlite3.connect('exchange_rates.db')
cursor = conn.cursor()

# Crear la tabla exchanges si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS exchanges (
        id TEXT PRIMARY KEY,
        currency VARCHAR(5),
        date_exchange DATE,
        amount FLOAT,
        is_active BOOLEAN
    )
''')
conn.commit()

# Definir la función para insertar o actualizar la tasa de cambio
def update_exchange_rate():
    currency_code = 'USD'
    currency = Currency()
    usd_rate = currency.get_rate(currency_code=currency_code, prettify=False)
    current_date = datetime.now().date()
    exchange_id = f"{currency_code}_{current_date}"

    # Desactivar todas las tasas anteriores
    cursor.execute("UPDATE exchanges SET is_active = 0 WHERE currency = ?", (currency_code,))

    # Insertar o actualizar la nueva tasa de cambio
    cursor.execute('''
        INSERT OR REPLACE INTO exchanges (id, currency, date_exchange, amount, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', (exchange_id, currency_code, current_date, usd_rate, True))

    # Confirmar cambios en la base de datos
    conn.commit()
    print(f"Tasa de cambio para {currency_code} actualizada: {usd_rate}")

# Ejecutar la actualización de la tasa de cambio
if __name__ == "__main__":
    update_exchange_rate()