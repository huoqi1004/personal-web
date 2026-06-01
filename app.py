"""陶兴旺个人网站 - Flask 后端"""
import os, sqlite3, hashlib, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DATA_DIR = "/tmp/data" if os.environ.get("VERCEL") else os.path.join(BASE_DIR, "data")
DATABASE = os.path.join(DATA_DIR, "site.db")

# ── Database ──────────────────────────────────────────────
def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop("db", None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS personal_info (
            id INTEGER PRIMARY KEY, key TEXT UNIQUE NOT NULL, value TEXT
        );
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY, category TEXT NOT NULL, name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, slug TEXT UNIQUE NOT NULL,
            role TEXT, description TEXT, version TEXT, is_featured INTEGER DEFAULT 0,
            repo_url TEXT, sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS project_tech (
            id INTEGER PRIMARY KEY, project_id INTEGER, tech_name TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS project_metrics (
            id INTEGER PRIMARY KEY, project_id INTEGER, label TEXT, value TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY, level TEXT CHECK(level IN ("national","provincial","other")),
            date TEXT, name TEXT, grade TEXT, sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY, icon TEXT, name TEXT, description TEXT,
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS ctf_records (
            id INTEGER PRIMARY KEY, date TEXT, description TEXT, sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY, type TEXT CHECK(type IN ("edu","intern")),
            icon TEXT, title TEXT, school TEXT, major TEXT, year TEXT,
            extra TEXT, description TEXT, sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS site_config (
            id INTEGER PRIMARY KEY, key TEXT UNIQUE NOT NULL, value TEXT
        );
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY, title TEXT, url TEXT, date TEXT, source TEXT DEFAULT "csdn"
        );
    """)
    db.commit()
    # Seed default admin
    try:
        h = hashlib.sha256("admin123".encode()).hexdigest()
        db.execute("INSERT OR IGNORE INTO admin(username,password_hash) VALUES(?,?)", ("admin", h))
        db.commit()
    except: pass
    db.close()

# ── Auth ──────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*a, **kw):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return decorated

def seed_data():
    db = get_db()
    # Only seed if empty
    if db.execute("SELECT COUNT(*) FROM personal_info").fetchone()[0] > 0: return
    info = [
        ("name","陶兴旺"),("title","网络空间安全探索者 · AI安全大模型开发者 · CTF竞赛选手"),
        ("subtitle","专注智能安全防御体系构建，用AI重塑网络安全的边界"),
        ("location","中国 · 兰州"),("email","1716669652@qq.com"),("phone","13145244706"),
        ("wechat","txw20000701"),("github","https://github.com/huoqi1004"),
        ("csdn","https://blog.csdn.net/yourcsdn"),("about_p1","我是一名网络空间安全与人工智能交叉领域的探索者，就读于兰州博文科技学院信息管理与信息系统专业（专业排名前3%）。"),
        ("about_p2","从CTF赛场到AI安全大模型研发，我始终站在安全攻防的最前沿。主导开发了玄光安全GPT、玄鉴安全检测系统等多个安全产品，其中玄光安全GPT已迭代至2.0版本，检测准确率突破90%，并完成首家企业落地。"),
        ("about_p3","我相信AI for Security的力量——用智能重塑安全的边界，让防御体系从\"被动响应\"走向\"主动预见\"。"),
        ("hero_badge","AVAILABLE FOR OPPORTUNITIES"),("hero_typing_titles","网络空间安全探索者,AI安全大模型开发者,CTF竞赛选手,智能安全防御架构师"),
        ("ga_id",""),("giscus_repo",""),("giscus_repo_id",""),("giscus_category",""),("giscus_category_id","")
    ]
    for k,v in info: db.execute("INSERT OR IGNORE INTO personal_info(key,value) VALUES(?,?)",(k,v))
    skills = [
        ("网络安全","CTF竞赛"),("网络安全","Web安全"),("网络安全","渗透测试"),("网络安全","漏洞挖掘"),
        ("网络安全","应急响应"),("网络安全","威胁情报"),("网络安全","安全运维"),("网络安全","代码审计"),
        ("网络安全","网络攻防"),("网络安全","红蓝对抗"),("网络安全","安全评估"),
        ("AI & 大模型","大模型微调"),("AI & 大模型","MoE架构"),("AI & 大模型","VGG16"),("AI & 大模型","CNN"),
        ("AI & 大模型","模型迁移"),("AI & 大模型","模型压缩"),("AI & 大模型","边缘部署"),("AI & 大模型","NLP"),
        ("AI & 大模型","PyTorch"),("AI & 大模型","深度学习"),("AI & 大模型","AI Agent"),
        ("开发 & 工具","Python"),("开发 & 工具","C++"),("开发 & 工具","SQL"),("开发 & 工具","Linux"),
        ("开发 & 工具","Docker"),("开发 & 工具","Git"),("开发 & 工具","GitHub"),("开发 & 工具","网络布线"),
        ("开发 & 工具","设备部署"),("开发 & 工具","技术文档"),("开发 & 工具","项目管理"),
    ]
    for c,n in skills: db.execute("INSERT INTO skills(category,name) VALUES(?,?)",(c,n))
    projects = [
        ("玄光安全GPT","xuan-guang-gpt","项目负责人 · 产品经理","基于通用大模型+安全专有MoE协同监督机制的网络空间安全大模型。有效应对当前主流网络攻击态势，同时覆盖传统网络安全问题，尤其擅长企业级数据安全防护。","v2.0",1,"https://github.com/huoqi1004/XuanGuang-GPT-",0),
        ("玄鉴安全检测系统","xuan-jian","项目负责人 · 架构设计师","基于大模型技术栈的智能安全检测系统，集成漏洞检测、资产测绘、威胁情报匹配三大核心能力。既可从安全知识库进行实时匹配推理，也可从全网实时获取威胁情报，为企业信息安全提供全方位防护。","",0,"https://github.com/youngestar/System.git",1),
        ("神农AI识别系统","shen-nong-ai","产品孵化","基于VGG16+CNN特征融合的农作物病虫害识别系统。通过多尺度特征融合、动态学习率优化、模型压缩等技术，在5种病害3300张图像上准确率达98.6%，模型压缩至2.1M，边缘设备32 FPS实时推理。","",0,"https://github.com/AAAkater/VGG.git",2),
        ("水木智慧安防平台","shui-mu","项目负责人","面向大型场馆、医院、学校等关键基础设施的智能安防平台。融合边缘计算、智能感知、深度学习与区块链技术，实现自动化、智能化、轻量化的实时安全监控与应急响应。","",0,"",3),
        ("智慧物流信息系统","zhi-hui-wu-liu","项目负责人","基于5G、IoT、云计算等技术构建的全链路智慧物流平台，覆盖采购、运输、装卸、仓储、安全全业务场景，实现物流流程的智能化与智慧化。获第十四届挑战杯校级银奖。","",0,"",4),
    ]
    for n,s,r,d,v,fe,repo,so in projects:
        db.execute("INSERT INTO projects(name,slug,role,description,version,is_featured,repo_url,sort_order) VALUES(?,?,?,?,?,?,?,?)",(n,s,r,d,v,fe,repo,so))
    # Project techs
    techs = {1:["大语言模型","MoE架构","协同监督","威胁检测","数据安全"],2:["大模型","漏洞检测","资产测绘","威胁情报","RAG"],3:["VGG16","CNN","特征融合","模型压缩","边缘计算","Jetson Nano"],4:["边缘计算","深度学习","智能感知","区块链","实时监控"],5:["5G","IoT","云计算","大数据","分布式存储"]}
    for pid,tlist in techs.items():
        for t in tlist: db.execute("INSERT INTO project_tech(project_id,tech_name) VALUES(?,?)",(pid,t))
    # Project metrics
    metrics = {1:[(">90%","检测准确率"),("1家","企业落地"),("v2.0","持续迭代")],2:[("10+","竞赛奖项"),("2家","企业对接"),("省级","立项项目")],3:[("98.6%","识别准确率"),("2.1MB","模型体积"),("32FPS","边缘推理")],5:[("校级","银奖"),("全链路","业务覆盖")]}
    for pid,mlist in metrics.items():
        for v,l in mlist: db.execute("INSERT INTO project_metrics(project_id,value,label) VALUES(?,?,?)",(pid,v,l))
    awards = [
        ("national","2025.10","第十九届挑战杯全国大学生课外学术科技作品竞赛","国家二等奖",0),
        ("national","2025.08","第一届全国大学生人工智能安全竞赛全国总决赛","国家二等奖",1),
        ("national","2024.03","第四届复兴杯全国大学生网络安全精英赛","全国排名1229",2),
        ("national","2024.06","第八届全国职工职业技能大赛上海选拔赛（网络安全）","第68名",3),
        ("national","2025.08","2025全国开源大赛决赛","入围",4),
        ("provincial","2025.09","甘肃省第十九届挑战杯","省级特等奖",0),
        ("provincial","2025.06","第十一届甘肃省大学生创新大赛","省级金奖+银奖",1),
        ("provincial","2024.09","第十四届挑战杯中国大学生创业计划竞赛","省级铜奖",2),
        ("provincial","2023.12","第十三届新华三杯大学生数字技术大赛","省级二等奖",3),
        ("provincial","2025.05","第二十届波音杯 · 应急先锋","省级二等奖",4),
        ("provincial","2025.11","甘肃省创新方法大赛","省级二等奖",5),
        ("other","2025","三好学生","",0),("other","2024.05","优秀共青团员","",1),
        ("other","2022.04","圣日耳曼杯 · 省级二等奖","",2),("other","2023.05","普通话考试通过","",3),
        ("other","2023","全国大学生数字技术应用大赛 · 三等奖","",4),
    ]
    for lv,dt,nm,gd,so in awards: db.execute("INSERT INTO awards(level,date,name,grade,sort_order) VALUES(?,?,?,?,?)",(lv,dt,nm,gd,so))
    certs = [("☁️","ACA 助理工程师","阿里云云计算助理工程师认证"),("🔐","H3C-NE","新华三网络安全工程师"),("📝","软件著作权","计算机软件著作权登记"),("🌍","AGE Fellow","AGE全球共济会荣誉博士"),("🤖","CAAI会员","中国人工智能学会")]
    for i,n,d in certs: db.execute("INSERT INTO certifications(icon,name,description) VALUES(?,?,?)",(i,n,d))
    ctfs = [("2025.05","第二届齐鲁杯CTF大赛 — 应急先锋称号（全国排名39）"),("2025.04","第十五届蓝桥杯 — 校级一等奖"),("2025.04","第三届网络空间安全前沿论坛 · 青年论坛 — 科技成果展示"),("2024.05","ISCC信息安全竞赛"),("2024.05","第二届京麒CTF大赛"),("2024.04","阿里巴巴网络安全CTF专题赛"),("2025.11","全国AI Agent专题赛 — 最佳跨越奖")]
    for d,desc in ctfs: db.execute("INSERT INTO ctf_records(date,description) VALUES(?,?)",(d,desc))
    edu = [("edu","🎓","教育背景","兰州博文科技学院","信息管理与信息系统","2022 - 2026","专业排名：前 3%","信息安全基础, C++, SQL, 数据结构, 计算机网络"),("intern","💼","实习经历","兰州佳宏信息科技有限公司","网络工程师","2024.07 - 2024.08","","负责天水师范学院信息中心项目的网络设备安装部署与网络布线规划")]
    for tp,ic,ti,sc,mj,yr,ex,ds in edu: db.execute("INSERT INTO education(type,icon,title,school,major,year,extra,description) VALUES(?,?,?,?,?,?,?,?)",(tp,ic,ti,sc,mj,yr,ex,ds))
    db.commit()

# ── Helpers ───────────────────────────────────────────────
def get_config(key, default=""):
    row = get_db().execute("SELECT value FROM personal_info WHERE key=?",(key,)).fetchone()
    return row["value"] if row and row["value"] else default

def get_site_config(key, default=""):
    row = get_db().execute("SELECT value FROM site_config WHERE key=?",(key,)).fetchone()
    return row["value"] if row and row["value"] else default

# ── Init ──────────────────────────────────────────────────
@app.before_request
def ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR,"templates"), exist_ok=True)
    init_db()
    seed_data()

# ── Public Routes ─────────────────────────────────────────
@app.route("/")
def index():
    db = get_db()
    info = {r["key"]:r["value"] for r in db.execute("SELECT key,value FROM personal_info").fetchall()}
    skills = db.execute("SELECT category, name FROM skills ORDER BY category, sort_order").fetchall()
    proj_list = []
    for p in db.execute("SELECT * FROM projects ORDER BY sort_order").fetchall():
        pd = dict(p)
        pd["techs"] = [r["tech_name"] for r in db.execute("SELECT tech_name FROM project_tech WHERE project_id=? ORDER BY rowid",(pd["id"],)).fetchall()]
        pd["metrics"] = [dict(r) for r in db.execute("SELECT value,label FROM project_metrics WHERE project_id=?",(pd["id"],)).fetchall()]
        proj_list.append(pd)
    awards_nat = db.execute("SELECT * FROM awards WHERE level='national' ORDER BY sort_order").fetchall()
    awards_prov = db.execute("SELECT * FROM awards WHERE level='provincial' ORDER BY sort_order").fetchall()
    awards_other = db.execute("SELECT * FROM awards WHERE level='other' ORDER BY sort_order").fetchall()
    certs = db.execute("SELECT * FROM certifications ORDER BY sort_order").fetchall()
    ctfs = db.execute("SELECT * FROM ctf_records ORDER BY sort_order").fetchall()
    edu = db.execute("SELECT * FROM education ORDER BY sort_order").fetchall()
    ga_id = get_site_config("ga_id","")
    giscus = {"repo":get_site_config("giscus_repo",""),"repo_id":get_site_config("giscus_repo_id",""),"category":get_site_config("giscus_category",""),"category_id":get_site_config("giscus_category_id","")}
    return render_template("index.html", info=info, skills=skills, projects=proj_list, awards_nat=awards_nat, awards_prov=awards_prov, awards_other=awards_other, certs=certs, ctfs=ctfs, edu=edu, ga_id=ga_id, giscus=giscus)

@app.route("/project/<slug>")
def project_detail(slug):
    db = get_db()
    p = db.execute("SELECT * FROM projects WHERE slug=?",(slug,)).fetchone()
    if not p: return "项目不存在", 404
    pd = dict(p)
    pd["techs"] = [r["tech_name"] for r in db.execute("SELECT tech_name FROM project_tech WHERE project_id=? ORDER BY rowid",(pd["id"],)).fetchall()]
    pd["metrics"] = [dict(r) for r in db.execute("SELECT value,label FROM project_metrics WHERE project_id=?",(pd["id"],)).fetchall()]
    ga_id = get_site_config("ga_id","")
    return render_template("project.html", project=pd, ga_id=ga_id)

@app.route("/timeline")
def timeline():
    db = get_db()
    awards_all = db.execute("SELECT date,name,grade,level FROM awards ORDER BY date").fetchall()
    ctfs_all = db.execute("SELECT date,description FROM ctf_records ORDER BY date").fetchall()
    ga_id = get_site_config("ga_id","")
    return render_template("timeline.html", awards=awards_all, ctfs=ctfs_all, ga_id=ga_id)

# ── Admin Routes ──────────────────────────────────────────
@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    h = hashlib.sha256(data.get("password","").encode()).hexdigest()
    user = get_db().execute("SELECT * FROM admin WHERE username=? AND password_hash=?",(data.get("username"),h)).fetchone()
    if user:
        session["admin"] = user["username"]
        return jsonify({"ok":True})
    return jsonify({"ok":False,"error":"用户名或密码错误"}), 401

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None)
    return redirect(url_for("admin_login_page"))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

# ── Admin API ─────────────────────────────────────────────
def admin_api(f):
    @wraps(f)
    @login_required
    def wrapper(*a,**kw): return f(*a,**kw)
    return wrapper

@app.route("/api/admin/info", methods=["GET","POST"])
@admin_api
def api_info():
    db = get_db()
    if request.method == "POST":
        for k,v in request.get_json().items():
            db.execute("INSERT OR REPLACE INTO personal_info(key,value) VALUES(?,?)",(k,v))
        db.commit()
        return jsonify({"ok":True})
    rows = db.execute("SELECT key,value FROM personal_info").fetchall()
    return jsonify({r["key"]:r["value"] for r in rows})

@app.route("/api/admin/site-config", methods=["GET","POST"])
@admin_api
def api_site_config():
    db = get_db()
    if request.method == "POST":
        for k,v in request.get_json().items():
            db.execute("INSERT OR REPLACE INTO site_config(key,value) VALUES(?,?)",(k,v))
        db.commit()
        return jsonify({"ok":True})
    rows = db.execute("SELECT key,value FROM site_config").fetchall()
    return jsonify({r["key"]:r["value"] for r in rows})

@app.route("/api/admin/projects", methods=["GET","POST"])
@admin_api
def api_projects():
    db = get_db()
    if request.method == "POST":
        p = request.get_json()
        if p.get("id"):
            db.execute("UPDATE projects SET name=?,slug=?,role=?,description=?,version=?,is_featured=?,repo_url=?,sort_order=? WHERE id=?",(p["name"],p["slug"],p["role"],p["description"],p.get("version",""),p.get("is_featured",0),p.get("repo_url",""),p.get("sort_order",0),p["id"]))
        else:
            db.execute("INSERT INTO projects(name,slug,role,description,version,is_featured,repo_url,sort_order) VALUES(?,?,?,?,?,?,?,?)",(p["name"],p["slug"],p["role"],p["description"],p.get("version",""),p.get("is_featured",0),p.get("repo_url",""),p.get("sort_order",0)))
        db.commit()
        return jsonify({"ok":True})
    rows = db.execute("SELECT * FROM projects ORDER BY sort_order").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/projects/<int:pid>/techs", methods=["GET","POST"])
@admin_api
def api_project_techs(pid):
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM project_tech WHERE project_id=?",(pid,))
        for t in request.get_json().get("techs",[]):
            db.execute("INSERT INTO project_tech(project_id,tech_name) VALUES(?,?)",(pid,t))
        db.commit()
        return jsonify({"ok":True})
    rows = db.execute("SELECT * FROM project_tech WHERE project_id=?",(pid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/projects/<int:pid>/metrics", methods=["GET","POST"])
@admin_api
def api_project_metrics(pid):
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM project_metrics WHERE project_id=?",(pid,))
        for m in request.get_json().get("metrics",[]):
            db.execute("INSERT INTO project_metrics(project_id,value,label) VALUES(?,?,?)",(pid,m["value"],m["label"]))
        db.commit()
        return jsonify({"ok":True})
    rows = db.execute("SELECT * FROM project_metrics WHERE project_id=?",(pid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/projects/<int:pid>", methods=["DELETE"])
@admin_api
def api_project_delete(pid):
    get_db().execute("DELETE FROM projects WHERE id=?",(pid,)); get_db().commit()
    return jsonify({"ok":True})

@app.route("/api/admin/skills", methods=["GET","POST"])
@admin_api
def api_skills():
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM skills")
        for s in request.get_json():
            db.execute("INSERT INTO skills(category,name,sort_order) VALUES(?,?,?)",(s["category"],s["name"],s.get("sort_order",0)))
        db.commit(); return jsonify({"ok":True})
    return jsonify([dict(r) for r in db.execute("SELECT * FROM skills ORDER BY category,sort_order").fetchall()])

@app.route("/api/admin/awards", methods=["GET","POST"])
@admin_api
def api_awards():
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM awards")
        for a in request.get_json():
            db.execute("INSERT INTO awards(level,date,name,grade,sort_order) VALUES(?,?,?,?,?)",(a["level"],a["date"],a["name"],a.get("grade",""),a.get("sort_order",0)))
        db.commit(); return jsonify({"ok":True})
    return jsonify([dict(r) for r in db.execute("SELECT * FROM awards ORDER BY level,sort_order").fetchall()])

@app.route("/api/admin/certs", methods=["GET","POST"])
@admin_api
def api_certs():
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM certifications")
        for c in request.get_json():
            db.execute("INSERT INTO certifications(icon,name,description,sort_order) VALUES(?,?,?,?)",(c["icon"],c["name"],c.get("description",""),c.get("sort_order",0)))
        db.commit(); return jsonify({"ok":True})
    return jsonify([dict(r) for r in db.execute("SELECT * FROM certifications ORDER BY sort_order").fetchall()])

@app.route("/api/admin/ctf", methods=["GET","POST"])
@admin_api
def api_ctf():
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM ctf_records")
        for c in request.get_json():
            db.execute("INSERT INTO ctf_records(date,description,sort_order) VALUES(?,?,?)",(c["date"],c["description"],c.get("sort_order",0)))
        db.commit(); return jsonify({"ok":True})
    return jsonify([dict(r) for r in db.execute("SELECT * FROM ctf_records ORDER BY sort_order").fetchall()])

@app.route("/api/admin/education", methods=["GET","POST"])
@admin_api
def api_education():
    db = get_db()
    if request.method == "POST":
        db.execute("DELETE FROM education")
        for e in request.get_json():
            db.execute("INSERT INTO education(type,icon,title,school,major,year,extra,description,sort_order) VALUES(?,?,?,?,?,?,?,?,?)",(e["type"],e["icon"],e["title"],e["school"],e["major"],e["year"],e.get("extra",""),e.get("description",""),e.get("sort_order",0)))
        db.commit(); return jsonify({"ok":True})
    return jsonify([dict(r) for r in db.execute("SELECT * FROM education ORDER BY sort_order").fetchall()])

# CSDN Blog Proxy (avoid CORS)
@app.route("/api/blog")
def api_blog():
    db = get_db()
    rows = db.execute("SELECT * FROM blog_posts ORDER BY date DESC LIMIT 20").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/blog", methods=["POST"])
@admin_api
def api_blog_refresh():
    # Manual blog sync – admin posts URLs
    data = request.get_json()
    db = get_db()
    if data.get("action") == "add":
        db.execute("INSERT INTO blog_posts(title,url,date,source) VALUES(?,?,?,?)",(data["title"],data["url"],data["date"],data.get("source","csdn")))
    elif data.get("action") == "clear":
        db.execute("DELETE FROM blog_posts")
    db.commit()
    return jsonify({"ok":True})

# ── Run ───────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR,"templates"), exist_ok=True)
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
