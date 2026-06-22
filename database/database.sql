CREATE DATABASE IF NOT EXISTS card_collection;
USE card_collection;

CREATE TABLE types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(20) NOT NULL,
  name VARCHAR(100) NOT NULL,
  short_name VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_type_name
    UNIQUE (type, name)
);

CREATE TABLE collections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  card_type_id INT NOT NULL,
  code VARCHAR(50) NOT NULL,
  is_manual BIT NOT NULL DEFAULT b'0',
  release_date DATE,
  force_url VARCHAR(500) DEFAULT NULL,
  force_download BIT NOT NULL DEFAULT b'0',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_collections_card_type
    FOREIGN KEY (card_type_id)
    REFERENCES types(id)
    ON DELETE RESTRICT,

  CONSTRAINT uq_type_code_manual
    UNIQUE (card_type_id, code, is_manual)
);

CREATE INDEX idx_collections_card_type ON collections(card_type_id);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  collection_id INT NOT NULL,
  product_type_id INT NOT NULL,
  product_format_id INT NOT NULL,
  product_number VARCHAR(50) NULL,
  is_manual BIT(1) NOT NULL DEFAULT b'0',
  is_verified BIT NOT NULL DEFAULT b'0',
  force_download BIT NULL DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_products_collection
    FOREIGN KEY (collection_id)
    REFERENCES collections(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_products_type
    FOREIGN KEY (product_type_id)
    REFERENCES types(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_products_format
    FOREIGN KEY (product_format_id)
    REFERENCES types(id)
    ON DELETE RESTRICT,

  CONSTRAINT uq_collection_product
    UNIQUE (collection_id, product_number, product_type_id, product_format_id, is_manual)
);

CREATE INDEX idx_products_collection ON products(collection_id);

CREATE TABLE entities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  url VARCHAR(500),
  entity_type INT NOT NULL,
  parent_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_entities_parent
    FOREIGN KEY (parent_id)
    REFERENCES entities(id)
    ON DELETE RESTRICT
);

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL,
  email VARCHAR(255) NULL,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(150) NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_login_at DATETIME NULL,
  password_changed_at DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT uq_users_username UNIQUE (username),
  CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX idx_users_active ON users(is_active);

CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  description VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_roles_name UNIQUE (name)
);

