Este script de Python está diseñado para ejecutarse como un cron job, obteniendo diariamente la tasa de cambio USD/VES del Banco Central de Venezuela (BCV) y actualizando esta información en una base de datos SQLite. Además, proporciona una API para consultar las tasas de cambio utilizando FastAPI.

## Características principales

- Obtiene la tasa de cambio USD/VES actual del BCV
- Verifica si ya existe un registro para la fecha actual en la base de datos SQLite
- Actualiza el registro existente o crea uno nuevo según sea necesario
- Proporciona una API para consultar la tasa de cambio activa y el historial de tasas de cambio
- Permite la actualización manual de la tasa de cambio
- Permite la eliminación de registros de tasas de cambio
- Proporciona autenticación básica para endpoints sensibles

## Requisitos

Para ejecutar este script, necesitarás Python 3.6+ y los siguientes paquetes:

- fastapi==0.100.0
- hypercorn==0.14.4
- pyBCV
- sqlite3
- schedule

## Instalación

1. Clona el repositorio o copia el script en tu sistema:

2. Crea un entorno virtual (opcional pero recomendado):

```sh
python -m venv venv
source venv/bin/activate  # En Windows usa venv\Scripts\activate
```

3. Instala las dependencias:

```sh
pip install -r requirements.txt
```

## Configuración

1. Asegúrate de tener una base de datos SQLite llamada `exchange_rates.db` en el mismo directorio que el script. El script creará automáticamente la base de datos y la tabla `exchanges` si no existen.

## Uso

### Ejecutar el script manualmente

Para actualizar la tasa de cambio manualmente, ejecuta:

```sh
python exchange.py
```

### Configurar como un cron job

Para configurarlo como un cron job en un sistema Unix:

1. Abre el editor de crontab:

```sh
crontab -e
```

2. Añade una línea como esta para ejecutar el script diariamente a las 9:00 AM:

```sh
0 9 * * * /ruta/al/entorno/python exchange.py >> /ruta/al/log.txt 2>&1
```

### Ejecutar el servidor FastAPI

Para correr el servidor FastAPI y proporcionar la API, usa el siguiente comando:

```sh
hypercorn main:app --reload
```

### Endpoints de la API

- **Consultar la tasa activa según la moneda:**

```http
GET /exchange_rate/active/?currency=USD
```

- **Consultar las últimas 30 tasas de cambio según la moneda:**

```http
GET /exchange_rate/history/?currency=USD
```

- **Actualizar la tasa de cambio automáticamente:**

```http
POST /exchange_rate/update/
```

- **Actualizar la tasa de cambio manualmente:**

```http
PUT /exchange_rate/update_manual/
```

- **Eliminar un registro de la tasa de cambio:**

```http
DELETE /exchange_rate/delete/
```

- **Crear una nueva tasa de cambio:**

```http
POST /exchange_rate/create/
```

## Funcionamiento

1. El script `exchange.py` obtiene la tasa de cambio actual USD/VES utilizando la biblioteca pyBCV.
2. Verifica si ya existe un registro en la base de datos SQLite para la fecha actual.
3. Si existe, actualiza el registro con la nueva tasa.
4. Si no existe, crea un nuevo registro con la fecha actual y la tasa obtenida.
5. El servidor FastAPI en `main.py` proporciona endpoints para consultar la tasa de cambio activa, el historial de tasas de cambio, y permite la actualización y eliminación de registros.

## Desarrollo

El script utiliza:

- `pyBCV` para obtener la tasa de cambio oficial del BCV.
- `fastapi` para crear la API.
- `sqlite3` para manejar la base de datos SQLite.
- `schedule` para programar la actualización automática de la tasa de cambio.

## Solución de problemas

- Asegúrate de que la base de datos SQLite `exchange_rates.db` exista en el directorio correcto.
- Verifica que la tabla `exchanges` exista en la base de datos y tenga la estructura correcta.
- Si el script falla al obtener la tasa del BCV, puede ser debido a cambios en la API del BCV o problemas de conexión.

## Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de crear un pull request.
