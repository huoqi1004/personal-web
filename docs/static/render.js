(function(){
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
