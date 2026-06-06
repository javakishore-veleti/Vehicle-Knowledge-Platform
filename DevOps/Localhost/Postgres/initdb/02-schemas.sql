-- VKP logical "databases" are SCHEMAS inside the single `postgres` database (one lean instance).
-- One schema per owning service/domain (all `vkp_`-prefixed), plus the shared `vkp_vectors` schema
-- for the embeddings table that indexing, explore and CEF all use. Services also CREATE SCHEMA IF NOT
-- EXISTS as a backstop (e.g. managed Postgres where this init script does not run).
CREATE SCHEMA IF NOT EXISTS vkp_company;          -- company-service: companies, company_resources
CREATE SCHEMA IF NOT EXISTS vkp_user;             -- user-service: customer_users
CREATE SCHEMA IF NOT EXISTS vkp_data_collection;  -- data-collection-service: company_resource_graph
CREATE SCHEMA IF NOT EXISTS vkp_ingestion;        -- ingestion-service: company_resource_content
CREATE SCHEMA IF NOT EXISTS vkp_indexing;         -- indexing-service: indexing_workflow, index_formula, ...
CREATE SCHEMA IF NOT EXISTS vkp_vector_config;    -- vector-config-service: company_resource_vector_config
CREATE SCHEMA IF NOT EXISTS vkp_guardrails;       -- guardrails-service: user_queries_*, search_feedback
CREATE SCHEMA IF NOT EXISTS vkp_explore;          -- vehicle-explore-service: veh_search_request_log
CREATE SCHEMA IF NOT EXISTS vkp_cef;              -- CEF: cef_chat_request_log, cef_strategy
CREATE SCHEMA IF NOT EXISTS vkp_vectors;          -- SHARED embeddings table (vec_*) used by index/explore/cef
