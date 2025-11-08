def mask_secret(s: str | None) -> str:
    if not s:
        return ""
    if len(s) <= 2:
        return "*" * len(s)
    return s[0] + "****" + s[-1]
