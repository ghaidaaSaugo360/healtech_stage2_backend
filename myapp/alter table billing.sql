alter table billing
drop column invoice_number;
alter table billing
drop column invoice_date;
alter table billing
drop column invoice_amount;

ALTER TABLE billing
add column invoice_number varchar(20) NULL;
ALTER TABLE billing 
ADD COLUMN invoice_date date NULL;
ALTER TABLE billing 
add column invoice_amount decimal (10,2) NULL;