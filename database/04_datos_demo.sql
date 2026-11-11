USE TecnoStock;
GO

-- Datos de demostracion opcionales. La aplicacion no depende de estos valores.
-- Se puede ejecutar mas de una vez: conserva productos y movimientos existentes.
CREATE OR ALTER PROCEDURE dbo.sp_demo_cargar @IdUsuario int
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE IdUsuario = @IdUsuario AND Activo = 1)
        THROW 50011, 'Crea primero un usuario activo para atribuir la carga inicial.', 1;

    DECLARE @Productos TABLE (
        Codigo nvarchar(40) PRIMARY KEY,
        Nombre nvarchar(150) NOT NULL,
        Descripcion nvarchar(500) NOT NULL,
        Categoria nvarchar(100) NOT NULL,
        PrecioCompra decimal(18,2) NOT NULL,
        PrecioVenta decimal(18,2) NOT NULL,
        StockMinimo int NOT NULL,
        CantidadInicial int NOT NULL
    );

    INSERT @Productos VALUES
        (N'LAP-001', N'Laptop Lenovo IdeaPad 15', N'Laptop de 15 pulgadas', N'Laptops', 1750.00, 2199.00, 3, 8),
        (N'LAP-002', N'Laptop HP 14', N'Laptop de 14 pulgadas', N'Laptops', 1650.00, 2099.00, 2, 5),
        (N'PER-001', N'Mouse Logitech M185', N'Mouse inalambrico', N'Perifericos', 35.00, 55.00, 5, 15),
        (N'PER-002', N'Teclado Redragon Kumara', N'Teclado mecanico', N'Perifericos', 110.00, 159.00, 4, 2),
        (N'ALM-001', N'SSD Kingston 480 GB', N'Unidad de estado solido', N'Almacenamiento', 125.00, 179.00, 4, 3),
        (N'MON-001', N'Monitor LG 24 pulgadas', N'Monitor de 24 pulgadas', N'Monitores', 420.00, 599.00, 2, 6);

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT dbo.Categorias(Nombre, Descripcion)
        SELECT c.Nombre, c.Descripcion
        FROM (VALUES
            (N'Laptops', N'Computadoras portatiles'),
            (N'Perifericos', N'Accesorios de entrada'),
            (N'Almacenamiento', N'Unidades de almacenamiento'),
            (N'Monitores', N'Pantallas para computadora')
        ) AS c(Nombre, Descripcion)
        WHERE NOT EXISTS (SELECT 1 FROM dbo.Categorias WHERE Nombre = c.Nombre);

        INSERT dbo.Productos(Codigo, Nombre, Descripcion, IdCategoria,
                             PrecioCompra, PrecioVenta, StockMinimo)
        SELECT d.Codigo, d.Nombre, d.Descripcion, c.IdCategoria,
               d.PrecioCompra, d.PrecioVenta, d.StockMinimo
        FROM @Productos AS d
        JOIN dbo.Categorias AS c ON c.Nombre = d.Categoria
        WHERE NOT EXISTS (SELECT 1 FROM dbo.Productos WHERE Codigo = d.Codigo);

        -- El stock inicial y su movimiento historico se guardan juntos.
        DECLARE @Carga TABLE (IdProducto int PRIMARY KEY, Cantidad int NOT NULL);
        INSERT @Carga(IdProducto, Cantidad)
        SELECT p.IdProducto, d.CantidadInicial
        FROM @Productos AS d
        JOIN dbo.Productos AS p ON p.Codigo = d.Codigo
        WHERE p.Activo = 1 AND p.StockActual = 0
          AND NOT EXISTS (SELECT 1 FROM dbo.Movimientos WHERE IdProducto = p.IdProducto);

        UPDATE p SET StockActual = c.Cantidad
        FROM dbo.Productos AS p
        JOIN @Carga AS c ON c.IdProducto = p.IdProducto;

        INSERT dbo.Movimientos(IdProducto, IdUsuario, Tipo, Cantidad, Fecha, Motivo,
                              StockAnterior, StockPosterior)
        SELECT c.IdProducto, @IdUsuario, 'ENTRADA', c.Cantidad, SYSDATETIME(),
               N'Carga inicial de demostracion', 0, c.Cantidad
        FROM @Carga AS c;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;

    SELECT COUNT(*) AS ProductosDemo,
           COALESCE(SUM(p.StockActual), 0) AS UnidadesDemo
    FROM dbo.Productos AS p
    JOIN @Productos AS d ON d.Codigo = p.Codigo
    WHERE p.Activo = 1;
END;
GO
