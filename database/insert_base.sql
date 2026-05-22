INSERT INTO types (type, name, short_name) VALUES
('card', 'Digimon TCG', 'DIG'),
('card', 'Dragon Ball CG', 'DBC'),
('card', 'Dragon Ball Heroes', 'DBH'),
('card', 'Final Fantasy', 'FF'),
('card', 'Flesh and Blood', 'FB'),
('card', 'Magic', 'MTG'),
('card', 'MetaZoo', 'MZ'),
('card', 'One Piece CG', 'OP'),
('card', 'Pokémon TCG', 'POK'),
('card', 'Vanguard', 'VAN'),
('card', 'Weiss Schwarz', 'WS'),
('card', 'World of Warcraft TCG', 'WOW'),
('card', 'Yu-Gi-Oh!', 'YUG'),
('file', 'image'),
('file', 'invoice'),
('file', 'document'),
('entity', 'store'),
('entity', 'person'),
('entity', 'platform');

INSERT INTO price_sources (
  name,
  base_url,
  language_param,
  condition_param
) VALUES (
  'CardMarket',
  'https://www.cardmarket.com',
  'language',
  'minCondition'
);

INSERT INTO languages (
  name,
  abbreviation,
  cardmarket_code,
  tcgdex_language_code,
  priority_order
) VALUES
('Español', 'ES', '4', 'es', 1),
('Inglés', 'EN', '1', 'en', 2),
('Japonés', 'JP', '7', 'ja', 3),
('Koreano', 'KR', '10', 'ko', 4),
('Alemán', 'DE', '3', 'de', 5),
('Francés', 'FR', '2', 'fr', 6),
('Italiano', 'IT', '5', 'it', 7),
('Portugués', 'PT', '8', 'pt', 8);

INSERT INTO product_conditions (
  name,
  abbreviation,
  cardmarket_code
) VALUES
('Mint', 'M', '1'),
('Near Mint', 'NM', '2'),
('Excellent', 'EX', '3'),
('Good', 'GD', '4'),
('Light Played', 'LP', '5'),
('Played', 'PL', '6'),
('Poor', 'PR', '7');

INSERT INTO roles (name, description) VALUES
('admin', 'Full application administration'),
('user', 'Standard application user'),
('product_read', 'Read-only access to product catalog'),
('product_write', 'Create, edit and delete products'),
('inventory_manage', 'Manage inventory and purchases'),
('collection_read', 'Read-only access to collections'),
('collection_write', 'Create, edit and delete collections'),
('scheduled_task_read', 'View scheduled tasks and executions'),
('scheduled_task_write', 'Create, edit and delete scheduled tasks and executions');

INSERT INTO settings (setting_key, setting_value) VALUES
('sync.pokemon.collections.api.base', 'https://api.tcgdex.net/v2'),
('sync.pokemon.collections.card.type', 'POK'),
('sync.pokemon.collections.migration.languages', 'en-EN;es-ES;ja-JP;de-DE;ko-KR;fr-FR;it-IT;pt-PT;'),
('sync.pokemon.products.api.base', 'https://api.tcgdex.net/v2'),
('sync.pokemon.products.card.type', 'POK'),
('sync.pokemon.products.migration.languages', 'en;es;ja;ko;de;'),
('sync.pokemon.products.files.path', './../.files/products_images'),
('bot.telegram.allowed.ids', ''),
('bot.telegram.admin.ids', ''),
('app.inventory.files.path', './../.files/inventory'),
('app.inventory.files.path.pattern', '{card_type}/{collection_code}/{product_number}/{inventory_id}'),
('app.purchase.files.path', './../.files/purchases'),
('app.purchase.files.path.pattern', '{year}/{month}/{purchase_id}');
