package com.jk.labs.vkp.indexing.wfs;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * pgVector store writer — writes into a per-model {@code vec_<model>} table using the SAME schema
 * the Airflow indexing DAG creates, so the AIRFLOW and SPRING_AI routes are interchangeable.
 */
@Component
@Slf4j
@RequiredArgsConstructor
public class PgVectorWriter implements VectorStoreWriter {

    /** Guards the table name interpolated into DDL/DML (never user free-text, but defensive). */
    private static final Pattern SAFE_TABLE = Pattern.compile("[a-z0-9_]{1,63}");

    private final JdbcTemplate jdbc;

    @Override
    public String store() {
        return "pgvector";
    }

    @Override
    @Transactional
    public void writeCompany(String table, int dim, String companyId, List<Row> rows) {
        if (!SAFE_TABLE.matcher(table).matches()) {
            throw new IllegalArgumentException("Unsafe vector table name: " + table);
        }
        jdbc.execute("CREATE EXTENSION IF NOT EXISTS vector");
        jdbc.execute("CREATE TABLE IF NOT EXISTS " + table + " ("
                + "id TEXT PRIMARY KEY, company_id TEXT, source_url TEXT, chunk_index INT, "
                + "chunk_text TEXT, embedding vector(" + dim + "))");
        // Full-text search support: a generated tsvector column + GIN index, so the vehicle-explore
        // service's fts/hybrid retrieval modes work over these rows without re-embedding. Generated
        // = Postgres maintains it automatically on insert/update.
        jdbc.execute("ALTER TABLE " + table + " ADD COLUMN IF NOT EXISTS content_tsv tsvector "
                + "GENERATED ALWAYS AS (to_tsvector('english', coalesce(chunk_text, ''))) STORED");
        jdbc.execute("CREATE INDEX IF NOT EXISTS " + table + "_tsv_gin ON " + table + " USING gin(content_tsv)");
        jdbc.update("DELETE FROM " + table + " WHERE company_id = ?", companyId);

        String sql = "INSERT INTO " + table
                + " (id, company_id, source_url, chunk_index, chunk_text, embedding) VALUES (?,?,?,?,?, ?::vector)";
        jdbc.batchUpdate(sql, rows, rows.size(), (ps, r) -> {
            ps.setString(1, UUID.randomUUID().toString().replace("-", ""));
            ps.setString(2, companyId);
            ps.setString(3, r.url());
            ps.setInt(4, r.chunkIndex());
            ps.setString(5, r.text());
            ps.setString(6, toVectorLiteral(r.embedding()));
        });
        log.info("Wrote {} vector row(s) into pgVector {} for company {}", rows.size(), table, companyId);
    }

    /** pgvector text input format: [v1,v2,...]. */
    private static String toVectorLiteral(float[] v) {
        StringBuilder sb = new StringBuilder(v.length * 8).append('[');
        for (int i = 0; i < v.length; i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(v[i]);
        }
        return sb.append(']').toString();
    }
}
