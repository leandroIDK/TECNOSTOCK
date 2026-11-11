# TecnoStock

Sistema web de inventario para productos informáticos. Permite categorías, productos, entradas, salidas, historial, stock bajo e indicadores.

## Tecnologías y estructura

- `frontend/src/app/components/`: componentes de login e inventario.
- `frontend/src/app/Interface/`: interfaces de los datos.
- `frontend/src/app/service/`: servicio HTTP; usa rutas relativas `/api`.
- `backend/app/main.py`: endpoints FastAPI.
- `backend/app/schemas.py`: validación de datos.
- `backend/app/services.py`: reglas y manejo de errores, autenticación JWT y comprobación bcrypt.
- `backend/app/repositories.py`: ejecuta únicamente procedimientos almacenados.
- `database/`: esquema y procedimientos para SQL Server 2022.

## Preparación de SQL Server

Se requiere SQL Server 2022 y una cuenta de Windows o SQL Server con permisos en la base. Ejecuta `database/01_schema.sql` y después `database/02_procedures.sql` en SQL Server Management Studio. El primer script se ejecuta **una vez**; el segundo usa `CREATE OR ALTER` y puede volver a ejecutarse.

Las tablas empiezan vacías. No hay usuarios, categorías ni productos fijos en el código. Cada categoría se crea desde la aplicación. El valor referencial del panel es la suma de `stock actual × precio de compra` de los productos activos.

## Backend

Instala Python 3.12 y Microsoft ODBC Driver 18 for SQL Server. En `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con el nombre o IP de la instancia SQL y una clave `JWT_SECRET` larga y aleatoria. `.env` está excluido de Git. `DB_AUTH=sql` usa `DB_USER` y `DB_PASSWORD`; `DB_AUTH=windows` usa la cuenta de Windows que ejecuta Python y no requiere esas dos variables. Usa el mismo nombre de servidor que ves en SSMS. Se puede usar una instancia remota o local: la ubicación de SQL Server se configura aquí y es independiente del proxy HTTP.

Comprueba la conexión y que los procedimientos estén instalados:

```powershell
python check_connection.py
```

Para el primer usuario de la aplicación, el usuario de base de datos necesita permiso de ejecución sobre los procedimientos de `dbo`. Si usas un usuario SQL con permisos limitados, asígnale `EXECUTE` sobre ese esquema en TecnoStock.

Tras ejecutar los scripts SQL, crea el primer usuario desde la terminal:

```powershell
python create_admin.py
uvicorn app.main:app --reload
```

Al escribir la contraseña en Windows se muestran asteriscos y se pide repetirla. Se transforma con bcrypt y solo se guarda su hash. Debe tener al menos 8 caracteres y no superar 72 bytes en UTF-8 (algunos caracteres ocupan más de un byte). Si no recuerdas la contraseña del primer usuario, vuelve a ejecutar `database/02_procedures.sql` y luego usa `python reset_password.py`. La API estará en el puerto 8000 y su documentación interactiva en `/docs`.

## Frontend y proxy

En `frontend/`:

```powershell
npm install
$env:API_PROXY_TARGET = "http://127.0.0.1:8000"
npm start
```

Abre `http://localhost:4200`. El archivo `proxy.conf.cjs` tiene una sola ruta: reenvía `/api/**` al destino indicado por `API_PROXY_TARGET`. Así Angular no incluye `localhost` ni otra dirección fija en sus solicitudes. Si FastAPI corre en otra máquina o puerto, cambia el valor de esa variable antes de iniciar `npm start`. En producción, configura el servidor web para reenviar `/api` a FastAPI bajo el mismo origen.

**El proxy solo reenvía solicitudes HTTP**. Los datos se guardan en la instancia indicada por `DB_SERVER`, no en el navegador ni en el proxy. Las credenciales SQL nunca se ponen en Angular.

## Reglas y pruebas manuales

1. Crea una categoría y un producto. El código no debe poder repetirse y ambos precios deben ser positivos.
2. Registra una entrada y comprueba el stock y el historial. La actualización del stock y la creación del movimiento están en una sola transacción SQL.
3. Intenta registrar una salida superior al stock; debe rechazarse sin crear movimiento.
4. Registra una salida válida; comprueba stock anterior y posterior.
5. Desactiva un producto con movimientos; debe desaparecer del catálogo activo y permanecer en el historial.
6. Filtra productos por texto y categoría; filtra el historial por producto y rango de fechas.
7. Consulta el panel y la vista de stock bajo después de cambiar existencias.

## Flujo Git

El proyecto se integró desde `codex/inventario` hacia `main` mediante el [Pull Request #1](https://github.com/leandroIDK/TECNOSTOCK/pull/1). Para cambios posteriores, trabaja en una rama nueva, registra commits descriptivos y abre otro Pull Request hacia `main`.
