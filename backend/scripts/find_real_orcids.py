import urllib.request
import urllib.parse
import json

faculty_names = [
    ("KLE-FAC-001", "Dr. Ashok Kumar Shettar", "Ashok Shettar"),
    ("KLE-FAC-002", "Dr. Nalini C. Iyer", "Nalini Iyer"),
    ("KLE-FAC-003", "Dr. Nagaraj Ramalingayya Banapurmath", "Nagaraj Banapurmath"),
    ("KLE-FAC-004", "Dr. Ashok M. Sajjan", "Ashok M. Sajjan"),
    ("KLE-FAC-005", "Dr. A. Y. Patil", "Arun Y. Patil"),
    ("KLE-FAC-006", "Dr. Sharanabasava V. Ganachari", "Sharanabasava Ganachari"),
    ("KLE-FAC-007", "Dr. D. G. Narayan", "D. G. Narayan"),
    ("KLE-FAC-008", "Prof. M. A. Umarfarooq", "M. A. Umarfarooq"),
    ("KLE-FAC-009", "Dr. Rajashri Khanai", "Rajashri Khanai"),
    ("KLE-FAC-010", "Dr. Sridhar Iyer", "Sridhar Iyer"),
    ("KLE-FAC-011", "Dr. Dattaprasad A. Torse", "Dattaprasad Torse"),
    ("KLE-FAC-012", "Dr. Basavaraj G. Katageri", "Basavaraj Katageri"),
    ("KLE-FAC-013", "Dr. Rajkumar V. Raikar", "Rajkumar Raikar"),
    ("KLE-FAC-014", "Dr. Vinayak Adimule", "Vinayak Adimule"),
    ("KLE-FAC-015", "Dr. S. Kotrappa", "S. Kotrappa"),
    ("KLE-FAC-016", "Dr. Udaykumar L. Naik", "Udaykumar Naik"),
    ("KLE-FAC-017", "Dr. Veerendrakumar C. Khed", "Veerendrakumar Khed"),
]

for fid, full_name, search_name in faculty_names:
    query = urllib.parse.quote(search_name)
    url = f"https://api.openalex.org/authors?search={query}"
    req = urllib.request.Request(url, headers={"User-Agent": "mailto:research-portal@kletech.ac.in"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            chosen = None
            for r in results:
                orcid = r.get("orcid")
                works = r.get("works_count", 0)
                affils = [a.get("institution", {}).get("display_name", "") for a in r.get("affiliations", [])]
                if orcid:
                    chosen = (r.get("display_name"), orcid.replace("https://orcid.org/", ""), works, affils[:1])
                    break
            if not chosen and results:
                r = results[0]
                chosen = (r.get("display_name"), r.get("orcid"), r.get("works_count", 0), [a.get("institution", {}).get("display_name", "") for a in r.get("affiliations", [])][:1])
            print(f"{fid} | {full_name} -> {chosen}")
    except Exception as e:
        print(f"{fid} | {full_name} -> ERROR: {e}")
