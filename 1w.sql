ALTER TABLE invoices
ADD CONSTRAINT fk_nitcomprador
FOREIGN KEY (nitcomprador) REFERENCES comprador(nitcomprador)
ON DELETE RESTRICT;

