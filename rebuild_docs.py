"""Rebuild static site for GitHub Pages"""
import os, json, sqlite3, shutil, glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE = os.path.join(DATA_DIR, "site.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")

def get_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    info = {r["key"]: r["value"] for r in db.execute("SELECT key,value FROM personal_info").fetchall()}
    skills = db.execute("SELECT category, name FROM skills ORDER BY category, sort_order").fetchall()
    projects = []
    for p in db.execute("SELECT * FROM projects ORDER BY sort_order").fetchall():
        pd = dict(p)
        pd["techs"] = [r["tech_name"] for r in db.execute("SELECT tech_name FROM project_tech WHERE project_id=? ORDER BY rowid",(pd["id"],)).fetchall()]
        pd["metrics"] = [dict(r) for r in db.execute("SELECT value,label FROM project_metrics WHERE project_id=?",(pd["id"],)).fetchall()]
        projects.append(pd)
    awards_nat = [dict(r) for r in db.execute("SELECT * FROM awards WHERE level='national' ORDER BY sort_order").fetchall()]
    awards_prov = [dict(r) for r in db.execute("SELECT * FROM awards WHERE level='provincial' ORDER BY sort_order").fetchall()]
    awards_other = [dict(r) for r in db.execute("SELECT * FROM awards WHERE level='other' ORDER BY sort_order").fetchall()]
    certs = [dict(r) for r in db.execute("SELECT * FROM certifications ORDER BY sort_order").fetchall()]
    ctfs = [dict(r) for r in db.execute("SELECT * FROM ctf_records ORDER BY sort_order").fetchall()]
    edu = [dict(r) for r in db.execute("SELECT * FROM education ORDER BY sort_order").fetchall()]
    images_dir = os.path.join(BASE_DIR, "images")
    honor_images = []
    if os.path.exists(images_dir):
        for ext in ["jpg","jpeg","png","gif","webp"]:
            for fp in glob.glob(os.path.join(images_dir, "*." + ext)):
                fn = os.path.basename(fp)
                base = os.path.splitext(fn)[0]
                parts = base.split("_")
                if len(parts) >= 2:
                    level = parts[-1] if parts[-1] in ["national","provincial","other"] else "other"
                    name = "_".join(parts[:-1]) if level in parts else base
                else:
                    level, name = "other", base
                honor_images.append({"name": name, "level": level, "filename": fn})
    conn.close()
    return {
        "info": info,
        "skills": [{"category": r["category"], "name": r["name"]} for r in skills],
        "projects": projects,
        "awards_nat": awards_nat,
        "awards_prov": awards_prov,
        "awards_other": awards_other,
        "certs": certs,
        "ctfs": ctfs,
        "edu": edu,
        "honor_images": honor_images
    }

# Export data
data = get_data()
with open(os.path.join(BASE_DIR, "static_data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Build docs
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)
os.makedirs(os.path.join(OUTPUT_DIR, "static", "js"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "static", "css"), exist_ok=True)

for src_sub in ["static/css", "static/js", "images"]:
    src_dir = os.path.join(BASE_DIR, src_sub)
    dst_dir = os.path.join(OUTPUT_DIR, src_sub)
    if os.path.exists(dst_dir):
        if os.path.isdir(dst_dir): shutil.rmtree(dst_dir)
        else: os.remove(dst_dir)
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dst_dir)

# data.js
with open(os.path.join(OUTPUT_DIR, "static", "data.js"), "w", encoding="utf-8") as f:
    f.write("window.SITE_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

# Copy index template
shutil.copy(os.path.join(BASE_DIR, "docs_index_template.html"), os.path.join(OUTPUT_DIR, "index.html"))

# .nojekyll
with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w") as f:
    f.write("")

print("Static site rebuilt successfully")
print("Files:", os.listdir(OUTPUT_DIR))
