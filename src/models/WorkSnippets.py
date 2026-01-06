from datetime import datetime
from zoneinfo import ZoneInfo
import json

class WorkDetailSnippet:
    """
    Represent a snippet record with a format structure for uniform storage in the backing store.
      Will generate a Json file for reability.
    """
    tz_pst = ZoneInfo("America/Los_Angeles")

    def __init__(self, name: str, content: str, user: str = "Unknown", topic: str = "General", classification: str = "WorkDetail"):
        
        today = datetime.now(tz=self.tz_pst)   # All dates and time aligned to Pacific Time Zone
        week_of_year = today.isocalendar()[1]  # Current week number[]
        self.week = (f"Week {week_of_year}")
        self.blob_name = name         # unique name of the snippet for storage and management
        self.content = content   # Text component of the work detail
        self.topic = topic       # Specific category or topic 
        self.classification = classification    # Indicates the type 
        self.date = today.isoformat()  # Date when the snippet was created
        self.user = user         # User who created the snippet

    def marshal(self):
        """
        Marshal the snippet record to a JSON string for storage.
        """
        
        work_detail_dict = {
            "week": self.week,
            "snippetName": self.name,
            "snippetContent": self.content,
            "snippetTopic": self.topic,
            "snippetClassification": self.classification,
            "snippetDate": self.date,
        }

        return json.dumps(work_detail_dict, indent=4)

    def unmarshal(self, json_string: str):
        """
        Unmarshal a JSON string to populate the snippet record.
        """
        work_detail_dict = json.loads(json_string)
        self.week = work_detail_dict.get("week", "")
        self.name = work_detail_dict.get("snippetName", "")
        self.content = work_detail_dict.get("snippetContent", "")
        self.topic = work_detail_dict.get("snippetTopic", "")
        self.classification = work_detail_dict.get("snippetClassification", "")
        self.date = work_detail_dict.get("snippetDate", "")
        return self
       
