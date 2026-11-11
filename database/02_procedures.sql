USE TecnoStock;
GO
CREATE OR ALTER PROCEDURE dbo.sp_usuario_crear
 @Usuario nvarchar(80), @Nombre nvarchar(120), @HashContrasena nvarchar(255)
AS
BEGIN
 SET NOCOUNT ON;
 IF NULLIF(TRIM(@Usuario), N'') IS NULL OR NULLIF(TRIM(@Nombre), N'') IS NULL THROW 50001, 'Usuario y nombre son obligatorios.', 1;
 INSERT dbo.Usuarios(Usuario,Nombre,HashContrasena) VALUES(TRIM(@Usuario),TRIM(@Nombre),@HashContrasena);
 SELECT IdUsuario, Usuario, Nombre FROM dbo.Usuarios WHERE IdUsuario = SCOPE_IDENTITY();
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_usuario_por_nombre @Usuario nvarchar(80)
AS
BEGIN
 SET NOCOUNT ON;
 SELECT IdUsuario, Usuario, Nombre, HashContrasena, Activo FROM dbo.Usuarios WHERE Usuario=@Usuario;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_usuario_cambiar_hash
 @Usuario nvarchar(80), @HashContrasena nvarchar(255)
AS
BEGIN
 SET NOCOUNT ON;
 UPDATE dbo.Usuarios SET HashContrasena=@HashContrasena WHERE Usuario=@Usuario AND Activo=1;
 IF @@ROWCOUNT=0 THROW 50008, 'Usuario activo no encontrado.', 1;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_categoria_crear @Nombre nvarchar(100), @Descripcion nvarchar(400)
AS
BEGIN
 SET NOCOUNT ON;
 IF NULLIF(TRIM(@Nombre), N'') IS NULL THROW 50002, 'El nombre de la categoria es obligatorio.', 1;
 INSERT dbo.Categorias(Nombre,Descripcion) VALUES(TRIM(@Nombre),TRIM(@Descripcion));
 SELECT IdCategoria,Nombre,Descripcion FROM dbo.Categorias WHERE IdCategoria=SCOPE_IDENTITY();
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_categoria_listar
AS
BEGIN
 SET NOCOUNT ON;
 SELECT IdCategoria,Nombre,Descripcion FROM dbo.Categorias ORDER BY Nombre;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_producto_crear
 @Codigo nvarchar(40), @Nombre nvarchar(150), @Descripcion nvarchar(500), @IdCategoria int,
 @PrecioCompra decimal(18,2), @PrecioVenta decimal(18,2), @StockMinimo int
AS
BEGIN
 SET NOCOUNT ON;
 IF NULLIF(TRIM(@Codigo),N'') IS NULL OR NULLIF(TRIM(@Nombre),N'') IS NULL THROW 50003, 'Codigo y nombre son obligatorios.', 1;
 IF @PrecioCompra<=0 OR @PrecioVenta<=0 OR @StockMinimo<0 THROW 50004, 'Precios o stock minimo invalidos.', 1;
 INSERT dbo.Productos(Codigo,Nombre,Descripcion,IdCategoria,PrecioCompra,PrecioVenta,StockMinimo)
 VALUES(TRIM(@Codigo),TRIM(@Nombre),TRIM(@Descripcion),@IdCategoria,@PrecioCompra,@PrecioVenta,@StockMinimo);
 SELECT IdProducto FROM dbo.Productos WHERE IdProducto=SCOPE_IDENTITY();
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_producto_actualizar
 @IdProducto int, @Codigo nvarchar(40), @Nombre nvarchar(150), @Descripcion nvarchar(500), @IdCategoria int,
 @PrecioCompra decimal(18,2), @PrecioVenta decimal(18,2), @StockMinimo int
AS
BEGIN
 SET NOCOUNT ON;
 IF NULLIF(TRIM(@Codigo),N'') IS NULL OR NULLIF(TRIM(@Nombre),N'') IS NULL THROW 50003, 'Codigo y nombre son obligatorios.', 1;
 IF @PrecioCompra<=0 OR @PrecioVenta<=0 OR @StockMinimo<0 THROW 50004, 'Precios o stock minimo invalidos.', 1;
 UPDATE dbo.Productos SET Codigo=TRIM(@Codigo),Nombre=TRIM(@Nombre),Descripcion=TRIM(@Descripcion),
 IdCategoria=@IdCategoria,PrecioCompra=@PrecioCompra,PrecioVenta=@PrecioVenta,StockMinimo=@StockMinimo
 WHERE IdProducto=@IdProducto AND Activo=1;
 IF @@ROWCOUNT=0 THROW 50005, 'Producto activo no encontrado.', 1;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_producto_desactivar @IdProducto int
AS
BEGIN
 SET NOCOUNT ON;
 UPDATE dbo.Productos SET Activo=0 WHERE IdProducto=@IdProducto AND Activo=1;
 IF @@ROWCOUNT=0 THROW 50005, 'Producto activo no encontrado.', 1;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_producto_listar
 @Buscar nvarchar(150)=NULL, @IdCategoria int=NULL, @SoloBajo bit=0, @SoloActivos bit=1
