CREATE TABLE IF NOT EXISTS resultados (
    id     SERIAL PRIMARY KEY,
    clave  VARCHAR(100) NOT NULL,
    valor  NUMERIC(18,2) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resultados_clave ON resultados (clave);
