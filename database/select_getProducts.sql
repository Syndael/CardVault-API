SELECT
	c.id AS col_id, c.code AS col_code, c.is_manual AS man,
   CONCAT(IFNULL(ct.name_alter, ct.name), IF(ct.name_alter IS NULL, '', CONCAT(' (', ct.name, ')'))) AS col_name,
	p.product_number AS pro_num,	pt.name AS pro_name
FROM products p
INNER JOIN collections c ON c.id = p.collection_id
INNER JOIN product_translations pt ON pt.product_id = p.id
INNER JOIN languages lpt ON lpt.id = pt.language_id
INNER JOIN collection_translations ct ON ct.collection_id = c.id
INNER JOIN languages lct ON lct.id = ct.language_id
WHERE
	lpt.priority_order = (
		SELECT MIN(l2.priority_order)
		FROM product_translations pt2
		INNER JOIN languages l2 ON l2.id = pt2.language_id
		WHERE pt2.product_id = p.id
	)
	AND lct.priority_order = (
		SELECT MIN(l3.priority_order)
		FROM collection_translations ct2
		INNER JOIN languages l3 ON l3.id = ct2.language_id
		WHERE ct2.collection_id = c.id
	)
 ORDER BY 2, 3, 5, 6;
-- ORDER BY p.id DESC;
