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

## Arranque en otra PC con los datos existentes (Windows)

Esta guía supone que Angular, FastAPI y SQL Server 2022 se ejecutarán en la otra PC. **GitHub contiene el código, pero no la base de datos ni `backend/.env`.** Lleva por separado el respaldo `.bak` de TecnoStock: contiene usuarios, hashes bcrypt de sus contraseñas, categorías, productos, movimientos, tablas y procedimientos almacenados. Si solo clonas GitHub, esos datos no aparecen.

1. **Prepara la PC.** Necesitas permiso para restaurar bases de datos en SQL Server 2022, SQL Server Management Studio (SSMS), Git, Python 3.12, Node.js 24.15 o posterior de la rama 24 y Microsoft ODBC Driver 18 for SQL Server. Comprueba en PowerShell `git --version`, `python --version`, `node --version` y `npm --version`. [Compatibilidad de Angular](https://angular.dev/reference/versions) · [Controlador ODBC de Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).
2. **Clona el proyecto.** Elige una carpeta propia; estas órdenes usan `C:\proyectos` como ejemplo:

   ```powershell
   New-Item -ItemType Directory -Force C:\proyectos
   cd C:\proyectos
   git clone https://github.com/leandroIDK/TECNOSTOCK.git
   cd .\TECNOSTOCK
   ```

3. **Restaura los datos.** Copia el `.bak` a la otra PC, en una carpeta que el servicio de SQL Server pueda leer. En SSMS conéctate a su instancia, haz clic derecho en **Bases de datos > Restaurar base de datos**, elige **Origen: Dispositivo > ... > Agregar** y selecciona el archivo. Comprueba que **Destino** sea `TecnoStock`. En **Archivos**, marca **Reubicar todos los archivos en una carpeta** y elige las carpetas de datos y registros de esa instancia si aparecen rutas de la PC anterior. Confirma la restauración. Si ya existe una base `TecnoStock` en esa PC, revisa primero sus datos: restaurar encima puede sustituirlos. [Guía oficial de restauración en SSMS](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/restore-a-database-to-a-new-location-sql-server).
4. **Configura el acceso de Python a SQL Server.** La cuenta de Windows o el login SQL que usará Python debe poder entrar a `TecnoStock` y ejecutar sus procedimientos. Los usuarios de la *web* sí vienen en el `.bak`; los logins de la *instancia SQL* pueden requerir crearse o asociarse de nuevo tras restaurar en otro servidor. Si usas Windows, inicia Python con una cuenta autorizada. Si usas autenticación SQL, crea un login y usuario de base de datos propios para la aplicación y concédeles `EXECUTE` sobre el esquema `dbo`. [Explicación de logins tras una restauración](https://learn.microsoft.com/en-us/sql/sql-server/failover-clusters/troubleshoot-orphaned-users-sql-server).

   Para la opción más simple en una instalación local, conéctate a SSMS mediante **Autenticación de Windows** y ejecuta Python con esa misma cuenta, siempre que tenga acceso a la base restaurada. Si necesitas autenticación SQL, un administrador puede crearla en **Seguridad > Inicios de sesión > Nuevo inicio de sesión** y, en **Asignación de usuarios**, marcar `TecnoStock`. Después, en una consulta de SSMS, concede permiso al usuario de base de datos creado (sustituye el nombre):

   ```sql
   USE TecnoStock;
   GRANT EXECUTE ON SCHEMA::dbo TO [tu_usuario_sql];
   ```
5. **Instala y configura el backend.** Desde la carpeta clonada:

   ```powershell
   cd C:\proyectos\TECNOSTOCK\backend
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
   notepad .env
   ```

   En `.env`, cambia `DB_SERVER` por el **Nombre del servidor** que funciona en SSMS (por ejemplo, `EQUIPO\SQLEXPRESS`; `sa` es un usuario, no un servidor). Deja `DB_NAME=TecnoStock`. Para usar la cuenta de Windows con la que ejecutas Python, pon `DB_AUTH=windows`; en ese modo `DB_USER` y `DB_PASSWORD` no se usan y puedes quitar esas dos líneas. Si creaste un login SQL, pon `DB_AUTH=sql` y escribe su `DB_USER` y `DB_PASSWORD`. Mantén `DB_DRIVER=ODBC Driver 18 for SQL Server` y, para esta instalación local con certificado de SQL Server sin autoridad de confianza, `DB_TRUST_CERTIFICATE=yes`. Copia el valor aleatorio que imprimió el comando anterior en `JWT_SECRET`, sin comillas. No conserves el texto de ejemplo.

   Ejemplo de `.env` con autenticación de Windows; sustituye los valores entre `< >` antes de usarlo:

   ```dotenv
   DB_SERVER=<NOMBRE_DEL_SERVIDOR_EN_SSMS>
   DB_NAME=TecnoStock
   DB_AUTH=windows
   DB_DRIVER=ODBC Driver 18 for SQL Server
   DB_TRUST_CERTIFICATE=yes
   JWT_SECRET=<CLAVE_ALEATORIA_GENERADA>
   JWT_EXP_MINUTES=120
   ```

6. **Comprueba y arranca el backend.** En la misma carpeta `backend`:

   ```powershell
   .\.venv\Scripts\python.exe check_connection.py
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

   La primera orden debe confirmar la conexión SQL y la configuración de sesión. Deja abierta esta ventana. La API estará en `http://127.0.0.1:8000/docs`.
7. **Arranca Angular en otra ventana de PowerShell:**

   ```powershell
   cd C:\proyectos\TECNOSTOCK\frontend
   npm ci
   $env:API_PROXY_TARGET = "http://127.0.0.1:8000"
   npm start
   ```

   Abre `http://localhost:4200` en esa PC. Inicia sesión con el **usuario** y contraseña de una cuenta ya registrada y comprueba productos e historial. `API_PROXY_TARGET` indica al proxy dónde está FastAPI; `DB_SERVER` indica al backend dónde está SQL Server. El proxy no almacena datos.

Si `check_connection.py` muestra el error `08001`, comprueba nombre de servidor, instancia y que SQL Server esté iniciado. Si aparece error `18456` o de permisos, revisa el login y su acceso a la base; tras mover una base, el login del servidor anterior puede no existir en el nuevo. Si aparece un error sobre `JWT_SECRET`, genera una clave real y guárdala en `backend/.env`. Si Angular no llega a la API, confirma que FastAPI siga abierto y que `API_PROXY_TARGET` se haya definido **en la misma ventana** donde ejecutaste `npm start`.

### Qué es JWT_SECRET y dónde se coloca

`JWT_SECRET` es una clave aleatoria privada que **solo el backend** usa para firmar y verificar el token de sesión JWT. No es la contraseña de SQL Server ni la contraseña de un usuario. Se escribe una sola vez en `backend/.env`; no se copia al frontend, al proxy, a SQL Server ni a GitHub. Después del login, Angular recibe un **token** y lo guarda en `sessionStorage` para enviarlo en las peticiones; nunca recibe `JWT_SECRET`. `JWT_EXP_MINUTES=120` limita la duración del token a 120 minutos. Si cambias la clave, las sesiones emitidas antes dejarán de ser válidas y los usuarios tendrán que iniciar sesión otra vez; sus cuentas y contraseñas bcrypt permanecen en SQL Server. Si ejecutas varios backends para la misma sesión, todos deben usar la misma clave.

El PDF del proyecto exige mantener las credenciales de conexión fuera del código público. Por eso `backend/.env` está excluido de Git y `backend/.env.example` contiene únicamente valores de muestra.

## Preparación de SQL Server

Se requiere SQL Server 2022 y una cuenta de Windows o SQL Server con permisos en la base. **Si restauraste un `.bak`, no ejecutes estos scripts:** el respaldo ya incluye la estructura, los procedimientos y los datos. Para una base completamente nueva y vacía, ejecuta `database/01_schema.sql`, luego `database/02_procedures.sql` y finalmente `database/03_registro_web.sql` en SQL Server Management Studio. El primer script se ejecuta **una vez**; los otros dos pueden volver a ejecutarse. Si ya tenías una base TecnoStock antigua funcionando sin registro web, ejecuta **solo** `03_registro_web.sql` para añadir DNI, apellido y registro web sin borrar usuarios, productos ni movimientos.

Si creas una base desde los scripts, las tablas empiezan vacías; al restaurar un respaldo, conservan sus datos. No hay usuarios, categorías ni productos fijos en el código. Cada persona puede crear su cuenta en la pantalla inicial con DNI, nombre, apellido, usuario y contraseña. El DNI y el usuario deben ser únicos. Los usuarios creados antes de esta ampliación conservan su acceso; sus campos DNI y apellido quedan vacíos. Cada categoría se crea desde la aplicación. El valor referencial del panel es la suma de `stock actual × precio de compra` de los productos activos.

## Backend

Instala Python 3.12 y Microsoft ODBC Driver 18 for SQL Server. En `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con el nombre o IP de la instancia SQL y una clave `JWT_SECRET` aleatoria de al menos 32 bytes. Puedes generarla con `python -c "import secrets; print(secrets.token_urlsafe(48))"` y copiar el resultado en `.env`. `.env` está excluido de Git. `DB_AUTH=sql` usa `DB_USER` y `DB_PASSWORD`; `DB_AUTH=windows` usa la cuenta de Windows que ejecuta Python y no requiere esas dos variables. Usa el mismo nombre de servidor que ves en SSMS. Se puede usar una instancia remota o local: la ubicación de SQL Server se configura aquí y es independiente del proxy HTTP. Si dos computadoras usan bases de datos distintas, sus usuarios y productos también serán distintos.

Comprueba la conexión, los procedimientos y la configuración de inicio de sesión:

```powershell
.\.venv\Scripts\python.exe check_connection.py
```

Para el primer usuario de la aplicación, el usuario de base de datos necesita permiso de ejecución sobre los procedimientos de `dbo`. Si usas un usuario SQL con permisos limitados, asígnale `EXECUTE` sobre ese esquema en TecnoStock.

Tras crear o restaurar la base SQL, inicia el servidor:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abre la página y selecciona **Crear una cuenta**. El backend genera un hash bcrypt y solo guarda ese hash, nunca la contraseña original. La contraseña debe tener al menos 8 caracteres y no superar 72 bytes en UTF-8 (algunos caracteres ocupan más de un byte). `python create_admin.py` sigue disponible para crear una cuenta desde la terminal. Si no recuerdas su contraseña, usa `python reset_password.py`. La API estará en el puerto 8000 y su documentación interactiva en `/docs`.

Si el registro funciona pero no el inicio de sesión, ejecuta `.\.venv\Scripts\python.exe check_connection.py` en `backend/`: revisa tanto SQL Server como `JWT_SECRET`. Inicia sesión con el campo **Usuario**, no con el DNI. Un error 401 indica que el usuario o la contraseña no coinciden; un error 503 indica un problema de configuración del servidor. Las cuentas antiguas estarán disponibles en otra PC si apunta a la misma base SQL o si allí restauraste una copia de esa base.

## Frontend y proxy

En `frontend/`:

```powershell
npm ci
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
