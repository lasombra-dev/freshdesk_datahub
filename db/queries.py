# Las queries pa hacer el MERGE de los datos

MERGE_CONTACTS = """
    MERGE Contactos AS target
    USING (SELECT ? AS ID, ? AS NombreCompleto, ? AS Correo) AS source
    ON target.ID = source.ID
    WHEN MATCHED THEN
        UPDATE SET NombreCompleto = source.NombreCompleto, Correo = source.Correo
    WHEN NOT MATCHED THEN
        INSERT (ID, NombreCompleto, Correo)
        VALUES (source.ID, source.NombreCompleto, source.Correo);
"""

MERGE_COMPANIES = """
    MERGE Empresas AS target
    USING (SELECT ? AS ID, ? AS NombreEmpresa) AS source
    ON target.ID = source.ID
    WHEN MATCHED THEN
        UPDATE SET NombreEmpresa = source.NombreEmpresa
    WHEN NOT MATCHED THEN
        INSERT (ID, NombreEmpresa)
        VALUES (source.ID, source.NombreEmpresa);
"""

MERGE_AGENTS = """
    MERGE Agentes AS target
    USING (SELECT ? AS ID, ? AS Nombre, ? AS Correo) AS source
    ON target.ID = source.ID
    WHEN MATCHED THEN
        UPDATE SET Nombre = source.Nombre, Correo = source.Correo
    WHEN NOT MATCHED THEN
        INSERT (ID, Nombre, Correo)
        VALUES (source.ID, source.Nombre, source.Correo);
"""

MERGE_TICKETS = """
    MERGE Tickets AS target
    USING (SELECT ? AS ID, ? AS Asunto, ? AS Estado, ? AS Prioridad, ? AS Tipo, 
                  ? AS Subtipo, ? AS CF_Empresa, ? AS Agente, ? AS TiempoCreacion, 
                  ? AS TiempoResolucion, ? AS RequesterID, ? AS CompanyID, ? AS Etiquetas) AS source
    ON target.ID = source.ID
    WHEN MATCHED THEN
        UPDATE SET Asunto = source.Asunto, Estado = source.Estado, Prioridad = source.Prioridad,
                   Tipo = source.Tipo, Subtipo = source.Subtipo, CF_Empresa = source.CF_Empresa,
                   Agente = source.Agente, TiempoCreacion = source.TiempoCreacion,
                   TiempoResolucion = source.TiempoResolucion, RequesterID = source.RequesterID,
                   CompanyID = source.CompanyID, Etiquetas = source.Etiquetas
    WHEN NOT MATCHED THEN
        INSERT (ID, Asunto, Estado, Prioridad, Tipo, Subtipo, CF_Empresa, Agente, 
                TiempoCreacion, TiempoResolucion, RequesterID, CompanyID, Etiquetas)
        VALUES (source.ID, source.Asunto, source.Estado, source.Prioridad, source.Tipo,
                source.Subtipo, source.CF_Empresa, source.Agente, source.TiempoCreacion,
                source.TiempoResolucion, source.RequesterID, source.CompanyID, source.Etiquetas);
"""
