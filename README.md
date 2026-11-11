# TecnoStock

Sistema web de inventario para productos informáticos. Permite registro e inicio de sesión de usuarios, categorías, productos, entradas, salidas, historial, stock bajo e indicadores.

## Tecnologías y estructura

- `frontend/src/app/components/`: componentes de login e inventario.
- `frontend/src/app/Interface/`: interfaces de los datos.
- `frontend/src/app/service/`: servicio HTTP; usa rutas relativas `/api`.
- `frontend/src/environments/environment.ts`: configura la ruta pública `/api` para el servicio Angular; el destino real se indica al proxy.
- `backend/app/main.py`: endpoints FastAPI.
- `backend/app/schemas.py`: validación de datos.
- `backend/app/services.py`: reglas y manejo de errores, autenticación JWT y comprobación bcrypt.
- `backend/app/repositories.py`: ejecuta únicamente procedimientos almacenados.
- `database/`: esquema y procedimientos para SQL Server 2022.

## Preparación de SQL Server

Se requiere SQL Server 2022 y una cuenta de Windows o SQL Server con permisos en la base. En una instalación nueva, ejecuta `database/01_schema.sql`, luego `database/02_procedures.sql` y finalmente `database/03_registro_web.sql` en SQL Server Management Studio. El primer script se ejecuta **una vez**; los otros dos pueden volver a ejecutarse. Si ya tenías TecnoStock funcionando, ejecuta **solo** `03_registro_web.sql` para añadir DNI, apellido y registro web sin borrar usuarios, productos ni movimientos.

Las tablas empiezan vacías. No hay usuarios, categorías ni productos fijos en el código. Cada persona puede crear su cuenta en la pantalla inicial con DNI, nombre, apellido, usuario y contraseña. El DNI y el usuario deben ser únicos. Los usuarios creados antes de esta ampliación conservan su acceso; sus campos DNI y apellido quedan vacíos. Cada categoría se crea desde la aplicación. El valor referencial del panel es la suma de `stock actual × precio de compra` de los productos activos.

## Backend

Instala Python 3.12 y Microsoft ODBC Driver 18 for SQL Server. En `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con el nombre o IP de la instancia SQL y una clave `JWT_SECRET` aleatoria de al menos 32 bytes. Puedes generarla con `python -c "import secrets; print(secrets.token_urlsafe(48))"` y copiar el resultado en `.env`. `.env` está excluido de Git. `DB_AUTH=sql` usa `DB_USER` y `DB_PASSWORD`; `DB_AUTH=windows` usa la cuenta de Windows que ejecuta Python y no requiere esas dos variables. Usa el mismo nombre de servidor que ves en SSMS. Se puede usar una instancia remota o local: la ubicación de SQL Server se configura aquí y es independiente del proxy HTTP. Si dos computadoras usan bases de datos distintas, sus usuarios y productos también serán distintos.

Comprueba la conexión, los procedimientos y la configuración de inicio de sesión:

```powershell
python check_connection.py
```

Para el primer usuario de la aplicación, el usuario de base de datos necesita permiso de ejecución sobre los procedimientos de `dbo`. Si usas un usuario SQL con permisos limitados, asígnale `EXECUTE` sobre ese esquema en TecnoStock.

Tras ejecutar los scripts SQL, inicia el servidor:

```powershell
uvicorn app.main:app --reload
```

Abre la página y selecciona **Crear una cuenta**. El backend genera un hash bcrypt y solo guarda ese hash, nunca la contraseña original. La contraseña debe tener al menos 8 caracteres y no superar 72 bytes en UTF-8 (algunos caracteres ocupan más de un byte). `python create_admin.py` sigue disponible para crear una cuenta desde la terminal. Si no recuerdas su contraseña, usa `python reset_password.py`. La API estará en el puerto 8000 y su documentación interactiva en `/docs`.

Si el registro funciona pero no el inicio de sesión, ejecuta `python check_connection.py` en `backend/`: ahora revisa tanto SQL Server como `JWT_SECRET`. Inicia sesión con el campo **Usuario**, no con el DNI. Un error 401 indica que el usuario o la contraseña no coinciden; un error 503 indica un problema de configuración del servidor. Las cuentas antiguas solo estarán disponibles en otra PC si ambas apuntan a la misma base de datos SQL Server.

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

## Pruebas automáticas

En `frontend/`, ejecuta `npm run build` y `npm test -- --watch=false`. En `backend/`, ejecuta `python -m unittest discover -s tests`. La prueba opcional de integración SQL se activa en PowerShell con `$env:TECNOSTOCK_DB_TEST = '1'` antes de ejecutar el mismo comando de pruebas. Crea datos temporales mediante procedimientos almacenados y revierte la transacción, de modo que conserva los usuarios y productos existentes.

## Flujo Git

El proyecto se integró desde `codex/inventario` hacia `main` mediante el [Pull Request #1](https://github.com/leandroIDK/TECNOSTOCK/pull/1). Para cambios posteriores, trabaja en una rama nueva, registra commits descriptivos y abre otro Pull Request hacia `main`.
