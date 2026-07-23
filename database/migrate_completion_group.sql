-- ============================================================
-- Migración: completion_group de VARCHAR a FK a types
-- Paso 1: Crear los tipos de completion_group en la tabla types
-- Paso 2: Añadir columna completion_group_id en products
-- Paso 3: Migrar datos de la columna antigua a la FK
-- Paso 4: Eliminar columna antigua y crear índices
-- ============================================================

-- PASO 1: Insertar los completion_groups como types
INSERT INTO types (name, short_name, type) VALUES
    ('Standard', 'STD', 'completion_group'),
    ('Reverse', 'REV', 'completion_group'),
    ('Holo', 'HOL', 'completion_group'),
    ('Secret', 'SEC', 'completion_group'),
    ('Alternativa', 'ALT', 'completion_group'),
    ('Optional', 'OPT', 'completion_group')
ON DUPLICATE KEY UPDATE short_name = VALUES(short_name);

-- PASO 2: Añadir la nueva columna FK
ALTER TABLE products
    ADD COLUMN completion_group_id INT NULL
    AFTER completion_group;

ALTER TABLE products
    ADD CONSTRAINT fk_product_completion_group
    FOREIGN KEY (completion_group_id) REFERENCES types(id)
    ON DELETE RESTRICT;

-- PASO 3: Migrar datos (los que no tengan coincidencia se quedan en NULL)
UPDATE products p
JOIN types t ON t.type = 'completion_group'
    AND (
        (p.completion_group = 'standard'   AND t.name = 'Standard')
        OR (p.completion_group = 'secret'  AND t.name = 'Secret')
        OR (p.completion_group = 'optional' AND t.name = 'Optional')
        OR (p.completion_group = 'reverse'  AND t.name = 'Reverse')
        OR (p.completion_group = 'holo'     AND t.name = 'Holo')
        OR (p.completion_group = 'alternativa' AND t.name = 'Alternativa')
    )
SET p.completion_group_id = t.id;

-- Los que quedaron en NULL ponerles Standard por defecto
UPDATE products
SET completion_group_id = (SELECT id FROM types WHERE type = 'completion_group' AND name = 'Standard')
WHERE completion_group_id IS NULL;

-- Hacer la columna NOT NULL
ALTER TABLE products
    MODIFY COLUMN completion_group_id INT NOT NULL;

-- PASO 4: Eliminar columna antigua y crear índices
ALTER TABLE products
    DROP COLUMN completion_group;

ALTER TABLE products
    ADD INDEX idx_products_completion_group (collection_id, completion_group_id);
