import pytest
from models.WorkSnippets import WorkDetailSnippet

def test_work_detail_snippet_initialization(capsys):
    work_detail = WorkDetailSnippet("Customer Meetings", "Worked on code to create a MCP server from scratch")
    serialized_work_detail = work_detail.marshal()
    print(f"Json Output Sample:\n {serialized_work_detail}")
    