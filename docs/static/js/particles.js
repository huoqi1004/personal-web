// Particle background animation
(function(){
  const canvas=document.getElementById("particle-canvas");
  const ctx=canvas.getContext("2d");
  let particles=[],w,h;
  function resize(){
    w=canvas.width=window.innerWidth;
    h=canvas.height=window.innerHeight;
  }
  class Particle{
    constructor(){
      this.reset();
      this.y=Math.random()*h;
    }
    reset(){
      this.x=Math.random()*w;this.y=-10;
      this.size=Math.random()*2+0.5;
      this.speed=Math.random()*0.5+0.2;
      this.opacity=Math.random()*0.5+0.1;
    }
    update(){
      this.y+=this.speed;
      if(this.y>h+10)this.reset();
    }
    draw(){
      ctx.beginPath();
      ctx.arc(this.x,this.y,this.size,0,Math.PI*2);
      ctx.fillStyle="rgba(0,238,255,"+this.opacity+")";
      ctx.fill();
    }
  }
  function init(){
    resize();
    particles=Array.from({length:80},()=>new Particle());
  }
  function animate(){
    ctx.clearRect(0,0,w,h);
    particles.forEach(p=>{p.update();p.draw();});
    // Draw connections
    for(let i=0;i<particles.length;i++){
      for(let j=i+1;j<particles.length;j++){
        const dx=particles[i].x-particles[j].x;
        const dy=particles[i].y-particles[j].y;
        const dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<120){
          ctx.beginPath();
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.strokeStyle="rgba(0,238,255,"+(0.08*(1-dist/120))+")";
          ctx.lineWidth=0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(animate);
  }
  window.addEventListener("resize",resize);
  init();animate();
})();
