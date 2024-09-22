import logging
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
from service.text_processor_service import TextProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ContentProcessorService:

    def __init__(self) -> None:
        logging.debug("Initializing ContentProcessorService")
        load_dotenv()
        self.__dao = DocumentDao("./test1.db")
        client = Groq(api_key=os.getenv('GROQ_KEY'))
        self.__llm = LLMUtils(client=client)
        self.__text_util = TextProcessor()
        logging.debug("ContentProcessorService initialized successfully")

    def __create_uuids(self, chunks):
        logging.debug("Creating UUIDs for chunks")
        uuid_list = [str(uuid4()) for _ in range(len(chunks))]
        logging.debug(f"UUIDs created: {uuid_list}")
        return uuid_list

    def __chunk_data(self, content, meta_data={"source": "copy_paste"}):
        logging.debug(f"Chunking data with content: {content[:50]}... and meta_data: {meta_data}")
        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=lambda text: len(tokenizer.encode(text)),
            is_separator_regex=False,
        )
        chunks = text_splitter.create_documents([content], metadatas=[{k: v} for k, v in meta_data.items()])
        logging.debug(f"Data chunked into {len(chunks)} chunks")
        return chunks

    def __create_tags(self, chunk):
        logging.debug(f"Creating tags for chunk: {chunk.page_content}...")
        prompt = f"""Based on the given content, generate 10 or fewer CATEGORIES that accurately and specifically represent the main subjects and themes covered.
        Ensure the CATEGORIES are more specific and exclude any overly broad or vague terms. 
        The 10 CATEGORIES should be able to describe the things talked about in the given content.
        Return the output as a valid JSON object with the CATEGORIES listed as strings.
        
        IMPORTANT:
        - The 10 CATEGORIES should be able to describe the things talked about in the given content.
        - The output MUST be a valid JSON object.
        - Return the output in this format: {{"tags": ["category1", "category2", "category3"]}}.
        - CATEGORIES should be specific and exclude any overly broad or vague terms.
        - Do not include any introductory text like "Here is the generated question" before the JSON.

        Content: {chunk.page_content}
        """
        tags = self.__llm.structured_query(Metadata, prompt)
        logging.debug(f"Tags created: {tags}")
        return tags

    def __clean_tags(self, tags, count):
        logging.debug(f"Cleaning tags: {tags} to retain top {count}")
        prompt = f"""
            You are required to return only the {count} most relevant tags, strictly in JSON format. 

            RULES:
            1. The output **MUST** be a valid JSON object in the format: {{"tags": ["tag1", "tag2", "tag3"]}}.
            2. All tags must be lexicographically sorted and in lowercase.
            3. **DO NOT** include any introductory, explanatory, or precursor text like "Here is the output in the required JSON format". 
            4. Any deviation from this format will be considered incorrect.

            Tags: {tags}
        """
        cleaned_tags = self.__llm.structured_query(Metadata, prompt)
        logging.debug(f"Cleaned tags: {cleaned_tags}")
        return cleaned_tags

    def __questions_by_search_query(self, chunk, query, questions):
        logging.debug(f"Generating questions for chunk: {chunk[:50]}... with query: {query}")
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
                    "correct_option": "the correct option in the format of (A / B / C / D) - the option number. Just the alphabet - nothing else",
                    "explanation": "why the correct option is correct"
                }}]}}
            - Ensure the explanation clearly justifies why the selected answer is correct.
            - **DO NOT** return any questions if the given content doesn't match the query: {query}
            - Do not include any introductory text like "Here is the generated question" before the JSON.

            Here is the content to base the questions on:
            {chunk}
            """
        questions = self.__llm.structured_query(SearchResponse, prompt)
        logging.debug(f"Questions generated: {questions}")
        return questions

    def __insert(self, text, meta_data):
        logging.debug(f"Inserting document with text: {text[:50]}... and meta_data: {meta_data}")
        chunks = self.__chunk_data(text, meta_data)
        doc_list = []
        uuid_list = self.__create_uuids(chunks)
        content_metadata_list = []
        tag_metadata_list = []
        tag_list = []
        for chunk in chunks:
            doc_list.append(chunk.page_content)
            metadata: Metadata = self.__create_tags(chunk)
            enriched_tags = self.__text_util.generate_tag_metadata(', '.join(metadata.tags))
            tag_list.append(enriched_tags)
            tag_metadata_list.append({k: v for k, v in chunk.metadata.items()})
            temp_meta = {k: v for k, v in chunk.metadata.items()}
            temp_meta["tags"] = enriched_tags
            content_metadata_list.append(temp_meta)

        self.__dao.store_document(Document(ids=uuid_list,
                                           tags=tag_list,
                                           tags_metadata=tag_metadata_list,
                                           content=doc_list,
                                           content_metadata=content_metadata_list))
        logging.debug("Document inserted successfully")

    def __combine_content(self, old_content, new_content):
        logging.debug(f"Combining old content: {old_content}... with new content: {new_content[:50]}...")
        prompt = f"""Change the contents of the old content:{old_content} based on the new content:{new_content} and rewrite the everything by  not losing any information.
        
        If there is a contradiction, over-write the old content with the new content.  
        Don't loose any information from the old content.
        The remaining relavant information from the new content should be kept.
        Structure the result in a manner that makes the most sense. 
        
        JUST GIVE ME THE REWRITTEN CONTENT, without any other text."""
        combined_content = self.__llm.query(prompt)
        logging.debug(f"Combined content: {combined_content}...")
        return combined_content

    '''
    Public Methods
    '''
    def upsert(self, request):
        logging.debug(f"Upserting content with request: {request}")
        cleaned_text = self.__text_util.preprocess_content(request.content)
        logging.debug("Cleaned Content: " + cleaned_text)
        chunks = self.__chunk_data(cleaned_text, meta_data={"source": request.source})
        queries = [chunk.page_content for chunk in chunks]
        for query in queries:
            similar_info = self.__dao.retrieve_by_content(query)
            if similar_info is not None:
                similar_info_ids = similar_info['ids'][0]
                similar_info_content = "\n".join(similar_info['documents'][0])
                self.remove(similar_info_ids)
                new_information = self.__combine_content(similar_info_content, query)
                self.__insert(new_information, meta_data={"source": request.source})
            else:
                self.__insert(cleaned_text, meta_data={"source": request.source})
        logging.debug("Upsert operation completed")

    def remove(self, ids):
        logging.debug(f"Removing document with ids: {ids}")
        self.__dao.remove_document(ids)
        logging.debug("Document removed successfully")

    def get_tags(self, count):
        logging.debug(f"Getting top {count} tags")
        all_tags = self.__dao.get_tags()
        cleaned_tags = self.__clean_tags(all_tags, count)
        logging.debug(f"Retrieved tags: {cleaned_tags}")
        return cleaned_tags

    def questions_by_search_query(self, request: QnABySearchQuery):
        logging.debug(f"Generating questions by search query with request: {request}")
        documents = self.__dao.retrieve_by_content(request.query, n_results=100, threshold=0.7)
        logging.debug(f"Documents retrieved: {documents}")
        questions = []
        if documents:
            chunks = [item for item in documents['documents']]
            covered_questions = []
            for chunk in chunks:
                response: SearchResponse = self.__questions_by_search_query(chunk, request.query, covered_questions)
                questions.extend(response.questions)
                covered_questions.extend(response.questions)
                if len(questions) > request.questions:
                    logging.debug(f"Generated questions: {questions[:request.questions]}")
                    return questions[:request.questions]
        logging.debug(f"Generated questions: {questions}")
        return questions