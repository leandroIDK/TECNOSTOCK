IF DB_ID(N'TecnoStock') IS NULL CREATE DATABASE TecnoStock;
GO
USE TecnoStock;
GO
CREATE TABLE dbo.Usuarios (
    IdUsuario int IDENTITY(1,1) PRIMARY KEY,
    Usuario nvarchar(80) NOT NULL UNIQUE,
    Nombre nvarchar(120) NOT NULL,
    HashContrasena nvarchar(255) NOT NULL,
    Activo bit NOT NULL CONSTRAINT DF_Usuarios_Activo DEFAULT 1
);
CREATE TABLE dbo.Categorias (
    IdCategoria int IDENTITY(1,1) PRIMARY KEY,
    Nombre nvarchar(100) NOT NULL UNIQUE,
    Descripcion nvarchar(400) NOT NULL
);
CREATE TABLE dbo.Productos (
    IdProducto int IDENTITY(1,1) PRIMARY KEY,
    Codigo nvarchar(40) NOT NULL UNIQUE,
    Nombre nvarchar(150) NOT NULL,
    Descripcion nvarchar(500) NOT NULL,
    IdCategoria int NOT NULL REFERENCES dbo.Categorias(IdCategoria),
    PrecioCompra decimal(18,2) NOT NULL CHECK (PrecioCompra > 0),
    PrecioVenta decimal(18,2) NOT NULL CHECK (PrecioVenta > 0),
    StockMinimo int NOT NULL CHECK (StockMinimo >= 0),
    StockActual int NOT NULL CONSTRAINT DF_Productos_Stock DEFAULT 0 CHECK (StockActual >= 0),
    Activo bit NOT NULL CONSTRAINT DF_Productos_Activo DEFAULT 1
);
CREATE TABLE dbo.Movimientos (
    IdMovimiento bigint IDENTITY(1,1) PRIMARY KEY,
    IdProducto int NOT NULL REFERENCES dbo.Productos(IdProducto),
    IdUsuario int NOT NULL REFERENCES dbo.Usuarios(IdUsuario),
    Tipo varchar(7) NOT NULL CHECK (Tipo IN ('ENTRADA','SALIDA')),
    Cantidad int NOT NULL CHECK (Cantidad > 0),
    Fecha datetime2(0) NOT NULL,
    Motivo nvarchar(400) NOT NULL,
    StockAnterior int NOT NULL,
    StockPosterior int NOT NULL,
    CONSTRAINT CK_Movimientos_Stock CHECK (StockAnterior >= 0 AND StockPosterior >= 0)
);
CREATE INDEX IX_Movimientos_Producto_Fecha ON dbo.Movimientos(IdProducto, Fecha DESC);
GO
