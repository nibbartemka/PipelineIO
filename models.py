from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PostData:
    user_id: int
    id: int
    title: str
    body: str


@dataclass(slots=True, frozen=True)
class ProcessedPost(PostData):
    complexity_score: float
    text_hash: str
