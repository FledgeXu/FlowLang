from pydantic import BaseModel, Field


class MindNode(BaseModel):
    text: str = Field(..., description="Text content of this node")
    children: list["MindNode"] = Field(default_factory=list, description="Child nodes")