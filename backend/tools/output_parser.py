def concise_output(text: str, max_lines: int = 6) -> str:
    """Return a natural, colorful, human-like response without asterisks or markdown."""
    if not text:
        return ""

    # Remove all markdown formatting and asterisks
    import re
    
    # Clean the text
    cleaned_text = text
    # Remove markdown headers
    cleaned_text = re.sub(r'^#+\s*', '', cleaned_text, flags=re.MULTILINE)
    # Remove asterisks and markdown bold/italic
    cleaned_text = re.sub(r'\*+([^*]+)\*+', r'\1', cleaned_text)
    # Remove bullet points at start of lines
    cleaned_text = re.sub(r'^[-•*]\s*', '', cleaned_text, flags=re.MULTILINE)
    
    lines = [l.strip() for l in cleaned_text.splitlines() if l.strip()]
    
    if not lines:
        return ""

    # Remove boilerplate/robotic language
    skip_phrases = [
        "based on the analysis", "here's what i found", "here are", "here is",
        "according to", "as per", "please note", "kindly", "you can",
        "it is recommended", "i recommend", "you should consider"
    ]
    
    filtered_lines = []
    for line in lines:
        line_lower = line.lower()
        if not any(phrase in line_lower for phrase in skip_phrases):
            # Make responses more conversational and colorful
            if line_lower.startswith(('the', 'this', 'that')):
                filtered_lines.append(line)
            elif any(word in line_lower for word in ['disease', 'pest', 'problem']):
                # Add concern emojis for problems
                if not any(emoji in line for emoji in ['🚨', '⚠️', '🔍']):
                    line = f"🚨 {line}"
                filtered_lines.append(line)
            elif any(word in line_lower for word in ['price', 'market', 'sell', 'buy']):
                # Add money emojis for market info
                if not any(emoji in line for emoji in ['💰', '📈', '📊']):
                    line = f"💰 {line}"
                filtered_lines.append(line)
            elif any(word in line_lower for word in ['scheme', 'subsidy', 'government']):
                # Add government emojis
                if not any(emoji in line for emoji in ['🏛️', '📋', '✅']):
                    line = f"🏛️ {line}"
                filtered_lines.append(line)
            elif any(word in line_lower for word in ['spray', 'apply', 'use', 'treatment']):
                # Add action emojis
                if not any(emoji in line for emoji in ['🌿', '💊', '🔧']):
                    line = f"🌿 {line}"
                filtered_lines.append(line)
            else:
                filtered_lines.append(line)

    # Take first max_lines and make them conversational
    result_lines = []
    for i, line in enumerate(filtered_lines[:max_lines]):
        # Make it more conversational
        if i == 0:
            # First line - make it engaging
            if 'disease' in line.lower() or 'problem' in line.lower():
                line = f"Looks like your crop has {line.lower()}"
            elif 'price' in line.lower():
                line = f"Good news about prices! {line}"
            elif 'scheme' in line.lower():
                line = f"There's a great scheme for you: {line}"
            else:
                line = f"Here's what I found: {line}"
        
        # Ensure each line is concise
        if len(line) > 120:
            line = line[:117] + "..."
        
        result_lines.append(line)

    return "\n".join(result_lines)