// 知日塾官网：菜单开关 + 进场浮现。?shot 参数=截图模式（全部直接显示）
(function(){
  var SHOT=location.search.indexOf('shot')>-1;if(SHOT)document.documentElement.classList.add('shot');
  document.querySelectorAll('.mbtn').forEach(function(b){b.addEventListener('click',function(){var o=document.body.classList.toggle('menu');b.setAttribute('aria-expanded',o);b.setAttribute('aria-label',o?'关闭菜单':'打开菜单')})});
  document.querySelectorAll('.ov a').forEach(function(a){a.addEventListener('click',function(){document.body.classList.remove('menu')})});
  addEventListener('keydown',function(e){if(e.key==='Escape')document.body.classList.remove('menu')});
  var els=document.querySelectorAll('.rv');
  if(SHOT||!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('in')});return}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
  els.forEach(function(el){io.observe(el)});
})();
// 首屏の写真切替：2枚目以降はページ読み込み後に取得（最初の表示を速くする）
addEventListener('load',function(){document.querySelectorAll('img[data-src]').forEach(function(i){if(i.dataset.srcset)i.srcset=i.dataset.srcset;i.src=i.dataset.src})});
