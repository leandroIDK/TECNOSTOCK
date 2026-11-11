# TecnoStock

Aplicación de inventario con registro de usuarios, productos, categorías, entradas, salidas, historial, stock bajo e indicadores.

## Instalación en otra PC desde GitHub

Esta guía crea una base **nueva** y carga seis productos de demostración. Las cuentas se crean durante la instalación con los nombres y contraseñas que tú elijas. Los usuarios y movimientos de otra instalación no se copian automáticamente.

1. **Instala los programas:** SQL Server 2022 y SQL Server Management Studio (SSMS), Git, Python 3.12, Node.js 24.15 o posterior de la rama 24 y Microsoft ODBC Driver 18 for SQL Server. Necesitas acceso para crear una base en SQL Server. Comprueba las versiones en PowerShell. [Versiones compatibles con Angular 22](https://angular.dev/reference/versions) · [ODBC Driver 18](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

   ```powershell
   git --version
   python --version
   node --version
   npm --version
   ```

2. **Descarga el código:**

   ```powershell
   New-Item -ItemType Directory -Force C:\proyectos
   cd C:\proyectos
   git clone https://github.com/leandroIDK/TECNOSTOCK.git
   ```

3. **Crea la base en SSMS.** Conéctate al SQL Server **de esa PC** y anota lo que aparece en **Nombre del servidor**. Abre cada archivo desde SSMS y ejecútalo con **F5**, uno por uno, en este orden:

   1. `C:\proyectos\TECNOSTOCK\database\01_schema.sql`
   2. `C:\proyectos\TECNOSTOCK\database\02_procedures.sql`
   3. `C:\proyectos\TECNOSTOCK\database\03_registro_web.sql`
   4. `C:\proyectos\TECNOSTOCK\database\04_datos_demo.sql`

   Haz esto en una instancia donde no exista ya una base `TecnoStock` con datos que quieras conservar. El primer archivo crea la base; el cuarto prepara la carga de prueba. Los productos aparecerán después del paso 6.

4. **Instala el backend.** Vuelve a PowerShell:

   ```powershell
   cd C:\proyectos\TECNOSTOCK\backend
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

5. **Configura la conexión.** En la misma ventana genera una clave de sesión y abre el archivo `.env`:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
   notepad .env
   ```

   En `backend/.env`, escribe `DB_SERVER` exactamente como el servidor con el que entraste a SSMS; `sa` es un nombre de usuario, no de servidor. Para usar la misma cuenta de Windows con la que abriste SSMS, configura:

   ```dotenv
   DB_SERVER=<NOMBRE_DEL_SERVIDOR_EN_SSMS>
   DB_NAME=TecnoStock
   DB_AUTH=windows
   DB_DRIVER=ODBC Driver 18 for SQL Server
   DB_TRUST_CERTIFICATE=yes
   JWT_SECRET=<PEGA_AQUI_LA_CLAVE_ALEATORIA_GENERADA>
   JWT_EXP_MINUTES=120
   ```

   Sustituye los valores entre `< >` y elimina las líneas `DB_USER` y `DB_PASSWORD` del ejemplo. La cuenta de Windows debe tener permiso para ejecutar procedimientos en `TecnoStock`. Si usas autenticación SQL, cambia a `DB_AUTH=sql` y agrega `DB_USER` y `DB_PASSWORD` de un login autorizado; no uses `sa` para la aplicación.

6. **Comprueba la conexión y crea las cuentas y productos:**

   ```powershell
   .\.venv\Scripts\python.exe check_connection.py
   .\.venv\Scripts\python.exe setup_demo.py
   ```

   La primera orden debe confirmar la conexión SQL y la configuración de sesión. **Si falla, detente aquí y corrige ese error antes de ejecutar la segunda orden.** `setup_demo.py` pide DNI, nombre, apellido, usuario y contraseña para la primera cuenta; puedes crear otras en la misma ejecución. La contraseña se muestra con asteriscos y solo se guarda su hash bcrypt. Después se cargan cuatro categorías, seis productos y entradas iniciales de stock mediante un procedimiento almacenado. Puedes registrar más usuarios desde la página web. **Anota el usuario y recuerda su contraseña** para iniciar sesión.

7. **Inicia FastAPI** en esa misma ventana y déjala abierta:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

8. **Inicia Angular** en otra ventana de PowerShell:

   ```powershell
   cd C:\proyectos\TECNOSTOCK\frontend
   npm ci
   $env:API_PROXY_TARGET = "http://127.0.0.1:8000"
   npm start
   ```

   Abre `http://localhost:4200` en esa PC, inicia sesión y comprueba los productos. `API_PROXY_TARGET` hace que el proxy de Angular envíe `/api` a FastAPI. `DB_SERVER` conecta FastAPI con SQL Server; el proxy no guarda datos.

Si `check_connection.py` falla con `08001`, revisa el nombre de servidor y que SQL Server esté iniciado. Si aparece `18456` o un error de permisos, revisa la autenticación y el acceso de esa cuenta a `TecnoStock`. Si falta `JWT_SECRET`, reemplaza el texto de ejemplo con la clave generada. Si Angular no llega al backend, confirma que FastAPI siga abierto y que `API_PROXY_TARGET` se definió en la misma ventana que ejecuta `npm start`.

## Qué es JWT_SECRET

Es una clave privada aleatoria usada **solo por FastAPI** para firmar y verificar los tokens JWT de sesión. Ponla únicamente en `backend/.env`. No es la contraseña de SQL ni se copia al frontend, proxy o GitHub. Angular recibe el **token** después del login, lo guarda en `sessionStorage` y lo envía en las solicitudes. Si cambias `JWT_SECRET`, habrá que iniciar sesión otra vez; las cuentas y sus contraseñas bcrypt no cambian. El PDF exige mantener credenciales fuera del código público, por eso `.env` está excluido de Git y `.env.example` solo tiene valores de muestra.

## Estructura y reglas

- **Angular 22 y Signal Forms:** componentes en `frontend/src/app/components/`, interfaces en `frontend/src/app/Interface/`, servicio HTTP en `frontend/src/app/service/` y URL relativa `/api` en `frontend/src/environments/environment.ts`.
- **FastAPI:** endpoints en `backend/app/main.py`, validación en `schemas.py`, reglas y autenticación en `services.py`, y llamadas exclusivas a procedimientos almacenados en `repositories.py`.
- **SQL Server 2022:** tablas y procedimientos en `database/`. `04_datos_demo.sql` contiene únicamente datos de ejemplo; la aplicación normal obtiene productos y categorías desde SQL Server.
- El código de producto es único; los precios y cantidades deben ser positivos. Las salidas no pueden dejar stock negativo. Cada entrada o salida actualiza stock e historial en una transacción SQL. Desactivar un producto conserva sus movimientos.

## Pruebas

Desde `backend/`: `.\.venv\Scripts\python.exe -m unittest discover -s tests`. Desde `frontend/`: `npm run build` y `npm test -- --watch=false`. La prueba opcional de integración SQL se activa en PowerShell con `$env:TECNOSTOCK_DB_TEST = '1'`; usa una transacción que se revierte al terminar.

## Git

Los cambios se desarrollan en ramas y se integran a `main` mediante Pull Requests. El archivo `backend/.env` y las contraseñas no se publican.
