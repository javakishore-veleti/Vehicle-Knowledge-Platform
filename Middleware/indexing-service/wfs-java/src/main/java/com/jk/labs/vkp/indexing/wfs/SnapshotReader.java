package com.jk.labs.vkp.indexing.wfs;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriUtils;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Reads a company's crawl-snapshot pages (and resolves selected doc PKs -> URLs) from
 * data-collection-service over HTTP — the same source the Airflow indexing DAG uses.
 */
@Component
@Slf4j
public class SnapshotReader {

    private static final int PAGE_LIMIT = 100;

    private final RestClient rest;

    public SnapshotReader(WfsProperties props) {
        this.rest = RestClient.builder().baseUrl(props.getDataCollectionBaseUrl()).build();
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Data
    public static class Page {
        private String url;
        private String text;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Data
    static class PagesResp {
        private List<Page> pages = new ArrayList<>();
        private int total;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Data
    static class Node {
        private String resourceGraphId;
        private String resourceUrl;
        private String resourceType;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Data
    static class GraphResp {
        private List<Node> nodes = new ArrayList<>();
    }

    /** All snapshot pages for a company (server-side paginated). */
    public List<Page> pages(String company) {
        List<Page> out = new ArrayList<>();
        int offset = 0;
        String enc = UriUtils.encodePathSegment(company, StandardCharsets.UTF_8);
        while (true) {
            PagesResp resp = rest.get()
                    .uri("/admin/data-collection/service/v1/snapshots/{c}/pages?offset={o}&limit={l}&full=true",
                            enc, offset, PAGE_LIMIT)
                    .retrieve().body(PagesResp.class);
            if (resp == null || resp.getPages().isEmpty()) {
                break;
            }
            out.addAll(resp.getPages());
            offset += PAGE_LIMIT;
            if (offset >= resp.getTotal()) {
                break;
            }
        }
        return out;
    }

    /** Map selected resource_graph PKs -> their URLs; null = whole-company (no filter). */
    public Set<String> allowedUrls(String companyId, List<String> docIds) {
        if (docIds == null || docIds.isEmpty()) {
            return null;
        }
        GraphResp resp = rest.get()
                .uri("/admin/data-collection/service/v1/companies/{id}/resource-graph", companyId)
                .retrieve().body(GraphResp.class);
        Set<String> wanted = Set.copyOf(docIds);
        return resp == null ? Set.of() : resp.getNodes().stream()
                .filter(n -> wanted.contains(n.getResourceGraphId()))
                .map(Node::getResourceUrl)
                .collect(Collectors.toSet());
    }
}
