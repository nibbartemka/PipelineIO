import hashlib
import logging
import math

from models import PostData, ProcessedPost

logger: logging.Logger = logging.getLogger(__name__)


def process_post(
    post: PostData,
) -> ProcessedPost | None:
    score: float = (sum(math.sin(i) for i in range(1_000_000))
                    * len(post.body))
    text_hash = hashlib.sha256(
        f"{post.title}{post.body}".encode()
    ).hexdigest()

    return ProcessedPost(
        user_id=post.user_id,
        id=post.id,
        title=post.title,
        body=post.body,
        complexity_score=score,
        text_hash=text_hash,
    )
