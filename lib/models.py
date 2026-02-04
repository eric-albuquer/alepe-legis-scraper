# models.py

class Decree:
    """Model representing a decree extracted from ALEPE."""

    def __init__(self, number = None, publish_date = None, link = None, summary = None, id = None):
        self.number = number
        self.publish_date = publish_date
        self.cnpj = None
        self.company = None
        self.link = link
        self.summary = summary
        self.program = None
        self.type = None
        self.origin_decree = None
        self.id = id
        self.framing = None

    def to_row(self):
        origin_decree_text = ";".join(map(str, self.origin_decree)) if isinstance(self.origin_decree, list) else None
        return [self.number, self.publish_date, self.program, self.type, self.framing, origin_decree_text, self.cnpj, self.company, self.link, self.id, self.summary]

    def to_dict(self):
        """Return a dict representation for JSON."""
        return {
            "number": self.number,
            "publish_date": self.publish_date,
            "program": self.program,
            "type": self.type,
            "framing": self.framing,
            "origin_decree": self.origin_decree,
            "cnpj": self.cnpj,
            "company": self.company,
            "link": self.link,
            "id": self.id,
            "summary": self.summary,
        }