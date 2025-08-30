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

    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase (reverse of camel_to_snake)."""
        if '_' not in name:
            return name
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def to_dict(self) -> dict[str, Any]:
        """
        Returns a dictionary representation of the Record that can be serialized to JSON.
        
        This method serializes all attributes of the Record, including:
        - Base attributes (id, created, updated).
        - Collection attributes (collectionId, collectionName).
        - Expand data.
        - All dynamic attributes set during the load method.
        
        Returns:
            dict[str, Any]: Dictionary representation of the Record.
        """
        data = {}
        
        # Add base attributes
        data['id'] = self.id
        data['created'] = self.created.isoformat() if hasattr(self.created, 'isoformat') else str(self.created)
        data['updated'] = self.updated.isoformat() if hasattr(self.updated, 'isoformat') else str(self.updated)
        
        # Add expand data
        data['expand'] = self.expand
        
        # Add all other dynamic attributes (excluding special attributes)
        exclude_attrs = {'id', 'created', 'updated', 'expand', 'client'}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name not in exclude_attrs:
                try:
                    attr_value = getattr(self, attr_name)
                    if not callable(attr_value):
                        # Use the same auto_snake_case setting as the client for consistency
                        auto_snake_case = (
                            getattr(self, "client", None) 
                            and getattr(self.client, "auto_snake_case", True)
                        )
                        
                        if auto_snake_case and '_' in attr_name:
                            # Convert snake_case back to camelCase for JSON output
                            json_key = self._snake_to_camel(attr_name)
                        else:
                            # Keep original format
                            json_key = attr_name
                            
                        data[json_key] = attr_value
                except (AttributeError, TypeError):
                    # Skip attributes that can't be accessed or serialized
                    continue
        
        return data
