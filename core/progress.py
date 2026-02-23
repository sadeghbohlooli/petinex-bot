"""نمایش پیشرفت ارزیابی."""

from questions import (
    QUESTION_FLOW,
    get_question_by_id,
    should_show_question,
    calculate_progress,
    get_section_for_question,
)


def get_progress_text(current_id, user_answers: dict) -> str:
    """Generate a progress indicator string."""
    progress = calculate_progress(current_id, user_answers)
    section = get_section_for_question(current_id)

    active_count = 0
    current_pos = 0
    for qid in QUESTION_FLOW:
        q = get_question_by_id(qid)
        if q and should_show_question(q, user_answers):
            active_count += 1
            if qid == current_id:
                current_pos = active_count

    return f"📊 سؤال {current_pos} از ~{active_count} ({progress}%)"
