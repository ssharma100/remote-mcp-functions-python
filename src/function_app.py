import json
import logging
import datetime

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Constants for the Azure Blob Storage container, file, and blob path
_PROPERTY_SNIPPET_NAME = "snippetName"
_PROPERTY_SNIPPET_CONTENT = "snippetContent"
_PROPERTY_SNIPPET_TOPIC = "snippetTopic"
_PROPERTY_SNIPPET_CLASSIFICATION = "snippetClassification"
_PROPERTY_SNIPPET_DATE = "snippetDate"
_BLOB_PATH = "snippets/{mcptoolargs." + _PROPERTY_SNIPPET_NAME + "}.json"


# Defint the property structure to hold name, type, and description
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
    PropertyTuple(_PROPERTY_SNIPPET_NAME, "string", "The name of the snippet."),
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

    heartbeatMsg = 'At {0}: Heartbeat MCP Service Is Up And Running I am MCPTool!'.format(datetime.datetime.today())
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
    description="Save a snippet of information for a give date, with a topic and with some string context. The use can optionally provide the classification of the snippet.",
    toolProperties=tool_properties_save_snippets_json,
)
@app.generic_output_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def save_snippet(file: func.Out[str], context) -> str:
    content = json.loads(context)
    snippet_name_from_args = content["arguments"][_PROPERTY_SNIPPET_NAME]
    snippet_content_from_args = content["arguments"][_PROPERTY_SNIPPET_CONTENT]
    # Unused At This Point - Future Enhancements For Re-Organziation Of The Snippets
    snippet_topic_from_args = content["arguments"][_PROPERTY_SNIPPET_TOPIC]
    snippet_classification_from_args = content["arguments"][_PROPERTY_SNIPPET_CLASSIFICATION]
    snippet_date_from_args = content["arguments"][_PROPERTY_SNIPPET_DATE]

    if not snippet_name_from_args:
        return "No snippet name provided"

    if not snippet_content_from_args:
        return "No snippet content provided"

    file.set(snippet_content_from_args)
    logging.info(f"Saved snippet: {snippet_content_from_args}")
    return f"Snippet '{snippet_content_from_args}' saved successfully"