AS
BEGIN
 SET NOCOUNT ON;
 SELECT p.IdProducto,p.Codigo,p.Nombre,p.Descripcion,p.IdCategoria,c.Nombre AS Categoria,
 p.PrecioCompra,p.PrecioVenta,p.StockMinimo,p.StockActual,p.Activo
 FROM dbo.Productos p JOIN dbo.Categorias c ON c.IdCategoria=p.IdCategoria
 WHERE (@SoloActivos=0 OR p.Activo=1)
 AND (@Buscar IS NULL OR p.Codigo LIKE N'%'+@Buscar+N'%' OR p.Nombre LIKE N'%'+@Buscar+N'%')
 AND (@IdCategoria IS NULL OR p.IdCategoria=@IdCategoria)
 AND (@SoloBajo=0 OR p.StockActual<=p.StockMinimo)
 ORDER BY p.Nombre;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_producto_obtener @IdProducto int
AS
BEGIN
 SET NOCOUNT ON;
 SELECT p.IdProducto,p.Codigo,p.Nombre,p.Descripcion,p.IdCategoria,c.Nombre AS Categoria,
 p.PrecioCompra,p.PrecioVenta,p.StockMinimo,p.StockActual,p.Activo
 FROM dbo.Productos p JOIN dbo.Categorias c ON c.IdCategoria=p.IdCategoria WHERE p.IdProducto=@IdProducto;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_movimiento_registrar
 @IdProducto int,@IdUsuario int,@Tipo varchar(7),@Cantidad int,@Fecha datetime2(0),@Motivo nvarchar(400)
AS
BEGIN
 SET NOCOUNT ON;
 SET XACT_ABORT ON;
 IF @Cantidad<=0 OR @Tipo NOT IN ('ENTRADA','SALIDA') OR NULLIF(TRIM(@Motivo),N'') IS NULL
  THROW 50006, 'Movimiento invalido.', 1;
 DECLARE @Anterior int,@Posterior int;
 BEGIN TRY
  BEGIN TRANSACTION;
  SELECT @Anterior=StockActual FROM dbo.Productos WITH (UPDLOCK,HOLDLOCK)
   WHERE IdProducto=@IdProducto AND Activo=1;
  IF @Anterior IS NULL THROW 50005, 'Producto activo no encontrado.', 1;
  IF @Tipo='SALIDA' AND @Cantidad>@Anterior THROW 50007, 'Stock insuficiente.', 1;
  SET @Posterior=CASE WHEN @Tipo='ENTRADA' THEN @Anterior+@Cantidad ELSE @Anterior-@Cantidad END;
  UPDATE dbo.Productos SET StockActual=@Posterior WHERE IdProducto=@IdProducto;
  INSERT dbo.Movimientos(IdProducto,IdUsuario,Tipo,Cantidad,Fecha,Motivo,StockAnterior,StockPosterior)
   VALUES(@IdProducto,@IdUsuario,@Tipo,@Cantidad,@Fecha,TRIM(@Motivo),@Anterior,@Posterior);
  COMMIT TRANSACTION;
  SELECT @Anterior AS StockAnterior,@Posterior AS StockPosterior;
 END TRY
 BEGIN CATCH
  IF @@TRANCOUNT>0 ROLLBACK TRANSACTION;
  THROW;
 END CATCH
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_movimiento_listar
 @IdProducto int=NULL,@Desde datetime2(0)=NULL,@Hasta datetime2(0)=NULL
AS
BEGIN
 SET NOCOUNT ON;
 SELECT m.IdMovimiento,m.IdProducto,p.Codigo,p.Nombre AS Producto,m.Tipo,m.Cantidad,
 m.Fecha,m.Motivo,m.StockAnterior,m.StockPosterior,u.Usuario
 FROM dbo.Movimientos m JOIN dbo.Productos p ON p.IdProducto=m.IdProducto
 JOIN dbo.Usuarios u ON u.IdUsuario=m.IdUsuario
 WHERE (@IdProducto IS NULL OR m.IdProducto=@IdProducto)
 AND (@Desde IS NULL OR m.Fecha>=@Desde)
 AND (@Hasta IS NULL OR m.Fecha<DATEADD(day,1,CONVERT(date,@Hasta)))
 ORDER BY m.Fecha DESC,m.IdMovimiento DESC;
END;
GO
CREATE OR ALTER PROCEDURE dbo.sp_indicadores
AS
BEGIN
 SET NOCOUNT ON;
 SELECT COUNT(*) AS ProductosActivos,
 COALESCE(SUM(CASE WHEN StockActual<=StockMinimo THEN 1 ELSE 0 END),0) AS ProductosStockBajo,
 COALESCE(SUM(StockActual*PrecioCompra),0) AS ValorInventario
 FROM dbo.Productos WHERE Activo=1;
END;
GO
