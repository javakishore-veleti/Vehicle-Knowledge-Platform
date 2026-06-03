package com.jk.labs.vkp.indexing.wfs;

import com.mongodb.client.MongoCollection;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.bson.Document;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * MongoDB (Atlas Vector Search) store writer — writes one document per chunk into a per-model
 * collection ({@code vec_<model>}), with the embedding as a numeric array. A vectorSearch index
 * on {@code embedding} makes the collection queryable by Atlas Vector Search.
 */
@Component
@Slf4j
@RequiredArgsConstructor
public class MongoVectorWriter implements VectorStoreWriter {

    private final MongoTemplate mongo;

    @Override
    public String store() {
        return "mongodb";
    }

    @Override
    public void writeCompany(String collection, int dim, String companyId, List<Row> rows) {
        MongoCollection<Document> col = mongo.getCollection(collection);
        col.deleteMany(new Document("companyId", companyId));   // clean re-index for this company

        List<Document> docs = new ArrayList<>(rows.size());
        for (Row r : rows) {
            List<Double> embedding = new ArrayList<>(r.embedding().length);
            for (float f : r.embedding()) {
                embedding.add((double) f);
            }
            docs.add(new Document("_id", UUID.randomUUID().toString().replace("-", ""))
                    .append("companyId", companyId)
                    .append("sourceUrl", r.url())
                    .append("chunkIndex", r.chunkIndex())
                    .append("chunkText", r.text())
                    .append("dim", dim)
                    .append("embedding", embedding));
        }
        if (!docs.isEmpty()) {
            col.insertMany(docs);
        }
        log.info("Wrote {} vector doc(s) into MongoDB collection {} for company {}", docs.size(), collection, companyId);
    }
}
