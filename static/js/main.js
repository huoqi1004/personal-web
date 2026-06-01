// Main JavaScript – typing effect, mobile nav, scroll animations
(function(){
  // === TYPING EFFECT ===
  const titles=["网络空间安全探索者","AI安全大模型开发者","CTF竞赛选手","智能安全防御架构师"];
  const typingEl=document.querySelector(".typing-text");
  let titleIdx=0,charIdx=0,isDeleting=false;
  function typeLoop(){
    const current=titles[titleIdx];
    if(isDeleting){
      typingEl.textContent=current.substring(0,charIdx-1);
      charIdx--;
    }else{
      typingEl.textContent=current.substring(0,charIdx+1);
      charIdx++;
    }
    let speed=isDeleting?40:100;
    if(!isDeleting&&charIdx===current.length){
      speed=2000;isDeleting=true;
    }else if(isDeleting&&charIdx===0){
      isDeleting=false;titleIdx=(titleIdx+1)%titles.length;speed=300;
    }
    setTimeout(typeLoop,speed);
  }
  if(typingEl)typeLoop();

  // === MOBILE NAV TOGGLE ===
  const toggle=document.querySelector(".mobile-toggle");
  const navLinks=document.querySelector(".nav-links");
  if(toggle){
    toggle.addEventListener("click",()=>{
      navLinks.classList.toggle("open");
      const spans=toggle.querySelectorAll("span");
      if(navLinks.classList.contains("open")){
        spans[0].style.transform="rotate(45deg) translate(5px,5px)";
        spans[1].style.opacity="0";
        spans[2].style.transform="rotate(-45deg) translate(5px,-5px)";
      }else{
        spans[0].style.transform="";spans[1].style.opacity="";spans[2].style.transform="";
      }
    });
  }

  // === NAVBAR SCROLL EFFECT ===
  const navbar=document.querySelector(".navbar");
  window.addEventListener("scroll",()=>{
    navbar.classList.toggle("scrolled",window.scrollY>50);
    // Active nav link
    const sections=document.querySelectorAll("section[id]");
    let current="";
    sections.forEach(s=>{
      if(window.scrollY>=s.offsetTop-100)current=s.getAttribute("id");
    });
    document.querySelectorAll(".nav-links a").forEach(a=>{
      a.classList.toggle("active",a.getAttribute("href")==="#"+current);
    });
  });

  // Close mobile nav on link click
  document.querySelectorAll(".nav-links a").forEach(a=>{
    a.addEventListener("click",()=>navLinks.classList.remove("open"));
  });

  // === SCROLL REVEAL ANIMATION ===
  const observer=new IntersectionObserver((entries)=>{
    entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add("reveal");});
  },{threshold:0.15});
  document.querySelectorAll(".project-card,.edu-card,.skill-category,.cert-card,.award-list li,.ctf-item,.contact-card").forEach(el=>observer.observe(el));

  // === COUNTER ANIMATION (hero stats on load) ===
  document.querySelectorAll(".stat-num").forEach(el=>{
    el.style.opacity="0";el.style.transform="translateY(10px)";
    setTimeout(()=>{el.style.transition="all 0.6s ease";el.style.opacity="1";el.style.transform="translateY(0)";},200);
  });
})();
