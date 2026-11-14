// Progressive enhancement for the {% include openscad.html %} embed.
//
// The include renders a poster + "View 3D" button. Clicking it loads the model
// surface in an iframe (deferring the heavier 3D view until the reader asks for
// it). When a live surface is configured (data-live-src), a "Customize" control
// then upgrades to the live in-browser customizer.
//
// One delegated listener handles every embed on the page; harmless on pages
// with none.
(function () {
  function makeFrame(container, src) {
    var frame = document.createElement('iframe');
    frame.className = 'openscad-embed__frame';
    frame.src = src;
    frame.title = 'OpenSCAD model: ' + (container.dataset.title || '');
    frame.setAttribute('width', '100%');
    frame.setAttribute('height', container.dataset.height || '480');
    frame.loading = 'lazy';
    frame.setAttribute('allow', 'fullscreen');
    frame.referrerPolicy = 'no-referrer';
    return frame;
  }

  function load(container, src, offerUpgrade) {
    container.replaceChildren(makeFrame(container, src));

    if (offerUpgrade && container.dataset.liveSrc) {
      var bar = document.createElement('div');
      bar.className = 'openscad-embed__bar';

      var upgrade = document.createElement('button');
      upgrade.type = 'button';
      upgrade.className = 'openscad-embed__upgrade';
      upgrade.textContent = 'Customize (live) →';
      upgrade.addEventListener('click', function () {
        load(container, container.dataset.liveSrc, false);
      });

      bar.appendChild(upgrade);
      container.appendChild(bar);
    }
  }

  document.addEventListener('click', function (event) {
    var target = event.target;
    var poster = target.closest ? target.closest('.openscad-embed__poster') : null;
    if (!poster) return;
    var container = poster.closest('[data-openscad-embed]');
    if (!container || !container.dataset.src) return;
    load(container, container.dataset.src, true);
  });
})();
