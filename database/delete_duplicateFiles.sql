SELECT product_id, language_id, original_name, stored_name, file_path, file_size, COUNT(*) FROM files WHERE product_id IS NOT NULL GROUP BY product_id, language_id, original_name, stored_name, file_path, file_size HAVING COUNT(*) > 1

DELETE FROM files WHERE ID IN (
	SELECT MAX(ID) FROM files WHERE product_id IS NOT NULL GROUP BY product_id, language_id, original_name, stored_name, file_path, file_size HAVING COUNT(*) > 1
);
