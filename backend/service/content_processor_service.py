
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import GPT2TokenizerFast
from uuid import uuid4
from groq import Groq
from dotenv import load_dotenv
import os

from models.document import Document
from models.metadata import Metadata
from models.request import QnABySearchQuery
from models.search_response import SearchResponse
from dao.document_dao import DocumentDao 
from utils.llm_utils import LLMUtils 

class ContentProcessorService:

    def __init__(self) -> None:
        load_dotenv()
        self.__dao = DocumentDao("./test.db")
        client = Groq(api_key=os.getenv('GROQ_KEY'))
        self.__llm = LLMUtils(client = client)

    def __create_uuids(self, chunks):
        uuid_list = [str(uuid4()) for _ in range(len(chunks))]
        return uuid_list

    ## Function that gets content, chunk size and returns a list of chunks
    def __chunk_data(self, content, meta_data={"source":"copy_paste"}):
        """Takes content(str) and optional meta_data(dict) and 
        Returns a list of chunks"""
        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function = lambda text: len(tokenizer.encode(text)),
            # separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            is_separator_regex=False,
        )
        return text_splitter.create_documents([content],metadatas=[{k:v} for k,v in meta_data.items()])
    

    def __create_tags(self, chunk):
        prompt = f"""Based on the given content generate 10 or less tags in the form of list seperated by comma.
                        you should return the TAGS ONLY and nothing else,
                        Your output should be SORTED LEXICOGRAPHICALLY, IN LOWERCASE. 
                        It MUST look like - <tag1>, <tag2>, <tag3>
                        
                        {chunk.page_content}
                """
        return self.__llm.query(prompt)
    

    def __clean_tags(self, tags, count):
       prompt = f"""Based on the given tags below, remove all tags that are redundant, not useful, or irrelevant. Return only the {count} most relevant tags.
        
        The purpose of these tags is for a user to select them when revisiting the content they read. 
        
        IMPORTANT:
        - The output MUST be a valid JSON object.
        - Return the output as a JSON object in this format: {{"tags": ["tag1", "tag2", "tag3"]}}.
        - Sort the tags lexicographically in lowercase.

        Here are the tags: {tags}
        """
       return self.__llm.structured_query(Metadata, prompt)
    
    def __questions_by_search_query(self, chunk, query, questions):
        prompt = f"""
            **IMPORTANT RULES:**
                - **DO NOT** ask questions that are similar to these previously asked questions:
                    {questions}
                - Questions must be **completely different** from the previously asked questions. Do not ask rephrased, slightly altered, or redundant questions.
                - **DO NOT** ask questions that focus on the same concept or idea as previously asked questions. Instead, generate questions that explore **new concepts** or details not covered by the prior questions.
                - Ensure each question brings new information or insights from the content.


            Based on the content provided below, generate relevant questions that helps users understand the key concepts or information. For each question, include multiple answer choices and identify the correct option with an explanation.


            IMPORTANT:
            - **DO NOT** return any questions if the given content doesn't match the query: {query}
            - The output MUST be a valid JSON object with **NO additional explanation or commentary outside of the JSON**.
            - Return the output **ONLY** as a JSON object in this format:
                {{"questions": [{{
                    "question": "your question here",
                    "options": ["option1", "option2", "option3"],
                    "correct_option": "the correct option",
                    "explanation": "why the correct option is correct"
                }}]}}
            - Ensure the explanation clearly justifies why the selected answer is correct.
            - **DO NOT** return any questions if the given content doesn't match the query: {query}
            - Do not include any introductory text like "Here is the generated question" before the JSON.

            Here is the content to base the questions on:
            {chunk}
            """
        return self.__llm.structured_query(SearchResponse, prompt)
    
    def __insert(self, text, meta_data):
            chunks = self.__chunk_data(text, meta_data)
            doc_list = []
            uuid_list = self.__create_uuids(chunks)
            content_metadata_list = []
            tag_metadata_list = []
            tag_list = []
            for chunk in chunks:
                doc_list.append(chunk.page_content)
                tags = self.__create_tags(chunk)
                tag_list.append(tags)
                tag_metadata_list.append({k:v for k,v in chunk.metadata.items()})
                temp_meta = {k:v for k,v in chunk.metadata.items()}
                temp_meta["tags"] = tags
                content_metadata_list.append(temp_meta)
 
            self.__dao.store_document(Document(ids = uuid_list,
                                             tags = tag_list, 
                                             tags_metadata = tag_metadata_list, 
                                             content = doc_list,
                                             content_metadata = content_metadata_list))

    def __combine_content(self, old_content, new_content):
        """Takes content(str) and returns rewritten content(str)"""

        prompt = f"""Change the contents of the old content:{old_content} based on the new content:{new_content} and rewrite the everything by  not losing any information.If there is a contradiction, over-write the old content with the new content.  Don't loose any information from the old content.The remaining relavant information from the new content should be kept.Structure the result in a manner that makes the most sense. JUST GIVE ME THE REWRITTEN CONTENT, without any other text."""

        return self.__llm.query(prompt)


    '''
    Public Methods
    '''
    def upsert(self, request):
        chunks = self.__chunk_data(request.content, meta_data = {"source" : request.source})
        queries = [chunk.page_content for chunk in chunks]
        for query in queries:
            similar_info = self.__dao.retrieve_by_content(query)
            if similar_info is not None:
                similar_info_ids = similar_info['ids'][0]
                similar_info_content = "\n".join(similar_info['documents'][0])
                self.remove(similar_info_ids)
                new_information = self.__combine_content(similar_info_content, query)
                self.__insert(new_information, meta_data = {"source" : request.source})
            else:
                self.__insert(request.content, meta_data = {"source" : request.source})
    
    def remove(self, ids):
        self.__dao.remove_document(ids)

    def get_tags(self, count):
        all_tags = self.__dao.get_tags()
        cleaned_tags = self.__clean_tags(all_tags, count)
        return cleaned_tags
    
    def questions_by_search_query(self, request: QnABySearchQuery):
        documents = self.__dao.retrieve_by_content(request.query, n_results = 100, threshold=0.7)
        print(documents)
        questions = []
        if documents:
            chunks = [item for item in documents['documents']]
            covered_questions = []
            for chunk in chunks:
                response: SearchResponse = self.__questions_by_search_query(chunk, request.query, covered_questions)
                questions.extend(response.questions)
                covered_questions.extend(response.questions)
                if(len(questions) > request.questions):
                    return questions
        return questions
