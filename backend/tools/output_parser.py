def concise_output(text: str, max_lines: int = 12) -> str:
    """Return a natural, human-like response without cutting important content."""
    if not text:
        return ""

    # Remove markdown formatting but keep content
    import re
    
    cleaned_text = text
    # Remove markdown headers but keep the text
    cleaned_text = re.sub(r'^#+\s*', '', cleaned_text, flags=re.MULTILINE)
    # Remove asterisks and markdown bold/italic but keep text
    cleaned_text = re.sub(r'\*+([^*]+)\*+', r'\1', cleaned_text)
    # Remove bullet points at start of lines but keep content
    cleaned_text = re.sub(r'^[-•*]\s*', '', cleaned_text, flags=re.MULTILINE)
    
    lines = [l.strip() for l in cleaned_text.splitlines() if l.strip()]
    
    if not lines:
        return ""

    # Remove only generic starting phrases
    skip_start_phrases = [
        "based on the analysis,", "here's what i found:", "according to the information,",
        "as per the analysis,", "here are the details:"
    ]
    
    result_lines = []
    for line in lines[:max_lines]:
        line_lower = line.lower()
        
        # Remove generic starting phrases
        for phrase in skip_start_phrases:
            if line_lower.startswith(phrase):
                line = line[len(phrase):].strip()
                break
        
        # Don't cut content - keep full lines
        if line:
            result_lines.append(line)

    return "\n".join(result_lines)