from __future__ import annotations

import json
from typing import Any

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.utils import camel_to_snake


class Record(BaseModel):
    collection_id: str
    collection_name: str
    expand: dict[str, Any]

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.expand = {}
        for key, value in data.items():
            key = camel_to_snake(
                key,
                getattr(self, "client", None)
                and getattr(self.client, "auto_snake_case", True),
            ).replace("@", "")
            setattr(self, key, value)
        self.load_expanded()

    @classmethod
    def parse_expanded(cls, data: Any):
        if isinstance(data, list):
            return [cls(a) for a in data]  # type: ignore
        return cls(data)

    def load_expanded(self) -> None:
        for key, value in self.expand.items():
            self.expand[key] = self.parse_expanded(value)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Record to a dictionary representation.
        
        Returns:
            dict: A dictionary containing all the record's data, including
                  base fields (id, created, updated), collection info,
                  dynamic fields, and expanded relations.
        """
        result = {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "collection_id": self.collection_id,
            "collection_name": self.collection_name,
        }
        
        # Add all dynamic fields (excluding the base fields and expand)
        for key, value in self.__dict__.items():
            if key not in ["id", "created", "updated", "collection_id", "collection_name", "expand"]:
                result[key] = self._serialize_value(value)
        
        # Add expanded relations
        if hasattr(self, 'expand') and self.expand:
            result["expand"] = self._serialize_value(self.expand)
        
        return result

    def to_json(self, **kwargs) -> str:
        """
        Convert the Record to a JSON string representation.
        
        Args:
            **kwargs: Additional arguments to pass to json.dumps()
        
        Returns:
            str: JSON string representation of the record
        """
        return json.dumps(self.to_dict(), **kwargs)

    def _serialize_value(self, value: Any) -> Any:
        """
        Recursively serialize a value to be JSON-compatible.
        
        Args:
            value: The value to serialize
            
        Returns:
            The serialized value
        """
        if isinstance(value, Record):
            return value.to_dict()
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {key: self._serialize_value(val) for key, val in value.items()}
        elif hasattr(value, 'isoformat'):  # datetime objects
            return value.isoformat()
        else:
            return value
