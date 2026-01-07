import os
import json
import logging
import secrets

import azure.functions as func
from models.WorkSnippets import WorkDetailSnippet
from datetime import datetime
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Constants for the Azure Blob Storage container, file, and blob path
_PROPERTY_SNIPPET_WEEK = "snippetWeek"
_PROPERTY_SNIPPET_NAME = "snippet_content"
_PROPERTY_SNIPPET_CONTENT = "snippetContent"
_PROPERTY_SNIPPET_TOPIC = "snippetTopic"
_PROPERTY_SNIPPET_CLASSIFICATION = "snippetClassification"
_PROPERTY_SNIPPET_DATE = "snippetDate"
_PROPERTY_SNIPPET_USER = "snippetUser"
_BLOB_PATH = "snippets/{storedObject." + _PROPERTY_SNIPPET_NAME + "}.json"


# Defines the property structure to hold name, type, and description
# Used for MCP protocol required structure of properties communicated to host using the agent.
class PropertyTuple:
    def __init__(self, name: str, type: str, description: str):
        self.name = name
        self.type = type
        self.description = description
        
    def to_dict(self):
        return {
            "propertyName": self.name,
            "propertyType": self.type,
            "description": self.description,
        }


# Instantiate the tool properties using the ToolProperty object definition
tool_save_snippets_property_list = [
    PropertyTuple(_PROPERTY_SNIPPET_USER, "string", "UserID or Owner associated with this snippet."),
    PropertyTuple(_PROPERTY_SNIPPET_CONTENT, "string", "The content of the snippet."),
    PropertyTuple(_PROPERTY_SNIPPET_TOPIC, "string", "The topic of the snippet."),
    PropertyTuple(_PROPERTY_SNIPPET_CLASSIFICATION, "string", "The classification of the snippet."),
    PropertyTuple(_PROPERTY_SNIPPET_DATE, "date", "The date of the snippet"),
]

tool_get_snippets_property_list = [PropertyTuple(_PROPERTY_SNIPPET_NAME, "string", "The name of the snippet.")]

# Convert the tool properties to JSON
tool_properties_save_snippets_json = json.dumps([prop.to_dict() for prop in tool_save_snippets_property_list])
tool_properties_get_snippets_json = json.dumps([prop.to_dict() for prop in tool_get_snippets_property_list])

# See Azure Function Annotation Documentation For Parameter/Decorator Specification:
# For @mcp_tool_trigger:
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp-trigger?tabs=attribute&pivots=programming-language-python

def snippet_stored_name() -> str:
    """
    Generate a standardized stored name for the snippet.
    """

    current_time = datetime.now()
    random_snippet_id = secrets.randbelow(10000)
    storage_name = f"snippet-{current_time:%Y%m%d%H%M%S}-{random_snippet_id}"
    return storage_name

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="heartbeat_mcp",
    description="Provides a Heartbeat message/ping verification that the MCP Service supporting User Snippet and work effort tracking is up and running.",
    toolProperties="[]",
)
def heartbeat_mcp(context) -> str:
    """
    A simple function that returns a heartbeat message.

    Args:
        context: The trigger context (not used in this function).

    Returns:
        str: A greeting message.
    """

    heartbeatMsg = 'At {0}: Heartbeat MCP Service Is Up And Running I am MCPTool!'.format(datetime.today())
    logging.info(heartbeatMsg)
    return heartbeatMsg


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_snippet",
    description="Retrieve a snippet by name.",
    toolProperties=tool_properties_get_snippets_json,
)
@app.generic_input_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def get_snippet(file: func.InputStream, context) -> str:
    """
    Retrieves a snippet by name from Azure Blob Storage.

    Args:
        file (func.InputStream): The input binding to read the snippet from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The content of the snippet or an error message.
    """
    snippet_content = file.read().decode("utf-8")
    logging.info(f"Retrieved snippet: {snippet_content}")
    return snippet_content


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="save_snippet",
    description="Save a snippet to store the users provided content (usually descriptions of actions and or activities) to be" +
      " recorded for a give snippet name and with a topic. The use can optionally provide the classification for the snippet to" + 
      " relay the snippet's importances or type.",
    toolProperties=tool_properties_save_snippets_json,
)
@app.generic_output_binding(arg_name="outputBlob", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def save_snippet(outputBlob: func.Out[str], context) -> str:
    mcp_message = json.loads(context)
    snippet_name = snippet_stored_name()
    snippet_content = mcp_message["arguments"][_PROPERTY_SNIPPET_CONTENT]
    # Unused At This Point - Future Enhancements For Re-Organziation Of The Snippets
    snippet_topic_from_args = mcp_message["arguments"][_PROPERTY_SNIPPET_TOPIC]
    snippet_classification_from_args = mcp_message["arguments"][_PROPERTY_SNIPPET_CLASSIFICATION]
    snippet_user = mcp_message["arguments"][_PROPERTY_SNIPPET_USER] 

    # Validate Required Fields

    if not snippet_content:
        return "No snippet content provided"

    # Create Formatted Json For Storage Document Structure
    storedObject = WorkDetailSnippet(name=snippet_name, 
                                     content=snippet_content,
                                     user=snippet_user,
                                     topic=snippet_topic_from_args,
                                     classification=snippet_classification_from_args)
    
    snippet_content = storedObject.marshal()
    # 1. Calculate your dynamic path
    dynamic_path = f"demo/{snippet_name}.json"
    
    # 2. Use the SDK to upload
    connection_string = os.getenv("AzureWebJobsStorage")
    service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = service_client.get_blob_client(container="snippets", blob=dynamic_path)

    blob_client.upload_blob(snippet_content, overwrite=True)
    logging.info(f"Saved snippet: {storedObject.summary()}")
    return f"Snippet '{storedObject.summary()}' saved successfully"

