import pytest
import secrets
from datetime import datetime
from models.WorkSnippets import WorkDetailSnippet

def test_work_detail_snippet_initialization(capsys):
    current_time = datetime.now()
    random_snippet_id = secrets.randbelow(10000)
    storage_name = f"snippet-{current_time:%Y%m%d%H%M%S}-{random_snippet_id}"
    work_detail = WorkDetailSnippet(storage_name, "Worked on code to create a MCP server from scratch")
    serialized_work_detail = work_detail.marshal()
    print(f"Json Output Sample:\n {serialized_work_detail}")

def test_work_detail_snippet_unmarshal(capsys):
    current_time = datetime.now()
    random_snippet_id = secrets.randbelow(10000)
    storage_name = f"snippet-{current_time:%Y%m%d%H%M%S}-{random_snippet_id}"
    work_detail = WorkDetailSnippet(storage_name, "Worked on code to create a MCP server from scratch")
    serialized_work_detail = work_detail.marshal()
    print(f"\nJson Output Sample To Unmarshal Later:\n {serialized_work_detail}")
    # Process Unmarshal - Create A new Object from the JSON String
    object = WorkDetailSnippet.from_json_string(serialized_work_detail)
    assert object.week == work_detail.week, "Week should be deserialized correctly and match original object value"
    assert object.storedName == work_detail.storedName, "StoredName should be deserialized correctly and match original object value"
    assert object.content == work_detail.content, "Content should be deserialized correctly and match original object value"
    assert object.topic == work_detail.topic, "Topic should be deserialized correctly and match original object value"
    assert object.classification == work_detail.classification, "Classification should be deserialized correctly and match original object value"
    assert object.date == work_detail.date, "Date should be deserialized correctly and match original object value"
    assert object.user == work_detail.user, "User should be deserialized correctly and match original object value"


