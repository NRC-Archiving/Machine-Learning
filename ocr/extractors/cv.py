import re
from extractors.utils import parse_date

def extract_cv(text):
    """
    Ekstrak data dari dokumen CV.
    """
    patterns = {
        "experience": r"(\b\w+\s\d{4}\s-\s(?:\w+\s\d{4}|Present|[Ss]ekarang))\s*:\s*(.*)\n([\s\S]+?)(?=\n\n|\Z)",
        "nama": r"Nama\s*:\s*(.*)",
        "ttl": r"Lahir\s*:\s*(.*)",
        "education": r"Pendidikan\s*:\s*(.*?)(?=\n\n|$)",
        "degree_year": r"([A-Za-z0-9]+( [A-Za-z0-9]+)+)\s*-\s*[0-9]+"
    }

    try:
        hasil = {}
        # Ekstraksi nama
        nama_match = re.search(patterns["nama"], text)
        hasil["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Ekstraksi TTL
        ttl_match = re.search(patterns["ttl"], text)
        hasil["ttl"] = ttl_match.group(1).strip() if ttl_match else "N/A"

        # Ekstraksi pendidikan
        education_match = re.search(patterns["education"], text, re.MULTILINE)
        if education_match:
            univ = education_match.group(1).strip()  # Assign the full education text to univ
            print(f"Debug: Extracted university text: {univ}")  # Debugging line

            # Extract degree and graduation year from the university text
            degree_year_match = re.search(patterns["degree_year"], univ, re.MULTILINE)
            hasil["degree_year"] = degree_year_match.group(1).strip()
            print(hasil["degree_year"])
            if degree_year_match:
                degree, graduation_year = degree_year_match.groups()
                hasil["education"] = {
                    "university": univ,
                    "degree": degree.strip(),
                    "graduation_year": int(graduation_year)
                }
            else:
                hasil["education"] = {
                    "university": univ,
                    "degree": "N/A",
                    "graduation_year": "N/A"
                }
        # if education_match:
        #     univ, gelar, lulus = education_match.groups()
        #     hasil["education"] = {
        #         "university": univ.strip(),
        #         "degree": gelar.strip(),
        #         "graduation_year": int(lulus)
        #     }

        # Ekstraksi pengalaman kerja
        # experiences = []
        # for date_range, role, project in re.findall(patterns["experience"], text):
        #     try:
        #         company_name_match = re.search(r"(.*)\n" + re.escape(date_range), text)
        #         company_name = company_name_match.group(1).strip() if company_name_match else "Unknown Company"
        #         start_date, end_date = map(parse_date, date_range.split(" - "))
        #         duration = (end_date - start_date).days / 365.25

        #         experiences.append({
        #             "company": company_name,
        #             "role": role.strip() if role else "No role specified",
        #             "project": project.replace("\n", " "),
        #             "start_date": start_date.strftime("%d-%m-%Y") if start_date else None,
        #             "end_date": end_date.strftime("%d-%m-%Y") if end_date else None,
        #             "duration_years": round(duration, 2)
        #         })
        #     except Exception as e:
        #         continue  # Skip invalid entries

        # # Menentukan pengalaman terbaru dan total durasi pengalaman
        # if experiences:
        #     latest_experience = max(experiences, key=lambda x: x["end_date"])
        #     total_years = round(sum(exp["duration_years"] for exp in experiences if exp["duration_years"]), 2)
        #     hasil["latest_experience"] = {
        #         "project": latest_experience["project"],
        #         "company": latest_experience["company"],
        #         "role": latest_experience["role"]
        #     }
        #     hasil["total_years_of_experience"] = total_years
        # else:
        #     hasil["latest_experience"] = "No experience found"
        #     hasil["total_years_of_experience"] = 0

        # hasil["experiences"] = experiences

        return hasil
    except Exception as e:
        return {"error": f"Error processing CV: {str(e)}"}
