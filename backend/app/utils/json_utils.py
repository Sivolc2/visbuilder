from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_to_json(obj):
    """Serialize an object to JSON string with datetime handling"""
    return json.dumps(obj, cls=DateTimeEncoder)

def parse_json(json_str):
    """Parse JSON string with datetime handling"""
    return json.loads(json_str) 