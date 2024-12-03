from datetime import datetime

def map_month_name():
    """
    Membangun mapping nama bulan ke nomor bulan.
    """
    month_names = [
        ["Januari", "Jan", "January"], ["Februari", "Feb", "February"],
        ["Maret", "Mar", "March"], ["April", "Apr"], ["Mei", "May"],
        ["Juni", "Jun", "June"], ["Juli", "Jul", "July"],
        ["Agustus", "Agu", "Aug", "August"], ["September", "Sep"],
        ["Oktober", "Okt", "Oct", "October"], ["November", "Nov"],
        ["Desember", "Des", "Dec", "December"]
    ]
    return {name: f"{i+1:02}" for i, names in enumerate(month_names) for name in names}

month_mapping = map_month_name()

def parse_date(day, month_name, year):
    """
    Mengubah string tanggal ke format datetime.
    """
    try:
        month_number = month_mapping.get(month_name, "00")
        return datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")
    except Exception as e:
        raise ValueError(f"Error parsing date: {e}")
