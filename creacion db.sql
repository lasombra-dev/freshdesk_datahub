-- Tabla de Contactos
CREATE TABLE Contactos (
    ID BIGINT PRIMARY KEY,                -- ID único del contacto
    NombreCompleto NVARCHAR(100),         -- Nombre completo del contacto
    Correo NVARCHAR(100)                  -- Correo del contacto
);

-- Tabla de Empresas
CREATE TABLE Empresas (
    ID BIGINT PRIMARY KEY,                -- ID único de la empresa
    NombreEmpresa NVARCHAR(100)           -- Nombre de la empresa
);

-- Tabla de Sincronización
CREATE TABLE Sincronizacion (
    EntityFreshdesk NVARCHAR(50) PRIMARY KEY,   -- Nombre de la entidad sincronizada (ej. "tickets", "contactos", etc.)
    LastUpdate DATETIME                          -- Última fecha de sincronización
);

-- Tabla de Agentes
CREATE TABLE Agentes (
    ID BIGINT PRIMARY KEY,                -- ID único del agente
    Nombre NVARCHAR(100),                 -- Nombre completo del agente
    Correo NVARCHAR(100),                 -- Correo electrónico del agente
);

-- Tabla de Tickets
CREATE TABLE Tickets (
    ID BIGINT PRIMARY KEY,                -- ID único del ticket
    Asunto NVARCHAR(255),                 -- Asunto del ticket
    Estado NVARCHAR(50),                  -- Estado del ticket
    Prioridad NVARCHAR(50),               -- Prioridad del ticket
    Tipo NVARCHAR(50),                    -- Tipo del ticket
    Subtipo NVARCHAR(100),                -- Subtipo del ticket
    Agente BIGINT,                        -- Agente asignado (clave foránea)
    TiempoCreacion DATETIME,              -- Fecha de creación del ticket
    TiempoResolucion DATETIME,            -- Fecha límite para resolver el ticket
    RequesterID BIGINT,                   -- ID del contacto que creó el ticket (clave foránea)
    CompanyID BIGINT,                     -- ID de la empresa asociada al ticket (clave foránea)
    Etiquetas NVARCHAR(255),              -- Etiquetas asociadas al ticket
    FOREIGN KEY (RequesterID) REFERENCES Contactos(ID), -- Relación con Contactos
    FOREIGN KEY (CompanyID) REFERENCES Empresas(ID),   -- Relación con Empresas
    FOREIGN KEY (Agente) REFERENCES Agentes(ID)        -- Relación con Agentes
);


ALTER TABLE Agentes NOCHECK CONSTRAINT ALL;
TRUNCATE TABLE Agentes;
ALTER TABLE Agentes CHECK CONSTRAINT ALL;