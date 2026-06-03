package com.jk.labs.vkp.indexing.wfs;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.transformers.TransformersEmbeddingModel;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Real Spring-AI indexing executor. Runs async: reads the company's snapshot pages from
 * data-collection, chunks + embeds them with Spring AI's local ONNX
 * {@link TransformersEmbeddingModel} (sentence-transformers/all-MiniLM-L6-v2, 384d), writes the
 * vectors into the per-model {@code vec_<model>} pgVector table (same schema as the Airflow
 * route), and reports terminal status back to the control plane.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SpringAiExecutor {

    private final WfsControlClient control;
    private final SnapshotReader snapshots;
    private final VectorWriter vectors;
    private final TransformersEmbeddingModel embeddingModel;
    private final WfsProperties props;
    private final ObjectMapper mapper = new ObjectMapper();

    @Async
    public void execute(String executorId, String indexLogId, Map<String, Object> rp) {
        // The control plane already marked this log IN_PROGRESS before invoking the executor, so we
        // only report the terminal status here (avoids racing its not-yet-committed trigger txn).
        String runRef = "wfs-" + indexLogId;
        log.info("Executor '{}' starting for log {} (company={})", executorId, indexLogId, rp.get("companyName"));
        try {
            String companyId = str(rp, "companyId");
            String companyName = str(rp, "companyName");
            String vectorTarget = orDefault(str(rp, "vectorTarget"), "vec_default");
            int chunkSize = props.getChunkSize();
            int chunkOverlap = props.getChunkOverlap();
            int dim = props.getDim();
            JsonNode params = parseParams(str(rp, "params"));
            if (params != null) {
                chunkSize = params.path("chunk_size").asInt(chunkSize);
                chunkOverlap = params.path("chunk_overlap").asInt(chunkOverlap);
                dim = params.path("dim").asInt(dim);
            }

            @SuppressWarnings("unchecked")
            List<String> docIds = (List<String>) rp.getOrDefault("docIds", List.of());
            Set<String> allowed = snapshots.allowedUrls(companyId, docIds);

            List<SnapshotReader.Page> pages = snapshots.pages(companyName);
            if (allowed != null) {
                pages = pages.stream().filter(p -> allowed.contains(p.getUrl())).toList();
                log.info("Doc selection: {} page(s) match {} selected id(s)", pages.size(), allowed.size());
            } else {
                log.info("Whole-company scope: {} snapshot page(s)", pages.size());
            }

            List<String> texts = new ArrayList<>();
            List<VectorWriter.Row> rows = new ArrayList<>();
            for (SnapshotReader.Page p : pages) {
                List<String> chunks = chunk(p.getText(), chunkSize, chunkOverlap);
                for (int ci = 0; ci < chunks.size(); ci++) {
                    texts.add(chunks.get(ci));
                    rows.add(new VectorWriter.Row(p.getUrl(), ci, chunks.get(ci), null));
                }
            }
            if (rows.isEmpty()) {
                control.callback(indexLogId, "INDEXED", 0, null, runRef);
                log.info("Nothing to index for '{}' (log {})", companyName, indexLogId);
                return;
            }

            List<float[]> embeddings = embeddingModel.embed(texts);
            List<VectorWriter.Row> finalRows = new ArrayList<>(rows.size());
            for (int i = 0; i < rows.size(); i++) {
                VectorWriter.Row r = rows.get(i);
                finalRows.add(new VectorWriter.Row(r.url(), r.chunkIndex(), r.text(), embeddings.get(i)));
            }
            vectors.writeCompany(vectorTarget, dim, companyId, finalRows);

            control.callback(indexLogId, "INDEXED", finalRows.size(), null, runRef);
            log.info("Executor '{}' indexed {} chunk(s) into {} for log {}",
                    executorId, finalRows.size(), vectorTarget, indexLogId);
        } catch (Exception e) {  // noqa: BLE001
            log.error("Executor '{}' failed for log {}", executorId, indexLogId, e);
            control.callback(indexLogId, "FAILED", null, e.getMessage(), runRef);
        }
    }

    private static List<String> chunk(String text, int size, int overlap) {
        List<String> out = new ArrayList<>();
        if (text == null || text.isBlank()) {
            return out;
        }
        int step = Math.max(1, size - overlap);
        for (int i = 0; i < text.length(); i += step) {
            String c = text.substring(i, Math.min(text.length(), i + size));
            if (!c.isBlank()) {
                out.add(c);
            }
        }
        return out;
    }

    private JsonNode parseParams(String params) {
        if (params == null || params.isBlank()) {
            return null;
        }
        try {
            return mapper.readTree(params);
        } catch (Exception e) {  // noqa: BLE001
            log.warn("Could not parse formula params '{}': {}", params, e.getMessage());
            return null;
        }
    }

    private static String str(Map<String, Object> m, String k) {
        Object v = m.get(k);
        return v == null ? null : v.toString();
    }

    private static String orDefault(String v, String def) {
        return v == null || v.isBlank() ? def : v;
    }
}
