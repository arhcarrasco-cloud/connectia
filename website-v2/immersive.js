
// ========== IMMERSIVE COSMOS SCROLL ==========
// Hijack scroll on hero block 1 to create a warp-into-logo effect
(function(){
  var hero1 = document.querySelector('.hero__block--1');
  var hero2 = document.querySelector('.hero__block--2');
  var canvas = document.getElementById('cosmosHero');
  if(!hero1 || !canvas) return;

  // Create overlay for warp effect
  var warpCanvas = document.createElement('canvas');
  warpCanvas.id = 'warpCanvas';
  warpCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9998;pointer-events:none;opacity:0;transition:opacity 0.3s';
  document.body.appendChild(warpCanvas);

  var ctx = warpCanvas.getContext('2d');
  var stars = [];
  var NUM_STARS = 400;
  var warpActive = false;
  var warpProgress = 0; // 0 to 1
  var scrollLocked = false;
  var totalScrollDistance = window.innerHeight * 2.5; // scroll distance for full animation
  var startScrollY = 0;

  // Initialize warp stars
  function initStars(){
    warpCanvas.width = window.innerWidth;
    warpCanvas.height = window.innerHeight;
    stars = [];
    for(var i=0;i<NUM_STARS;i++){
      stars.push({
        x: (Math.random()-0.5)*2, // -1 to 1 from center
        y: (Math.random()-0.5)*2,
        z: Math.random()*3+0.5,
        size: Math.random()*2+0.5,
        speed: Math.random()*0.02+0.005
      });
    }
  }
  initStars();
  window.addEventListener('resize', initStars);

  // Render warp frame
  function renderWarp(progress){
    var w = warpCanvas.width, h = warpCanvas.height;
    var cx = w/2, cy = h/2;
    ctx.clearRect(0,0,w,h);

    // Background: fade from transparent to deep space blue to black
    if(progress > 0.1){
      var alpha = Math.min((progress-0.1)/0.3, 1) * 0.95;
      ctx.fillStyle = 'rgba(5,5,15,'+alpha+')';
      ctx.fillRect(0,0,w,h);
    }

    // Warp speed factor: accelerates in middle, decelerates at end
    var speedFactor = progress < 0.3 ? progress/0.3 :
                      progress < 0.7 ? 1 :
                      1 - (progress-0.7)/0.3;
    speedFactor = Math.max(0, Math.min(1, speedFactor));

    // Draw streaking stars
    stars.forEach(function(s){
      // Move stars toward viewer (z decreases)
      s.z -= s.speed * speedFactor * 8;
      if(s.z <= 0.1){ s.z = 3; s.x = (Math.random()-0.5)*2; s.y = (Math.random()-0.5)*2; }

      var sx = cx + (s.x/s.z) * w * 0.5;
      var sy = cy + (s.y/s.z) * h * 0.5;

      // Trail length based on speed
      var trail = speedFactor * 40 / s.z;
      var prevSx = cx + (s.x/(s.z + s.speed*speedFactor*8)) * w * 0.5;
      var prevSy = cy + (s.y/(s.z + s.speed*speedFactor*8)) * h * 0.5;

      // Star brightness: brighter when closer
      var brightness = Math.min(1, 2/s.z) * (progress > 0.8 ? 1-(progress-0.8)/0.2 : 1);

      if(sx > -50 && sx < w+50 && sy > -50 && sy < h+50){
        ctx.beginPath();
        ctx.moveTo(prevSx, prevSy);
        ctx.lineTo(sx, sy);
        ctx.strokeStyle = 'rgba(255,255,255,'+brightness+')';
        ctx.lineWidth = s.size * (1/s.z) * (1 + speedFactor*2);
        ctx.stroke();

        // Glow dot at head
        ctx.beginPath();
        ctx.arc(sx, sy, s.size*(1/s.z)*(1+speedFactor), 0, Math.PI*2);
        ctx.fillStyle = 'rgba(200,220,255,'+brightness*0.8+')';
        ctx.fill();
      }
    });

    // Central glow: the "logo" getting brighter as you approach
    if(progress > 0.2 && progress < 0.85){
      var glowAlpha = (progress-0.2)/0.5 * 0.15;
      var glowRadius = w * 0.2 * (1 + progress*2);
      var gradient = ctx.createRadialGradient(cx,cy,0,cx,cy,glowRadius);
      gradient.addColorStop(0, 'rgba(150,120,255,'+glowAlpha+')');
      gradient.addColorStop(0.5, 'rgba(100,80,200,'+glowAlpha*0.3+')');
      gradient.addColorStop(1, 'rgba(50,30,100,0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0,0,w,h);
    }

    // Final fade to black
    if(progress > 0.85){
      var fadeAlpha = (progress-0.85)/0.15;
      ctx.fillStyle = 'rgba(0,0,0,'+fadeAlpha+')';
      ctx.fillRect(0,0,w,h);
    }
  }

  // Scroll handler
  var sectionTop = 0;
  function updateSectionTop(){ sectionTop = hero1.getBoundingClientRect().top + window.scrollY; }
  updateSectionTop();

  var animFrame;
  function onScroll(){
    var scrollY = window.scrollY;
    var heroBottom = sectionTop + hero1.offsetHeight;

    // Activate warp when scrolling past 80% of hero1
    if(scrollY > sectionTop + hero1.offsetHeight*0.5 && scrollY < heroBottom + totalScrollDistance){
      if(!warpActive){
        warpActive = true;
        warpCanvas.style.opacity = '1';
        startScrollY = sectionTop + hero1.offsetHeight*0.5;
      }
      warpProgress = Math.min(1, Math.max(0, (scrollY - startScrollY) / totalScrollDistance));
      renderWarp(warpProgress);

      // When complete, hide warp and let normal scrolling continue
      if(warpProgress >= 1){
        warpCanvas.style.opacity = '0';
        warpActive = false;
      }
    } else if(scrollY <= sectionTop + hero1.offsetHeight*0.5){
      warpCanvas.style.opacity = '0';
      warpActive = false;
      warpProgress = 0;
    }
  }

  window.addEventListener('scroll', onScroll, {passive:true});

  // Make hero1 taller to accommodate scroll animation
  hero1.style.marginBottom = totalScrollDistance + 'px';
})();
