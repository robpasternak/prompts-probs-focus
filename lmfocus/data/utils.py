"""Utility functions."""

def capitalize_first_letter(s: str, ignore_string: str) -> str:
    """
    Capitalizes the first letter of a string, not counting the ignore_string.
    """
    if not s:
        return s
    if s.startswith(ignore_string):
        return ignore_string + s[len(ignore_string)].upper() + s[len(ignore_string)+1:]
    return s[0].upper() + s[1:]

def replace_focus_with_all_caps(string: str) -> str:
    """
    Remove focus markers (<<>>) from the string and convert
    the focused part of the string to upper case.
    For example, "This is a <<test>> string." becomes "This is a TEST string."
    """
    while '<<' in string and '>>' in string:
        start = string.index('<<')
        end = string.index('>>', start)
        focused_part = string[start + 2:end]
        string = string[:start] + focused_part.upper() + string[end + 2:]
    return string.strip()

def replace_focus_with_bracketing(string: str, start_bracket: str, end_bracket: str) -> str:
    """
    Remove focus markers (<<>>) from the string and replace them with brackets.
    For example, "This is a <<test>> string." becomes "This is a [test] string."
    """
    return string.strip().replace('<<', start_bracket).replace('>>', end_bracket)