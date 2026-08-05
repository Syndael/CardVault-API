-- ============================================================
-- Migración: Publicaciones con múltiples inventarios y compras
-- ============================================================

-- 1. Tablas de cruce N:M
CREATE TABLE publication_inventory (
  publication_id INT NOT NULL,
  inventory_id   INT NOT NULL,
  PRIMARY KEY (publication_id, inventory_id),
  CONSTRAINT fk_pub_inv_pub
    FOREIGN KEY (publication_id)
    REFERENCES publication_schedule(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_pub_inv_inv
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT,
  INDEX idx_pub_inv_inv (inventory_id)
);

CREATE TABLE publication_purchases (
  publication_id INT NOT NULL,
  purchase_id    INT NOT NULL,
  PRIMARY KEY (publication_id, purchase_id),
  CONSTRAINT fk_pub_pur_pub
    FOREIGN KEY (publication_id)
    REFERENCES publication_schedule(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_pub_pur_pur
    FOREIGN KEY (purchase_id)
    REFERENCES purchases(id)
    ON DELETE RESTRICT,
  INDEX idx_pub_pur_pur (purchase_id)
);

-- 2. FK publication_id en files (subida directa)
ALTER TABLE files
  ADD COLUMN publication_id INT NULL AFTER purchase_id,
  ADD CONSTRAINT fk_files_publication
    FOREIGN KEY (publication_id)
    REFERENCES publication_schedule(id)
    ON DELETE SET NULL,
  ADD INDEX idx_files_publication (publication_id);

-- 3. Migrar datos existentes (1:1 → N:M)
INSERT INTO publication_inventory (publication_id, inventory_id)
  SELECT id, inventory_id
  FROM publication_schedule
  WHERE inventory_id IS NOT NULL;

-- 4. Eliminar la FK y columna inventory_id de publication_schedule
ALTER TABLE publication_schedule
  DROP FOREIGN KEY fk_publication_inventory;

ALTER TABLE publication_schedule
  DROP COLUMN inventory_id;

-- 5. Añadir columna title a publication_schedule
ALTER TABLE publication_schedule
  ADD COLUMN title VARCHAR(255) NULL AFTER id;
