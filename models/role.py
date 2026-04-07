from typing import List, Optional
from pydantic import BaseModel


class Role(BaseModel):
    name: str
    superuser: bool = False
    createdb: bool = False
    createrole: bool = False
    login: bool = False
    replication: bool = False
    inherit: bool = True
    member_of: List[str] = []
    password: Optional[str] = None
    valid_until: Optional[str] = None
