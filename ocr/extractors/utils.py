import re
from datetime import datetime

def map_month_name():
    month_names = [
        ["Januari", "Jan", "January"], ["Februari", "Feb", "February"],
        ["Maret", "Mar", "March"], ["April", "Apr"], ["Mei", "May"],
        ["Juni", "Jun", "June"], ["Juli", "Jul", "July"],
        ["Agustus", "Agu", "Agt", "Aug", "August"], ["September", "Sep"],
        ["Oktober", "Okt", "Oct", "October"], ["November", "Nov"],
        ["Desember", "Des", "Dec", "December"]
    ]
    return {name.lower(): f"{i+1:02}" for i, names in enumerate(month_names) for name in names}

month_mapping = map_month_name()

def parse_date(date_str, format_hint=None):
    try:
        if format_hint:
            return datetime.strptime(date_str, format_hint)

        # Match full date: "12 Januari 2023"
        match = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str)
        if match:
            day, month_name, year = match.groups()
            month_number = month_mapping.get(month_name.lower())
            if not month_number:
                raise ValueError(f"Bulan tidak dikenali: {month_name}")
            return datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")

        # Match Month Day, Year: "December 31, 2020"
        match = re.match(r"(\w+)\s+(\d{1,2}),\s+(\d{4})", date_str)
        if match:
            month_name, day, year = match.groups()
            month_number = month_mapping.get(month_name.lower())
            if not month_number:
                raise ValueError(f"Bulan tidak dikenali: {month_name}")
            return datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")

        # Match partial date: "Jan 2004" (default day = 1)
        match = re.match(r"(\w+)\s+(\d{4})", date_str)
        if match:
            month_name, year = match.groups()
            month_number = month_mapping.get(month_name.lower())
            if not month_number:
                raise ValueError(f"Bulan tidak dikenali: {month_name}")
            return datetime.strptime(f"01-{month_number}-{year}", "%d-%m-%Y")

        raise ValueError(f"Tanggal tidak valid: {date_str}")
    except Exception as e:
        raise ValueError(f"Error parsing date: {date_str} ({str(e)})")