import jdatetime
from datetime import datetime
def normalize_to_gregorian(date_str: str) -> str:
    """
    Takes a date string (Jalali or Gregorian) and converts it to
    standard Gregorian format (YYYY-MM-DD).
    
    Examples:
        "1404-09-12" -> "2025-12-03"
        "1404/9/12"  -> "2025-12-03"
        "2025-12-03" -> "2025-12-03"
    """
    if not date_str:
        raise ValueError("Date string cannot be empty")

    # Normalize separators
    clean_date = date_str.replace("/", "-").strip()
    
    try:
        parts = clean_date.split("-")
        if len(parts) != 3:
            raise ValueError("Invalid format")
            
        y, m, d = map(int, parts)
        
        # Logic: If year is less than 1700, assume Jalali (Shamsi)
        if y < 1700:
            gregorian_date = jdatetime.date(y, m, d).togregorian()
            return gregorian_date.strftime("%Y-%m-%d")
        else:
            # Validate it's a correct Gregorian date
            valid_date = datetime(y, m, d)
            return valid_date.strftime("%Y-%m-%d")
            
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date: {date_str}. Use YYYY-MM-DD or YYYY/MM/DD.")