from typing import Literal, TypedDict


class AftAccountInfo(TypedDict):
    id: str
    email: str
    name: str
    joined_method: str
    joined_date: str
    status: str
    parent_id: str
    parent_type: str
    org_name: str
    type: Literal["account"]
    vendor: Literal["aws"]
