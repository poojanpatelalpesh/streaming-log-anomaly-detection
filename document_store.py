import pathway as pw

# Ingest troubleshooting docs
docs = pw.io.fs.read(
    path="./docs/",
    format="plaintext",
    mode="static"
)

#  Embed them into vectors (semantic search)
embedded_docs = pw.text.embedding.openai.Embedder("text-embedding-3-small").run(docs.data)

#  Store in Pathway's Document Store
store = pw.docstore.IndexedDocs(embedded_docs, id_col=docs.id, text_col=docs.data)

# Export the store for use by other scripts
store.save("./document_store/")
