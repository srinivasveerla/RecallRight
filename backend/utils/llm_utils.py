from langchain.output_parsers import PydanticOutputParser

class LLMUtils:

    def __init__(self, client) -> None:
        self.client = client

    def query(self, prompt, model = "llama3-8b-8192", temperature = 0):
        """Queries the LLM with the given model, temperature and prompt. Returns the reponse from the model"""
      
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model = model,
            temperature = temperature
        )
        return chat_completion.choices[0].message.content
    
    def structured_query(self, pydantic_class, prompt):
        output_parser = PydanticOutputParser(pydantic_object=pydantic_class)
        response = self.query(prompt)
        return output_parser.parse(response)