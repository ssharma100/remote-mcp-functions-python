from datetime import datetime
from zoneinfo import ZoneInfo
import json

class WorkDetailSnippet:
    """
    Represent a snippet record with a format structure for uniform storage in the backing store.
      Will generate a Json file for reability.
    """
    tz_pst = ZoneInfo("America/Los_Angeles")  # Pacific Time Zone
    week = ""
    storedName = ""
    content = ""
    topic = ""
    classification = ""
    date = ""
    user = ""

    def __init__(self, name: str, content: str, user: str = "Unknown", topic: str = "General", classification: str = "WorkDetail"):
        
        today = datetime.now(tz=self.tz_pst)   # All dates and time aligned to Pacific Time Zone
        week_of_year = today.isocalendar()[1]  # Current week number[]
        self.week = (f"Week {week_of_year}")

        self.storedName = name         # unique name of the snippet for storage and management
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
            "backstoreRef": self.storedName,
            "snippetContent": self.content,
            "snippetTopic": self.topic,
            "snippetClassification": self.classification,
            "snippetDate": self.date,
        }

        return json.dumps(work_detail_dict, indent=4)

    @classmethod
    def from_json_string(cls, json_string: str):
        """
        Unmarshal a JSON string to populate the snippet record.
        """
        work_detail_dict = json.loads(json_string)
        # Init Doesn't Work With The Get Fields - so object is empty
        cls("",
                    work_detail_dict.get("snippetContent", ""),
                    work_detail_dict.get("snippetTopic", ""),
                    work_detail_dict.get("snippetClassification", ""))
        
        # Enhancements not populated via constructor
        cls.week = work_detail_dict.get("week", "")
        cls.storedName = work_detail_dict.get("backstoreRef", "")
        cls.content = work_detail_dict.get("snippetContent", "")
        cls.topic = work_detail_dict.get("snippetTopic", "")
        cls.classification = work_detail_dict.get("snippetClassification", "")
        cls.date = work_detail_dict.get("snippetDate", "")
        cls.user = work_detail_dict.get("user", "Unknown")
        return cls

    def summary(self):
        """
        Generate a summary string for logging or display.
        """
        return (f"WorkDetailSnippet(Name: {self.storedName}, "
                f"Week: {self.week}, " 
                f"Topic: {self.topic}, "
                f"Classification: {self.classification}, "
                f"Date: {self.date}, "
                f"User: {self.user})")