CREATE TABLE user_roles (
  user_id INT NOT NULL,
  role_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (user_id, role_id),

  CONSTRAINT fk_user_roles_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_user_roles_role
    FOREIGN KEY (role_id)
    REFERENCES roles(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_user_roles_role ON user_roles(role_id);

CREATE TABLE user_sessions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token_hash CHAR(64) NOT NULL,
  user_agent VARCHAR(255) NULL,
  ip_address VARCHAR(45) NULL,
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_user_sessions_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

  CONSTRAINT uq_user_sessions_token_hash UNIQUE (token_hash)
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

CREATE TABLE purchases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  entity_id INT NOT NULL,
  purchase_date DATETIME NULL,
  total_amount DECIMAL(10,2) NULL,
  shipping_cost DECIMAL(10,2) DEFAULT 0,
  currency VARCHAR(10) DEFAULT 'EUR',
  conversion_rate DECIMAL(10,4) NULL,
  original_amount DECIMAL(10,2) NULL,
  original_currency VARCHAR(10) NULL,
  external_reference VARCHAR(255) NULL,
  tracking_code VARCHAR(255) NULL,
  shipping_status_id INT NULL,
  shipping_company_id INT NULL,
  notes TEXT,
  user_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_purchases_entity
    FOREIGN KEY (entity_id)
    REFERENCES entities(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_purchases_shipping_status
    FOREIGN KEY (shipping_status_id)
    REFERENCES types(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_purchases_shipping_company
    FOREIGN KEY (shipping_company_id)
    REFERENCES entities(id)
    ON DELETE RESTRICT
);

CREATE TABLE purchase_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  purchase_id INT NOT NULL,
  product_id INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  conversion_rate DECIMAL(10,4) NULL,
  original_unit_price DECIMAL(10,2) NULL,
  original_currency VARCHAR(10) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_purchase_items_purchase
    FOREIGN KEY (purchase_id)
    REFERENCES purchases(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_purchase_items_product_id
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT
);

CREATE TABLE languages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  abbreviation VARCHAR(10) NOT NULL,
  cardmarket_code VARCHAR(10),
  tcgdex_language_code VARCHAR(10) NULL DEFAULT NULL,
  priority_order INT NOT NULL DEFAULT 999,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_languages_name UNIQUE (name),
  CONSTRAINT uq_languages_abbr UNIQUE (abbreviation)
);

CREATE TABLE product_conditions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  abbreviation VARCHAR(10) NOT NULL,
  cardmarket_code VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_conditions_name UNIQUE (name),
  CONSTRAINT uq_conditions_abbr UNIQUE (abbreviation)
);

CREATE TABLE inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  collection_id INT NOT NULL,
  user_id INT NOT NULL,
  extra_type_id INT,
  purchase_id INT,
  purchase_item_id INT,
  quantity INT DEFAULT 1,
  is_sealed BOOLEAN DEFAULT FALSE,
  posted_instagram BOOLEAN DEFAULT FALSE,
  language_id INT,
  condition_id INT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_inventory_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_collection
    FOREIGN KEY (collection_id)
    REFERENCES collections(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_extra_type
    FOREIGN KEY (extra_type_id)
    REFERENCES types(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_language
    FOREIGN KEY (language_id)
    REFERENCES languages(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_condition
    FOREIGN KEY (condition_id)
    REFERENCES product_conditions(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_purchase
    FOREIGN KEY (purchase_id)
    REFERENCES purchases(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_purchase_item
    FOREIGN KEY (purchase_item_id)
    REFERENCES purchase_items(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inventory_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_collection ON inventory(collection_id);
CREATE INDEX fk_inventory_purchase_item ON inventory(purchase_item_id);
CREATE INDEX idx_inventory_user ON inventory(user_id);

CREATE TABLE files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NULL,
  inventory_id INT NULL,
  purchase_id INT NULL,
  language_id INT NULL,
  original_name VARCHAR(255) NOT NULL,
  stored_name VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_type_id INT,
  file_size INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_files_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_files_purchase
    FOREIGN KEY (purchase_id)
    REFERENCES purchases(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_files_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_files_language
    FOREIGN KEY (language_id)
    REFERENCES languages(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_files_file_type
    FOREIGN KEY (file_type_id)
    REFERENCES types(id)
    ON DELETE RESTRICT
);

CREATE TABLE price_sources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  base_url VARCHAR(500),
  language_param VARCHAR(50),
  condition_param VARCHAR(50)
);

CREATE TABLE product_price_tracking (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  price_source_id INT NOT NULL,
  url VARCHAR(500) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_tracking_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_tracking_source
    FOREIGN KEY (price_source_id)
    REFERENCES price_sources(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_tracking_product ON product_price_tracking(product_id);

CREATE TABLE inventory_price_history (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  inventory_id INT NOT NULL,
  product_price_tracking_id INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  min_price DECIMAL(10,2) NULL,
  max_price DECIMAL(10,2) NULL,
  min_price_recorded_at TIMESTAMP NULL,
  max_price_recorded_at TIMESTAMP NULL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_price_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_price_product
    FOREIGN KEY (product_price_tracking_id)
    REFERENCES product_price_tracking(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_history_inventory ON inventory_price_history(inventory_id);
CREATE INDEX idx_history_recorded_at ON inventory_price_history(recorded_at);

CREATE TABLE inventory_price_history_archive (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  inventory_id INT NOT NULL,
  product_price_tracking_id INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  min_price DECIMAL(10,2) NULL,
  max_price DECIMAL(10,2) NULL,
  min_price_recorded_at TIMESTAMP NULL,
  max_price_recorded_at TIMESTAMP NULL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_price_archive_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_price_archive_product
    FOREIGN KEY (product_price_tracking_id)
    REFERENCES product_price_tracking(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_archive_inventory ON inventory_price_history_archive(inventory_id);
CREATE INDEX idx_archive_recorded_at ON inventory_price_history_archive(recorded_at);
CREATE INDEX idx_archive_archived_at ON inventory_price_history_archive(archived_at);

CREATE TABLE product_translations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  language_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  name_alter VARCHAR(255) NULL DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_pt_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_pt_language
    FOREIGN KEY (language_id)
    REFERENCES languages(id)
    ON DELETE RESTRICT,

  CONSTRAINT uq_product_lang
    UNIQUE (product_id, language_id),

  FULLTEXT INDEX ft_product_translations_name (name, name_alter)
);

CREATE TABLE collection_translations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  collection_id INT NOT NULL,
  language_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  name_alter VARCHAR(255) NULL DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_coll_t_collection
    FOREIGN KEY (collection_id)
    REFERENCES collections(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_coll_t_language
    FOREIGN KEY (language_id)
    REFERENCES languages(id)
    ON DELETE RESTRICT,

  CONSTRAINT uq_collection_lang
    UNIQUE (collection_id, language_id),

  FULLTEXT INDEX ft_collection_translations_name (name, name_alter)
);

CREATE TABLE settings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  setting_key VARCHAR(150) NOT NULL,
  setting_value TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT uq_settings_key
    UNIQUE (setting_key)
);

CREATE TABLE tags (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  color      VARCHAR(7)   NULL DEFAULT NULL,
  created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_tag_name UNIQUE (name)
);

CREATE TABLE inventory_tags (
  inventory_id INT NOT NULL,
  tag_id       INT NOT NULL,
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (inventory_id, tag_id),

  CONSTRAINT fk_inv_tags_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_inv_tags_tag
    FOREIGN KEY (tag_id)
    REFERENCES tags(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_inventory_tags_tag ON inventory_tags(tag_id);

CREATE TABLE scheduled_tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  script_path VARCHAR(500) NOT NULL,
  cron_expression VARCHAR(100) NULL,
  enabled BIT NOT NULL DEFAULT b'1',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_executions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  scheduled_task_id INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  scheduled_date DATETIME NOT NULL,
  started_at DATETIME,
  finished_at DATETIME,
  output TEXT,
  log_file_path VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_executions_task
    FOREIGN KEY (scheduled_task_id)
    REFERENCES scheduled_tasks(id)
    ON DELETE CASCADE,

  INDEX idx_executions_status_date (status, scheduled_date),
  INDEX idx_executions_task (scheduled_task_id)
);

CREATE TABLE inventory_urls (
  id INT AUTO_INCREMENT PRIMARY KEY,
  inventory_id INT NOT NULL,
  url VARCHAR(500) NOT NULL,
  name VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_urls_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventory(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_inventory_urls_inventory ON inventory_urls(inventory_id);
CREATE INDEX idx_collections_code_manual ON collections(code, is_manual);
CREATE INDEX idx_products_type_collection ON products(product_type_id, collection_id);
CREATE INDEX idx_files_product_language_id ON files(product_id, language_id, id);

ALTER TABLE purchases ADD COLUMN delivery_date DATETIME NULL AFTER purchase_date;

ALTER TABLE users ADD COLUMN telegram_id VARCHAR(100) NULL AFTER is_email_verified;

CREATE TABLE wishlist_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  target_price DECIMAL(10,2) NULL,
  language_id INT NULL,
  condition_id INT NULL,
  notes TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_wishlist_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_wishlist_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_wishlist_language
    FOREIGN KEY (language_id)
    REFERENCES languages(id)
    ON DELETE RESTRICT,

  CONSTRAINT fk_wishlist_condition
    FOREIGN KEY (condition_id)
    REFERENCES product_conditions(id)
    ON DELETE RESTRICT
);

CREATE INDEX idx_wishlist_user ON wishlist_items(user_id);
CREATE INDEX idx_wishlist_product ON wishlist_items(product_id);

CREATE TABLE wishlist_prices (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  wishlist_item_id INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  source VARCHAR(100) NULL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_wishlist_prices_item
    FOREIGN KEY (wishlist_item_id)
    REFERENCES wishlist_items(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_wishlist_prices_item ON wishlist_prices(wishlist_item_id);
CREATE INDEX idx_wishlist_prices_recorded ON wishlist_prices(recorded_at);

CREATE TABLE wishlist_notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  wishlist_item_id INT NOT NULL,
  notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  type VARCHAR(20) NOT NULL DEFAULT 'email',
  price DECIMAL(10,2) NOT NULL,

  CONSTRAINT fk_wishlist_notifications_item
    FOREIGN KEY (wishlist_item_id)
    REFERENCES wishlist_items(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_wishlist_notifications_item ON wishlist_notifications(wishlist_item_id);
CREATE INDEX idx_wishlist_notifications_type ON wishlist_notifications(type);

ALTER TABLE wishlist_prices
  ADD COLUMN min_price DECIMAL(10,2) NULL AFTER price,
  ADD COLUMN max_price DECIMAL(10,2) NULL AFTER min_price,
  ADD COLUMN min_price_recorded_at TIMESTAMP NULL AFTER max_price,
  ADD COLUMN max_price_recorded_at TIMESTAMP NULL AFTER min_price_recorded_at;

ALTER TABLE wishlist_items
  ADD COLUMN w_state VARCHAR(20) NOT NULL DEFAULT 'buscando'
  AFTER condition_id;

CREATE INDEX idx_wishlist_w_state ON wishlist_items(w_state);
