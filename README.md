# TecnoStock

Sistema web de inventario para productos informáticos. Permite categorías, productos, entradas, salidas, historial, stock bajo e indicadores.

## Tecnologías y estructura

- `frontend/`: Angular 22 y Signal Forms. Los servicios HTTP usan rutas relativas `/api`.
- `backend/app/main.py`: endpoints FastAPI.
- `backend/app/schemas.py`: validación de datos.
- `backend/app/services.py`: reglas y manejo de errores, autenticación JWT y comprobación bcrypt.
- `backend/app/repositories.py`: ejecuta únicamente procedimientos almacenados.
- `database/`: esquema y procedimientos para SQL Server 2022.

## Preparación de SQL Server

Se requiere SQL Server 2022 y un usuario SQL con permisos en la base. Ejecuta `database/01_schema.sql` y después `database/02_procedures.sql` en SQL Server Management Studio. El primer script se ejecuta **una vez**; el segundo usa `CREATE OR ALTER` y puede volver a ejecutarse.

Las tablas empiezan vacías. No hay usuarios, categorías ni productos fijos en el código. Cada categoría se crea desde la aplicación. El valor referencial del panel es la suma de `stock actual × precio de compra` de los productos activos.

## Backend

Instala Python 3.12 y Microsoft ODBC Driver 18 for SQL Server. En `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con el nombre o IP de la instancia SQL, las credenciales y una clave `JWT_SECRET` larga y aleatoria. `.env` está excluido de Git. Se puede usar una instancia remota o local: la ubicación de SQL Server se configura aquí y es independiente del proxy HTTP.

Tras ejecutar los scripts SQL, crea el primer usuario desde la terminal:

```powershell
python create_admin.py
uvicorn app.main:app --reload
```

La contraseña se lee sin mostrarla, se transforma con bcrypt y solo se guarda su hash. La API estará en el puerto 8000 y su documentación interactiva en `/docs`.

## Frontend y proxy

En `frontend/`:

```powershell
npm install
npm start
```

Abre `http://localhost:4200`. El archivo `proxy.conf.json` tiene una sola ruta: reenvía `/api/**` al backend. Así Angular no incluye `localhost` en sus solicitudes. Si FastAPI corre en otra dirección o puerto, cambia únicamente el `target` del proxy y reinicia `npm start`. En producción, configura el servidor web para reenviar `/api` a FastAPI bajo el mismo origen.

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

Trabaja en ramas `codex/<funcionalidad>` o `<funcionalidad>`, haz commits descriptivos y abre un Pull Request por funcionalidad hacia la rama principal. El repositorio remoto se configura al publicarlo.
