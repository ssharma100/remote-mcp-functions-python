class WorkDetailSnippet:
    """Represent a snippet record with a format structure for uniform storage in the backing store.
      Will generate a Json file for reability."""

    def __init__(self, name: str, content: str, topic: str = "", classification: str = "", date: str = ""):
        self.name = name
        self.content = content
        self.topic = topic
        self.classification = classification
        self.date = date

