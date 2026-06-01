"""Complete rebuild for GitHub Pages - exports data and generates all static files"""
import os, json, sqlite3, shutil, glob

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "data", "site.db")
OUT = os.path.join(BASE, "docs")

def get_data():
    conn = sqlite3.connect(DB)
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
    img_dir = os.path.join(BASE, "images")
    honor_images = []
    if os.path.exists(img_dir):
        for ext in ["jpg","jpeg","png","gif","webp"]:
            for fp in glob.glob(os.path.join(img_dir, "*." + ext)):
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

data = get_data()

# Clean
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
os.makedirs(os.path.join(OUT, "static", "js"), exist_ok=True)
os.makedirs(os.path.join(OUT, "static", "css"), exist_ok=True)

# Copy static assets
for sub in ["static/css", "static/js", "images"]:
    src = os.path.join(BASE, sub)
    dst = os.path.join(OUT, sub)
    if os.path.exists(dst):
        if os.path.isdir(dst): shutil.rmtree(dst)
        else: os.remove(dst)
    if os.path.exists(src):
        shutil.copytree(src, dst)

# Generate data.js
with open(os.path.join(OUT, "static", "data.js"), "w", encoding="utf-8") as f:
    f.write("window.SITE_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

# Generate render.js
render_js = r'''(function(){
  var D = window.SITE_DATA || {};
  var info = D.info || {};

  if (info.name) document.getElementById("hero-name").textContent = info.name;
  if (info.subtitle) document.getElementById("hero-desc").textContent = info.subtitle;
  if (info.about_p1) document.getElementById("about-p1").textContent = info.about_p1;
  if (info.about_p2) document.getElementById("about-p2").textContent = info.about_p2;
  if (info.about_p3) document.getElementById("about-p3").textContent = info.about_p3;

  var eduContainer = document.getElementById("edu-container");
  if (eduContainer) {
    (D.edu || []).forEach(function(e) {
      var card = document.createElement("div");
      card.className = "edu-card";
      var html = '<div class="edu-icon">' + (e.icon || "🎓") + '</div><h3>' + (e.title || "") + '</h3><div class="edu-info">';
      if (e.school) html += '<p class="edu-school">' + e.school + '</p>';
      if (e.major) html += '<p class="edu-major">' + e.major + '</p>';
      if (e.year) html += '<p class="edu-year">' + e.year + '</p>';
      if (e.extra) html += '<p class="edu-rank">' + e.extra + '</p>';
      if (e.description) html += '<p class="edu-desc">' + e.description + '</p>';
      html += '</div>';
      card.innerHTML = html;
      eduContainer.appendChild(card);
    });
  }

  var skillsContainer = document.getElementById("skills-container");
  if (skillsContainer) {
    var skills = D.skills || [];
    var catMap = {};
    skills.forEach(function(s) {
      if (!catMap[s.category]) catMap[s.category] = [];
      catMap[s.category].push(s.name);
    });
    Object.keys(catMap).forEach(function(cat) {
      var div = document.createElement("div");
      div.className = "skill-category";
      var html = '<h3>' + cat + '</h3><div class="skill-tags">';
      catMap[cat].forEach(function(n) { html += '<span>' + n + '</span>'; });
      html += '</div>';
      div.innerHTML = html;
      skillsContainer.appendChild(div);
    });
  }

  var projContainer = document.getElementById("projects-container");
  if (projContainer) {
    (D.projects || []).forEach(function(p) {
      var card = document.createElement("div");
      card.className = "project-card" + (p.is_featured ? " featured" : "");
      var html = '<div class="project-header">';
      if (p.is_featured) html += '<span class="project-tag tag-featured">🌟 旗舰项目</span>';
      if (p.version) html += '<span class="project-version">' + p.version + '</span>';
      html += '</div><h3 class="project-name">' + p.name + '</h3>';
      if (p.role) html += '<p class="project-role">' + p.role + '</p>';
      if (p.description) html += '<p class="project-desc">' + p.description + '</p>';
      if (p.techs && p.techs.length) {
        html += '<div class="project-tech">';
        p.techs.forEach(function(t) { html += '<span>' + t + '</span>'; });
        html += '</div>';
      }
      if (p.metrics && p.metrics.length) {
        html += '<div class="project-metrics">';
        p.metrics.forEach(function(m) { html += '<div class="metric"><span class="metric-val">' + m.value + '</span><span>' + m.label + '</span></div>'; });
        html += '</div>';
      }
      card.innerHTML = html;
      projContainer.appendChild(card);
    });
  }

  var awardsNat = document.getElementById("awards-nat");
  if (awardsNat) {
    (D.awards_nat || []).forEach(function(a) {
      var li = document.createElement("li");
      li.innerHTML = '<span class="award-year">' + a.date + '</span><span class="award-name">' + a.name + '</span><span class="award-grade grade-national">' + (a.grade || "") + '</span>';
      awardsNat.appendChild(li);
    });
  }
  var awardsProv = document.getElementById("awards-prov");
  if (awardsProv) {
    (D.awards_prov || []).forEach(function(a) {
      var li = document.createElement("li");
      li.innerHTML = '<span class="award-year">' + a.date + '</span><span class="award-name">' + a.name + '</span><span class="award-grade grade-provincial">' + (a.grade || "") + '</span>';
      awardsProv.appendChild(li);
    });
  }

  var certsContainer = document.getElementById("certs-container");
  if (certsContainer) {
    (D.certs || []).forEach(function(c) {
      var card = document.createElement("div");
      card.className = "cert-card";
      card.innerHTML = '<div class="cert-icon">' + (c.icon || "📜") + '</div><h4>' + c.name + '</h4><p>' + (c.description || "") + '</p>';
      certsContainer.appendChild(card);
    });
  }

  var ctfContainer = document.getElementById("ctf-container");
  if (ctfContainer) {
    (D.ctfs || []).forEach(function(c) {
      var div = document.createElement("div");
      div.className = "ctf-item";
      div.innerHTML = '<span class="ctf-date">' + c.date + '</span><span>' + (c.description || "") + '</span>';
      ctfContainer.appendChild(div);
    });
  }

  var contactCards = document.getElementById("contact-cards");
  if (contactCards) {
    if (info.email) contactCards.innerHTML += '<a href="mailto:' + info.email + '" class="contact-card"><div class="contact-icon">📧</div><h4>电子邮箱</h4><p>' + info.email + '</p></a>';
    if (info.phone) contactCards.innerHTML += '<div class="contact-card"><div class="contact-icon">📱</div><h4>电话</h4><p>' + info.phone + '</p></div>';
    if (info.wechat) contactCards.innerHTML += '<div class="contact-card"><div class="contact-icon">💬</div><h4>微信</h4><p>' + info.wechat + '</p></div>';
    if (info.github) contactCards.innerHTML += '<a href="' + info.github + '" target="_blank" class="contact-card"><div class="contact-icon">🐙</div><h4>GitHub</h4><p>github.com/huoqi1004</p></a>';
  }

  var carousel = document.getElementById("honorCarousel");
  var indicatorsEl = document.getElementById("carouselIndicators");
  if (carousel && indicatorsEl) {
    var honorImages = D.honor_images || [];
    var PER_SLIDE = 7;
    var slides = [];
    for (var i = 0; i < honorImages.length; i += PER_SLIDE) {
      slides.push(honorImages.slice(i, i + PER_SLIDE));
    }
    if (slides.length === 0) slides.push([]);
    slides.forEach(function(group, idx) {
      var slide = document.createElement("div");
      slide.className = "carousel-slide";
      group.forEach(function(img) {
        var card = document.createElement("div");
        card.className = "carousel-card";
        card.innerHTML = '<img src="images/' + img.filename + '" alt="' + img.name + '" class="carousel-image"><div class="carousel-overlay"><span class="carousel-name">' + img.name + '</span></div>';
        slide.appendChild(card);
      });
      if (group.length === 0) {
        slide.innerHTML = '<div class="empty-state"><p>暂无荣誉图片</p></div>';
      }
      carousel.appendChild(slide);
      var dot = document.createElement("button");
      dot.className = "indicator" + (idx === 0 ? " active" : "");
      dot.dataset.index = idx;
      dot.addEventListener("click", function() { goToSlide(idx); });
      indicatorsEl.appendChild(dot);
    });
    var currentSlide = 0;
    function goToSlide(index) {
      if (!carousel) return;
      var total = slides.length;
      if (index < 0) index = total - 1;
      if (index >= total) index = 0;
      currentSlide = index;
      carousel.style.transform = 'translateX(-' + (index * 100) + '%)';
      document.querySelectorAll(".carousel-indicators .indicator").forEach(function(d, i) {
        d.classList.toggle("active", i === currentSlide);
      });
    }
    var prevBtn = document.getElementById("prevBtn");
    var nextBtn = document.getElementById("nextBtn");
    if (nextBtn) nextBtn.addEventListener("click", function() { goToSlide(currentSlide + 1); });
    if (prevBtn) prevBtn.addEventListener("click", function() { goToSlide(currentSlide - 1); });
    setInterval(function() { goToSlide(currentSlide + 1); }, 5000);
  }

  if (document.getElementById("stat-projects")) document.getElementById("stat-projects").textContent = (D.projects || []).length + "+";
  if (document.getElementById("stat-certs")) document.getElementById("stat-certs").textContent = (D.certs || []).length;

  var typingEl = document.querySelector(".typing-text");
  if (typingEl) {
    var titles = (info.hero_typing_titles || "网络空间安全探索者,AI安全大模型开发者,CTF竞赛选手,智能安全防御架构师").split(",");
    var titleIdx = 0, charIdx = 0, isDeleting = false;
    function typeLoop() {
      var current = titles[titleIdx];
      if (isDeleting) {
        typingEl.textContent = current.substring(0, charIdx - 1);
        charIdx--;
      } else {
        typingEl.textContent = current.substring(0, charIdx + 1);
        charIdx++;
      }
      var speed = isDeleting ? 40 : 100;
      if (!isDeleting && charIdx === current.length) {
        speed = 2000; isDeleting = true;
      } else if (isDeleting && charIdx === 0) {
        isDeleting = false; titleIdx = (titleIdx + 1) % titles.length; speed = 300;
      }
      setTimeout(typeLoop, speed);
    }
    typeLoop();
  }

  window.addEventListener("scroll", function() {
    var navbar = document.querySelector(".navbar");
    if (navbar) navbar.classList.toggle("scrolled", window.scrollY > 50);
  });
})();
'''
with open(os.path.join(OUT, "static", "render.js"), "w", encoding="utf-8") as f:
    f.write(render_js)

# Generate index.html
index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>陶兴旺 | 网络安全 · AI安全</title>
  <link rel="stylesheet" href="static/css/style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap">
</head>
<body>
  <canvas id="particle-canvas"></canvas>
  <nav class="navbar">
    <div class="nav-container">
      <a href="index.html" class="nav-logo">TXW<span class="accent">.sec</span></a>
      <ul class="nav-links">
        <li><a href="#about">关于</a></li>
        <li><a href="#projects">项目</a></li>
        <li><a href="honors.html">荣誉墙</a></li>
        <li><a href="timeline.html">时间线</a></li>
        <li><a href="#contact">联系</a></li>
      </ul>
    </div>
  </nav>

  <section id="hero" class="hero">
    <div class="hero-content">
      <div class="hero-badge"><span class="badge-dot"></span> AVAILABLE FOR OPPORTUNITIES</div>
      <h1 class="hero-name">
        <span class="greeting">Hi, I'm</span>
        <span class="name" id="hero-name">陶兴旺</span>
      </h1>
      <div class="hero-title"><span class="typing-text"></span><span class="cursor">|</span></div>
      <p class="hero-desc" id="hero-desc"></p>
      <div class="hero-actions">
        <a href="#projects" class="btn btn-primary">探索项目</a>
        <a href="#contact" class="btn btn-outline">联系我</a>
      </div>
      <div class="hero-stats">
        <div class="stat"><span class="stat-num" id="stat-projects">0+</span><span class="stat-label">核心项目</span></div>
        <div class="stat"><span class="stat-num">15+</span><span class="stat-label">竞赛奖项</span></div>
        <div class="stat"><span class="stat-num" id="stat-certs">0</span><span class="stat-label">专业认证</span></div>
        <div class="stat"><span class="stat-num">TOP3%</span><span class="stat-label">专业排名</span></div>
      </div>
    </div>
  </section>

  <section id="about" class="about section">
    <div class="container">
      <h2 class="section-title"><span class="num">01.</span> 关于我</h2>
      <div class="about-grid">
        <div class="about-text">
          <p id="about-p1"></p>
          <p id="about-p2"></p>
          <p id="about-p3"></p>
        </div>
        <div class="about-edu" id="edu-container"></div>
      </div>
    </div>
  </section>

  <section id="skills" class="skills section">
    <div class="container">
      <h2 class="section-title"><span class="num">02.</span> 技术能力</h2>
      <div class="skills-grid" id="skills-container"></div>
    </div>
  </section>

  <section id="projects" class="projects section">
    <div class="container">
      <h2 class="section-title"><span class="num">03.</span> 核心项目</h2>
      <div id="projects-container"></div>
    </div>
  </section>

  <section id="honor-wall-carousel" class="honor-wall-carousel section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title"><span class="num">🏆</span> 荣誉墙</h2>
        <a href="honors.html" class="view-all-link">查看全部 →</a>
      </div>
      <div class="carousel-container">
        <div class="carousel-track" id="honorCarousel"></div>
        <button class="carousel-btn carousel-prev" id="prevBtn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 19l-7-7 7-7"/></svg>
        </button>
        <button class="carousel-btn carousel-next" id="nextBtn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5l7 7-7 7"/></svg>
        </button>
        <div class="carousel-indicators" id="carouselIndicators"></div>
      </div>
    </div>
  </section>

  <section id="awards" class="awards section">
    <div class="container">
      <h2 class="section-title"><span class="num">04.</span> 荣誉 & 认证</h2>
      <div class="awards-grid">
        <div class="award-level">
          <h3 class="award-level-title">🏅 国家级奖项</h3>
          <ul class="award-list" id="awards-nat"></ul>
        </div>
        <div class="award-level">
          <h3 class="award-level-title">🏆 省部级奖项</h3>
          <ul class="award-list" id="awards-prov"></ul>
        </div>
      </div>
      <div class="certs-section">
        <h3 class="award-level-title">📜 专业认证</h3>
        <div class="certs-grid" id="certs-container"></div>
      </div>
      <div class="ctf-section">
        <h3 class="award-level-title">⚔️ CTF & 安全竞赛</h3>
        <div class="ctf-timeline" id="ctf-container"></div>
      </div>
    </div>
  </section>

  <section id="contact" class="contact section">
    <div class="container">
      <h2 class="section-title"><span class="num">05.</span> 联系我</h2>
      <div class="contact-content">
        <p class="contact-intro">如果你对我的项目感兴趣，或者想交流网络安全与AI相关技术，欢迎随时联系我。</p>
        <div class="contact-cards" id="contact-cards"></div>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="container">
      <p>&copy; 2026 陶兴旺 · 网络安全与AI安全探索者</p>
    </div>
  </footer>

  <script src="static/js/particles.js"></script>
  <script src="static/data.js"></script>
  <script src="static/js/main.js"></script>
  <script src="static/render.js"></script>
</body>
</html>
'''
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# Generate honors.html
honors_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>荣誉墙 | 陶兴旺</title>
  <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
  <canvas id="particle-canvas"></canvas>
  <nav class="navbar">
    <div class="nav-container">
      <a href="index.html" class="nav-logo">TXW<span class="accent">.sec</span></a>
      <ul class="nav-links">
        <li><a href="index.html#about">关于</a></li>
        <li><a href="index.html#projects">项目</a></li>
        <li><a href="honors.html" class="active">荣誉墙</a></li>
        <li><a href="timeline.html">时间线</a></li>
        <li><a href="index.html#contact">联系</a></li>
      </ul>
    </div>
  </nav>
  <section id="honors-wall" class="honors-wall section">
    <div class="container">
      <h2 class="section-title"><span class="num"></span> 荣誉墙</h2>
      <p class="section-subtitle">记录每一个奋斗的足迹，见证每一份来之不易的荣誉</p>
      <div class="honors-filter">
        <button class="filter-btn active" data-filter="all">全部</button>
        <button class="filter-btn" data-filter="national">国家级</button>
        <button class="filter-btn" data-filter="provincial">省部级</button>
        <button class="filter-btn" data-filter="other">其他</button>
      </div>
      <div class="honors-grid" id="honors-grid"></div>
    </div>
  </section>
  <footer class="footer">
    <div class="container">
      <p>&copy; 2026 陶兴旺 · 网络安全与AI安全探索者</p>
    </div>
  </footer>
  <script src="static/js/particles.js"></script>
  <script src="static/data.js"></script>
  <script>
  (function(){
    var images = SITE_DATA.honor_images || [];
    var grid = document.getElementById("honors-grid");
    images.forEach(function(img){
      var levelText = img.level === "national" ? "国家级" : img.level === "provincial" ? "省部级" : "其他";
      var card = document.createElement("div");
      card.className = "honor-card";
      card.dataset.level = img.level;
      card.innerHTML = '<div class="honor-image-wrapper"><img src="images/' + img.filename + '" alt="' + img.name + '" class="honor-image"><div class="honor-overlay"><span class="honor-name">' + img.name + '</span><span class="honor-level">' + levelText + '</span></div></div>';
      grid.appendChild(card);
    });
    document.querySelectorAll(".filter-btn").forEach(function(btn){
      btn.addEventListener("click", function(){
        document.querySelectorAll(".filter-btn").forEach(function(b){ b.classList.remove("active"); });
        this.classList.add("active");
        var filter = this.dataset.filter;
        document.querySelectorAll(".honor-card").forEach(function(card){
          card.style.display = (filter === "all" || card.dataset.level === filter) ? "block" : "none";
        });
      });
    });
  })();
  </script>
</body>
</html>
'''
with open(os.path.join(OUT, "honors.html"), "w", encoding="utf-8") as f:
    f.write(honors_html)

# Generate timeline.html
timeline_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>时间线 | 陶兴旺</title>
  <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
  <canvas id="particle-canvas"></canvas>
  <nav class="navbar">
    <div class="nav-container">
      <a href="index.html" class="nav-logo">TXW<span class="accent">.sec</span></a>
      <ul class="nav-links">
        <li><a href="index.html#about">关于</a></li>
        <li><a href="index.html#projects">项目</a></li>
        <li><a href="honors.html">荣誉墙</a></li>
        <li><a href="timeline.html" class="active">时间线</a></li>
        <li><a href="index.html#contact">联系</a></li>
      </ul>
    </div>
  </nav>
  <section class="section">
    <div class="container">
      <h2 class="section-title"><span class="num">📅</span> 时间线</h2>
      <div id="timeline-content"></div>
    </div>
  </section>
  <footer class="footer">
    <div class="container">
      <p>&copy; 2026 陶兴旺 · 网络安全与AI安全探索者</p>
    </div>
  </footer>
  <script src="static/js/particles.js"></script>
  <script src="static/data.js"></script>
  <script>
  (function(){
    var items = [];
    (SITE_DATA.awards_nat || []).forEach(function(a){ items.push({date:a.date, type:"国家级奖项", text:a.name, grade:a.grade}); });
    (SITE_DATA.awards_prov || []).forEach(function(a){ items.push({date:a.date, type:"省部级奖项", text:a.name, grade:a.grade}); });
    (SITE_DATA.awards_other || []).forEach(function(a){ items.push({date:a.date, type:"其他奖项", text:a.name, grade:a.grade}); });
    (SITE_DATA.ctfs || []).forEach(function(c){ items.push({date:c.date, type:"CTF", text:c.description}); });
    items.sort(function(a,b){ return (b.date||"").localeCompare(a.date||""); });
    var container = document.getElementById("timeline-content");
    items.forEach(function(item){
      var div = document.createElement("div");
      div.className = "ctf-item";
      div.innerHTML = '<span class="ctf-date">' + item.date + '</span> <strong>[' + item.type + ']</strong> ' + item.text + (item.grade ? ' · ' + item.grade : '');
      container.appendChild(div);
    });
  })();
  </script>
</body>
</html>
'''
with open(os.path.join(OUT, "timeline.html"), "w", encoding="utf-8") as f:
    f.write(timeline_html)

# .nojekyll
with open(os.path.join(OUT, ".nojekyll"), "w") as f:
    f.write("")

print("Build complete!")
print("Files in docs:", os.listdir(OUT))
print("JS files:", os.listdir(os.path.join(OUT, "static")))
