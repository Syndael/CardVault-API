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
('card', 'Yu-Gi-Oh!', 'YUG');

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

INSERT INTO types (type, name) VALUES
('file', 'image'),
('file', 'invoice'),
('file', 'document'),
('entity', 'store'),
('entity', 'person'),
('entity', 'platform');

INSERT INTO roles (name, description) VALUES
('admin', 'Full application administration'),
('user', 'Standard application user'),
('product_read', 'Read-only access to product catalog'),
('product_write', 'Create, edit and delete products'),
('inventory_manage', 'Manage inventory and purchases');
