import chromadb
from models.document import Document

class DocumentDao:

    def __init__(self, path) -> None:
        client = chromadb.PersistentClient(path = path)
        self.tag_db = client.get_or_create_collection(name="tag_collection",metadata={"hnsw:space": "cosine"})        
        self.content_db = client.get_or_create_collection(name="content_collection",metadata={"hnsw:space": "cosine"})


    def retrieve_similar(self, db, query, threshold = 0.7):
        """Takes in list of query texts and returns list of docs"""
        results = db.query(query_texts = [query])
        for ind in range(len(results['distances'][0])):
            dist = results['distances'][0][ind]
            if dist > threshold:
                results['ids'][0] = results['ids'][0][:ind]
                results['distances'][0] = results['distances'][0][:ind]
                results['metadatas'][0] = results['metadatas'][0][:ind]
                results['documents'][0] = results['documents'][0][:ind]
                break
        if len(results['ids'][0]) > 0:
            return results
        else:
            return None
        

    def retrieve_by_tags(self, query):
        return self.retrieve_similar(self.tags_db, query)
    
    def retrieve_by_content(self, query):
        return self.retrieve_similar(self.content_db, query)

    def store_document(self, document: Document):
        self.tag_db.add(documents = document.tags, ids=document.ids, metadatas = document.tags_metadata)
        self.content_db.add(documents = document.content, ids=document.ids, metadatas = document.content_metadata)
        
    def remove_document(self, ids):
        self.content_db.delete(ids = ids)
        self.tag_db.delete(ids = ids)

    def get_tags(self):
        all_embeddings = self.content_db.get(include=['metadatas'])
        all_tags = [item.get('tags') for item in all_embeddings['metadatas'] if 'tags' in item]
        return all_embeddings