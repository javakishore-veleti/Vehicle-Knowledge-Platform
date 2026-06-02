# Vehicles / Ingestion DAGs

**Purpose:** iterate through each discovered link and fetch the **actual content**.

These DAGs read discovered links from the Company Resource graph, crawl each one, extract
the real content, and store it — to the local filesystem, AWS S3, or any other blob / file
server. Extracted content and its metadata are recorded (e.g. `company_resource_content`),
which downstream `Indexing` DAGs then chunk, embed, and index into the vector stores.

Place crawl/extraction DAG `.py` files in this folder (e.g. `vkp_process_resources.py`,
`vkp_extract_content.py`).
