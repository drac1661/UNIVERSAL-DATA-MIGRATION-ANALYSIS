from typing import List, Optional
from pydantic import BaseModel


class Permission(BaseModel):
    grantee: str
    privileges: List[str] = []
    object_type: Optional[str] = None
    object_name: Optional[str] = None
    grantable: Optional[bool] = False
