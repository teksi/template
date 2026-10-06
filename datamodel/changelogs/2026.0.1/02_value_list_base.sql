CREATE TABLE temp_vl.value_list_base
(
code integer NOT NULL,
vsacode integer NOT NULL,
value_en character varying(100),
value_de character varying(100),
value_fr character varying(100),
value_it character varying(100),
value_ro character varying(100),
abbr_en character varying(3),
abbr_de character varying(3),
abbr_fr character varying(3),
abbr_it character varying(3),
abbr_ro character varying(3),
active boolean,
CONSTRAINT pkey_tww_value_list_code PRIMARY KEY (code)
)
WITH (
   OIDS = False
);