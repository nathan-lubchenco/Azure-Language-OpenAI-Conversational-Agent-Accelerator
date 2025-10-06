# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# HACKDAY: Using mocks for Azure services
import os
import uuid
from typing import Callable
from router.router_type import RouterType
from router.router_utils import create_router
from hackday_mocks import MockTextAnalyticsClient


class UnifiedConversationOrchestrator():
    """
    Unified-Conversation-Orchestrator.

    Orchestration support for CLU/CQA/fallback.
    """

    def __init__(
        self,
        router_type: RouterType,
        fallback_function: Callable[[str, str, str], dict]
    ):
        """
        Initialize orchestrator: create internal TA client and router.
        """
        # HACKDAY: Use mock TextAnalyticsClient
        self.ta_client = MockTextAnalyticsClient(
            endpoint=os.environ.get("LANGUAGE_ENDPOINT", "dummy"),
            credential=None
        )

        # Router is Callable[[str, str, str], dict]:
        self.router_type = router_type
        self.router = create_router(
            router_type=self.router_type
        )

        self.fallback_function = fallback_function

    def detect_language(
        self,
        text: str
    ) -> str:
        """
        Detect language of input text using Azure AI Lanuage.
        """
        result = self.ta_client.detect_language(documents=[text])
        language = result[0].primary_language.iso6391_name
        return language

    def orchestrate(
        self,
        message: str,
        id: str = None
    ) -> dict:
        """
        Orchestrate message with registered router/fallback-function.
        """
        if id is None:
            id = str(uuid.uuid4())

        language = self.detect_language(text=message)

        # Router expects a message, language, and id:
        routing_result = self.router(message, language, id)

        orchestration_response = {
            "id": id,
            "query": message,
            "router_type": self.router_type.name
        }

        if routing_result is None or routing_result["error"] is not None:
            # Fallback-function expects a message, language, and message id:
            fallback_result = self.fallback_function(
                message,
                language,
                id)

            orchestration_response["route"] = "fallback"
            orchestration_response["result"] = fallback_result

            if routing_result is not None:
                orchestration_response["attempted_route"] = routing_result

        else:
            routing_result.pop("error")
            route = "clu" if routing_result["kind"] == "clu_result" else "cqa"
            orchestration_response["route"] = route
            orchestration_response["result"] = routing_result

        return orchestration_response
