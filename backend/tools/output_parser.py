def concise_output(text: str, max_lines: int = 8) -> str:
    """
    Parse and condense a long text response to a maximum of `max_lines` lines.
    Keeps the title/first line and the next most informative lines (bullets, tips, etc).
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return ""
    # Always keep the first line (title or summary)
    output = [lines[0]]
    # Collect the next most informative lines (bullets, tips, et
    bullets = [l for l in lines[1:] if l.startswith("*") or l.startswith("-")]
    # If not enough bullets, add other lines
    rest = [l for l in lines[1:] if l not in bullets]
    for l in bullets:
        if len(output) < max_lines:
            output.append(l)
    for l in rest:
        if len(output) < max_lines:
            output.append(l)
    return "\n".join(output[:max_lines]) 