from datetime import datetime
from zoneinfo import ZoneInfo
import json

class WorkDetailSnippet:
    """
    Represent a snippet record with a format structure for uniform storage in the backing store.
      Will generate a Json file for reability.
    """
    tz_pst = ZoneInfo("America/Los_Angeles")

    def __init__(self, name: str, content: str, topic: str = "General", classification: str = "WorkDetail"):
        
        today = datetime.now(tz=self.tz_pst)   # All dates and time aligned to Pacific Time Zone
        week_of_year = today.isocalendar()[1]  # Current week number[]
        self.week = (f"Week {week_of_year}")
        self.name = name         # unique name of the snippet
        self.content = content   # Text component of the work detail
        self.topic = topic       # Specific category or topic 
        self.classification = classification    # Indicates the type 
        self.date = today.isoformat()  # Date when the snippet was created

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
       
