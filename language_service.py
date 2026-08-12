import os
from dotenv import load_dotenv
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractiveSummaryAction
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()


def get_language_client():
    endpoint = os.getenv("LANGUAGE_ENDPOINT")
    key = os.getenv("LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Azure Language credentials are missing.")

    credential = AzureKeyCredential(key)

    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=credential
    )


def extract_key_phrases(text):
    client = get_language_client()

    documents = [text]

    response = client.extract_key_phrases(documents=documents)

    result = response[0]

    if result.is_error:
        raise Exception(
            f"Language API error: {result.error.code} - {result.error.message}"
        )

    return result.key_phrases

def generate_summary(text):
    client = get_language_client()

    documents = [text]

    poller = client.begin_analyze_actions(
        documents=documents,
        actions=[
            ExtractiveSummaryAction(sentence_count=3)
        ]
    )

    results = poller.result()

    summary = []

    for document_result in results:
        for result in document_result:

            if result.is_error:
                raise Exception(
                    f"Language API error: "
                    f"{result.error.code} - "
                    f"{result.error.message}"
                )

            for sentence in result.sentences:
                summary.append(sentence.text)

    return summary