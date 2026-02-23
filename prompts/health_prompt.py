# prompts/health_prompt.py
def generate_health_prompt(answers: dict) -> str:
    """Generate a simple text report from answers."""
    lines = ["📊 گزارش سلامت پت", "="*30]
    for key, value in answers.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
