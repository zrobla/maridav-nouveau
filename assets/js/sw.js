self.addEventListener('install', (e)=>{
  e.waitUntil(caches.open('maridav-ci-v1').then(c=>c.addAll(['/','/index.html'])));
});
self.addEventListener('fetch', (e)=>{
  e.respondWith(
    caches.match(e.request).then(res=>res||fetch(e.request).then(r=>{
      const copy=r.clone(); caches.open('maridav-ci-v1').then(c=>c.put(e.request,copy)); return r;
    }).catch(()=>res))
  );
});

