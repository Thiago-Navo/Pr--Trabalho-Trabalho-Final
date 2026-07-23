from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BaseModel:
    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
