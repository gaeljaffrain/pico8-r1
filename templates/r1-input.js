// Maps R1 touch + hardware events onto PICO-8's pico8_buttons[0] bitfield.
// bits: 1 left, 2 right, 4 up, 8 down, 16 O, 32 X, 64 menu
(function(){
  var LEFT=1,RIGHT=2,UP=4,DOWN=8,O=16,X=32,MENU=64;
  var cfg=window.R1_CONFIG||{};
  var wheelUp=cfg.invertWheel?DOWN:UP, wheelDown=cfg.invertWheel?UP:DOWN;
  var PULSE_MS=100;

  var held={};      // pointerId -> mask
  var pulses=0;     // bits held by timed pulses (wheel, side button)
  var menuHeld=0;   // long press -> pause menu

  function apply(){
    var m=pulses|menuHeld; for(var k in held)m|=held[k];
    pico8_buttons[0]=m;
  }
  function pulse(bit){
    pulses|=bit; apply();
    setTimeout(function(){pulses&=~bit;apply();},PULSE_MS);
  }

  // R1 hardware events. The wheel's physical-up fires 'scrollDown' and vice versa.
  window.addEventListener('scrollDown',function(){pulse(wheelUp);});
  window.addEventListener('scrollUp',function(){pulse(wheelDown);});
  window.addEventListener('sideClick',function(){pulse(O);});
  window.addEventListener('longPressStart',function(){menuHeld=MENU;apply();});
  window.addEventListener('longPressEnd',function(){menuHeld=0;apply();});

  // d-pad: one round region, direction from finger position (allows diagonals and sliding)
  var pad=document.getElementById('pad'),dot=pad.querySelector('i');
  function padMask(e){
    var r=pad.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;
    var dx=(e.clientX-cx)/(r.width/2),dy=(e.clientY-cy)/(r.height/2),t=0.3,m=0;
    if(dx<-t)m|=LEFT; else if(dx>t)m|=RIGHT;
    if(dy<-t)m|=UP; else if(dy>t)m|=DOWN;
    var c=Math.max(-1,Math.min(1,dx)),d=Math.max(-1,Math.min(1,dy));
    var h=r.width/2; dot.style.left=(h-6+c*(h-12))+'px'; dot.style.top=(h-6+d*(h-12))+'px';
    return m;
  }
  function padEnd(e){delete held[e.pointerId];var h=pad.offsetWidth/2-6; dot.style.left=dot.style.top=h+'px';apply();}
  pad.addEventListener('pointerdown',function(e){e.preventDefault();pad.setPointerCapture(e.pointerId);held[e.pointerId]=padMask(e);apply();});
  pad.addEventListener('pointermove',function(e){if(e.pointerId in held){held[e.pointerId]=padMask(e);apply();}});
  pad.addEventListener('pointerup',padEnd);
  pad.addEventListener('pointercancel',padEnd);

  // action buttons
  [].forEach.call(document.querySelectorAll('.btn'),function(el){
    var b=+el.dataset.b;
    function end(e){delete held[e.pointerId];el.classList.remove('on');apply();}
    el.addEventListener('pointerdown',function(e){e.preventDefault();el.setPointerCapture(e.pointerId);held[e.pointerId]=b;el.classList.add('on');apply();});
    el.addEventListener('pointerup',end);
    el.addEventListener('pointercancel',end);
  });

  // pointer events only: swallow the duplicate touch events so nothing scrolls or double-fires
  ['touchstart','touchmove'].forEach(function(n){
    document.addEventListener(n,function(e){e.preventDefault();},{passive:false});
  });
})();

// layout + optional fps meter, driven by window.R1_CONFIG
(function(){
  var cfg=window.R1_CONFIG||{};
  if(cfg.layout==='overlay')document.body.classList.add('overlay');
  if(!cfg.fps)return;
  var el=document.getElementById('fps'),last=0,lastT=performance.now();
  el.style.display='block';
  setInterval(function(){
    var f=(typeof pico8_state!=='undefined'&&pico8_state.frame_number)||0,t=performance.now();
    var fps=last&&f>=last?Math.round((f-last)*1000/(t-lastT)):0;
    el.textContent=fps+' fps\n'+innerWidth+'x'+innerHeight;
    last=f;lastT=t;
  },1000);
})();
