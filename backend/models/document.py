class Document:
    def __init__(self, 
                 ids,
                 tags, 
                 tags_metadata, 
                 content, 
                 content_metadata) -> None:
        self.ids = ids
        self.tags = tags
        self.tags_metadata = tags_metadata
        self.content = content
        self.content_metadata = content_metadata