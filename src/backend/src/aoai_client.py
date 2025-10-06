# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# HACKDAY MODIFICATION: Using OpenAI instead of Azure OpenAI
import logging
import json
import os
from typing import Callable
from openai import OpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

def get_prompt(
    prompt: str,
    path: str = "prompts/"
) -> str:
    """
    Load prompt.
    """
    with open(path + prompt, 'r') as fp:
        content = fp.read()
    return content


RAG_GROUNDING_PROMPT = get_prompt("rag_grounding.txt")


class AOAIClient(OpenAI):
    """
    Chat-only AOAI Client.

    HACKDAY: OpenAI wrapper (not Azure) with function-calling and RAG support.
    """

    def __init__(
        self,
        endpoint: str = None,  # Ignored for OpenAI, kept for compatibility
        deployment: str = "gpt-4o-mini",  # Model name for OpenAI
        api_version: str = None,  # Ignored for OpenAI, kept for compatibility
        scope: str = None,  # Ignored for OpenAI, kept for compatibility
        azure_credential = None,  # Ignored for OpenAI, kept for compatibility
        system_message: str = None,
        function_calling: bool = False,
        tools: list = None,
        functions: dict[str, Callable] = None,
        return_functions: bool = False,
        use_rag: bool = False,
        search_client: SearchClient = None
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

        # HACKDAY: Use OpenAI API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        OpenAI.__init__(
            self,
            api_key=api_key
        )

        # Function-calling:
        self.function_calling = function_calling
        self.tools = tools
        self.functions = functions
        self.return_functions = return_functions

        # RAG:
        self.use_rag = use_rag
        self.search_client = search_client

        # General:
        self.deployment = self.model_name = deployment
        self.chat_api = True
        self.messages = []

        if system_message:
            # Prepend system message:
            self.messages = [{"role": "system", "content": system_message}]

    def call_functions(
        self,
        language: str,
        id: str
    ) -> tuple[list, list]:
        """
        AOAI function calling.

        Returns:
            Tuple of (function_responses, tool_calls_info) for logging/display
        """
        # Call chat API with function-calling enabled:
        response = self.chat.completions.create(
            model=self.deployment,
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
        )

        # Process model's response:
        response_message = response.choices[0].message
        self.messages.append(response_message)
        self.logger.info(f"Model response: {response_message}")

        # Handle function calls:
        function_responses = []
        tool_calls_info = []

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                self.logger.info(f"Function call: {function_name}")
                self.logger.info(f"Function arguments: {function_args}")

                # Store tool call info for UI display
                tool_calls_info.append({
                    "id": tool_call.id,
                    "name": function_name,
                    "arguments": function_args
                })

                if function_name in self.functions:
                    # Call the function with its arguments
                    func = self.functions[function_name]
                    func_response = func(**function_args)
                else:
                    func_response = {"error": f"Unknown function: {function_name}"}

                function_responses.append(func_response)
                self.logger.info(f"Function response: {str(func_response)}")
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(func_response) if isinstance(func_response, dict) else str(func_response)
                })
        else:
            self.logger.info("No tool calls made by model.")

        return function_responses, tool_calls_info

    def generate_rag_prompt(
        self,
        query: str
    ) -> str:
        """
        Generates RAG grounding prompt given query and search client.
        """
        self.logger.info("Calling search client")
        vector_query = VectorizableTextQuery(
            text=query,
            k_nearest_neighbors=50,
            fields="text_vector"
        )
        search_results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["title", "chunk"],
            top=5
        )

        sources_formatted = "=================\n".join(
            [f'TITLE: {doc["title"]}, CONTENT: {doc["chunk"]}' for doc in search_results]
        )

        prompt = RAG_GROUNDING_PROMPT.format(
            query=query,
            sources=sources_formatted
        )

        return prompt

    def chat_completion(
        self,
        message: str,
        language: str = None,
        id: str = None,
        return_tool_calls: bool = False
    ) -> str | dict:
        """
        AOAI chat completion with optional tool calling.

        Args:
            message: User message
            language: Language code (optional)
            id: Request ID (optional)
            return_tool_calls: If True, returns dict with content and tool_calls info

        Returns:
            Response content string, or dict with content and tool_calls if return_tool_calls=True
        """
        # Add user message:
        prompt = self.generate_rag_prompt(message) if self.use_rag else message
        self.messages.append({"role": "user", "content": prompt})

        tool_calls_made = []

        if self.function_calling:
            function_results, tool_calls_info = self.call_functions(language=language, id=id)
            tool_calls_made = tool_calls_info

            if self.return_functions:
                # Return function-call results directly:
                return function_results

        # Call chat API:
        print(f"   📤 Sending {len(self.messages)} messages to OpenAI...")
        response = self.chat.completions.create(
            model=self.deployment,
            messages=self.messages
        )
        response_message = response.choices[0].message
        print(f"   📥 OpenAI response: {response_message.content}")
        self.logger.info(f"Model response: {response_message}")
        self.messages.append(response_message)

        if return_tool_calls and tool_calls_made:
            return {
                "content": response_message.content,
                "tool_calls": tool_calls_made
            }

        return response_message.content
