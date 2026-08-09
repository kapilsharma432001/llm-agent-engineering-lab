"""Tools available to the Phase 1 study-planning agent."""

from langchain.tools import tool


@tool
def create_study_plan(
    total_topics: int,
    available_days: int,
) -> list[int]:
    """Distribute a non-negative number of topics across available study days.

    Each list item is the topic count for that day, starting with day one.
    """

    if total_topics < 0:
        raise ValueError("total_topics must be zero or greater.")
    if available_days <= 0:
        raise ValueError("available_days must be greater than zero.")

    topics_per_day, remaining_topics = divmod(total_topics, available_days)

    # Put one remainder topic on each earliest day.
    return [
        topics_per_day + (1 if day < remaining_topics else 0)
        for day in range(available_days)
    ]
