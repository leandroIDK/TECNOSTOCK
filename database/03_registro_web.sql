SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
GO
USE TecnoStock;
GO
-- Conserva los usuarios existentes; sus datos nuevos quedan vacíos hasta que se actualicen.
IF COL_LENGTH(N'dbo.Usuarios', N'Apellido') IS NULL
    ALTER TABLE dbo.Usuarios ADD Apellido nvarchar(120) NULL;
IF COL_LENGTH(N'dbo.Usuarios', N'Dni') IS NULL
    ALTER TABLE dbo.Usuarios ADD Dni char(8) NULL;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID(N'dbo.Usuarios') AND name = N'UX_Usuarios_Dni')
    CREATE UNIQUE INDEX UX_Usuarios_Dni ON dbo.Usuarios(Dni) WHERE Dni IS NOT NULL;
GO
CREATE OR ALTER PROCEDURE dbo.sp_usuario_registrar
 @Dni char(8), @Nombre nvarchar(120), @Apellido nvarchar(120),
 @Usuario nvarchar(80), @HashContrasena nvarchar(255)
AS
BEGIN
 SET NOCOUNT ON;
 IF @Dni IS NULL OR @Dni NOT LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
    THROW 50009, 'El DNI debe tener ocho digitos.', 1;
 IF NULLIF(TRIM(@Nombre), N'') IS NULL OR NULLIF(TRIM(@Apellido), N'') IS NULL
    OR NULLIF(TRIM(@Usuario), N'') IS NULL OR NULLIF(@HashContrasena, N'') IS NULL
    THROW 50010, 'Faltan datos obligatorios del usuario.', 1;
 INSERT dbo.Usuarios(Dni, Nombre, Apellido, Usuario, HashContrasena)
 VALUES(@Dni, TRIM(@Nombre), TRIM(@Apellido), TRIM(@Usuario), @HashContrasena);
 SELECT IdUsuario, Dni, Nombre, Apellido, Usuario
 FROM dbo.Usuarios WHERE IdUsuario = SCOPE_IDENTITY();
END;
GO
