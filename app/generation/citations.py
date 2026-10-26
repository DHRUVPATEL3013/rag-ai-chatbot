def format_sources(documents: list) -> list:
    """Extract source information from retrieved documents."""

    sources = []

    for document in documents:
        metadata = document.metadata

        source = metadata.get("source", "Unknown source")
        page = metadata.get("page")

        if page is not None:
            page = page + 1

        sources.append(
            {
                "source": source,
                "page": page,
            }
        )

    return sources