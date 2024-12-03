from datetime import datetime
import re

def map_month_name():
    """
    Membuat mapping nama bulan ke nomor bulan.
    """
    month_names = [
        ["Januari", "Jan", "January"], ["Februari", "Feb", "February"],
        ["Maret", "Mar", "March"], ["April", "Apr"], ["Mei", "May"],
        ["Juni", "Jun", "June"], ["Juli", "Jul", "July"],
        ["Agustus", "Agu", "Aug", "August"], ["September", "Sep"],
        ["Oktober", "Okt", "Oct", "October"], ["November", "Nov"],
        ["Desember", "Des", "Dec", "December"]
    ]
    return {name.lower(): f"{i+1:02}" for i, names in enumerate(month_names) for name in names}

month_mapping = map_month_name()

def parse_date(date_str, format_hint=None):
    """
    Mengonversi string tanggal menjadi objek datetime.

    Args:
        date_str (str): Tanggal dalam format string.
        format_hint (str, optional): Format tanggal yang diharapkan. Contoh: "%d %b %Y".

    Returns:
        datetime: Objek datetime hasil parsing.

    Raises:
        ValueError: Jika format tanggal tidak dikenali.
    """
    try:
        if format_hint:
            return datetime.strptime(date_str, format_hint)

        # Coba format umum: "12 Januari 2023"
        day, month_name, year = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str).groups()
        month_number = month_mapping.get(month_name.lower())
        if not month_number:
            raise ValueError(f"Bulan tidak dikenali: {month_name}")
        return datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")
    except Exception as e:
        raise ValueError(f"Error parsing date: {date_str} ({str(e)})")
