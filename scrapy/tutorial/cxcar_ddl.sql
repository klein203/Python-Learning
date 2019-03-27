-- Database: scrapy_db
-- DROP DATABASE scrapy_db;
CREATE DATABASE scrapy_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Chinese (Simplified)_People''s Republic of China.936'
    LC_CTYPE = 'Chinese (Simplified)_People''s Republic of China.936'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

    
-- User: scrapy_user
-- DROP USER scrapy_user;
CREATE USER scrapy_user WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION;

COMMENT ON ROLE scrapy_user IS 'pwd:scrapy';


-- SEQUENCE: public.t_cxcar_id_seq
-- DROP SEQUENCE public.t_cxcar_id_seq;
CREATE SEQUENCE public.t_cxcar_id_seq;

ALTER SEQUENCE public.t_cxcar_id_seq
    OWNER TO scrapy_user;


-- Table: public.t_cxcar
-- DROP TABLE public.t_cxcar;
CREATE TABLE public.t_cxcar
(
    id bigint NOT NULL DEFAULT nextval('t_cxcar_id_seq'::regclass),
    series_name character varying(50) COLLATE pg_catalog."default",
    model_name character varying(80) COLLATE pg_catalog."default",
    price character varying(20) COLLATE pg_catalog."default",
    price_num numeric(10,2),
    create_timestamp timestamp without time zone,
    update_timestamp timestamp without time zone,
    CONSTRAINT t_cxcar_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.t_cxcar
    OWNER to scrapy_user;