/* Annuaire Bamako — application statique, aucune étape de build. */
(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const els = {
    q: $('#q'), qClear: $('#q-clear'), chips: $('#chips-cat'), commune: $('#f-commune'), sort: $('#f-sort'),
    reset: $('#btn-reset'), grid: $('#grid'), count: $('#count'), empty: $('#empty'), emptyReset: $('#empty-reset'),
    urg: $('#urgences-list'), btnCarte: $('#btn-carte'), mapPanel: $('#map-panel'), stats: $('#stats'),
    tpl: $('#tpl-row'), suggest: [$('#empty-suggest'), $('#about-suggest')],
  };

  const state = { q: '', cat: '', commune: '', sort: 'name', map: false };
  let DATA = { entries: [], categories: {}, urgences: [], meta: {} };
  let map = null, layer = null;

  // --- utilitaires -------------------------------------------------------
  const fold = (s) => (s || '').toString().normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  // Index de recherche : accents retirés, ponctuation remplacée par des espaces, bordé d'espaces
  // pour pouvoir ancrer les termes sur un début de mot.
  const hayOf = (s) => ` ${fold(s).replace(/[^a-z0-9]+/g, ' ').trim()} `;

  // Un terme colle au début d'un mot, jamais au milieu : sinon « commune v » sortait 287 fiches,
  // le « v » se trouvant dans ville, vaccin, Travélé… Les suites de chiffres restent cherchées
  // en sous-chaîne pour retrouver un numéro tapé par tranches (« 20 23 07 80 »).
  const hit = (hay, t) => {
    if (/^\d+$/.test(t)) return hay.includes(t);
    if (t.length <= 2) return hay.includes(` ${t} `);
    return hay.includes(` ${t}`);
  };
  const digits = (s) => (s || '').replace(/\D/g, '');
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // Numérotation malienne : 8 chiffres ; les mobiles commencent par 5, 6, 7 ou 9.
  // Les numéros courts (3 à 5 chiffres) ne sont joignables que depuis le Mali.
  function phoneInfo(raw) {
    const d = digits(raw);
    const national = d.startsWith('223') && d.length === 11 ? d.slice(3) : d;
    const isShort = national.length <= 5;
    const isMobile = national.length === 8 && /^[5679]/.test(national);
    return {
      tel: isShort ? national : `+223${national}`,
      display: isShort ? national : national.replace(/(\d{2})(?=\d)/g, '$1 '),
      isShort, isMobile,
      wa: isMobile ? `223${national}` : null,
    };
  }

  function mapsUrl(e) {
    if (e.lat && e.lng) return `https://www.google.com/maps/dir/?api=1&destination=${e.lat},${e.lng}`;
    const q = [e.name, e.address, e.quartier, 'Bamako, Mali'].filter(Boolean).join(', ');
    return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(q)}`;
  }

  function fmtDate(iso) {
    if (!iso) return '';
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
    return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
  }

  // Renvoie null tant qu'aucun dépôt ni e-mail de contact n'est renseigné dans meta :
  // mieux vaut masquer le bouton que proposer un lien qui ne mène nulle part.
  function suggestUrl(e) {
    const { repo, contact } = DATA.meta;
    if (!repo && !contact) return null;
    const title = e ? `Correction : ${e.name}` : 'Nouvelle structure à ajouter';
    const body = e
      ? `Fiche : ${e.name} (id ${e.id})\n\nCe qui est incorrect / à mettre à jour :\n\n`
      : 'Nom :\nCatégorie :\nAdresse :\nTéléphone(s) :\nSource (site, document) :\n';
    if (repo) return `https://github.com/${repo}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
    return `mailto:${contact}?subject=${encodeURIComponent('[Danaya] ' + title)}&body=${encodeURIComponent(body)}`;
  }

  // --- URL <-> état -------------------------------------------------------
  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get('q') || '';
    state.cat = p.get('cat') || '';
    state.commune = p.get('commune') || '';
    state.sort = p.get('tri') || 'name';
    state.map = p.get('carte') === '1';
  }
  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set('q', state.q);
    if (state.cat) p.set('cat', state.cat);
    if (state.commune) p.set('commune', state.commune);
    if (state.sort !== 'name') p.set('tri', state.sort);
    if (state.map) p.set('carte', '1');
    const qs = p.toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
  }

  // --- proximité ---------------------------------------------------------
  // Pensé pour qui ne connaît pas la ville — un Malien de l'extérieur rentré au pays,
  // un nouvel arrivant : la question n'est pas « comment ça s'appelle » mais « c'est où ».
  let maPosition = null;

  const distanceKm = (a, b) => {
    const R = 6371, rad = (d) => d * Math.PI / 180;
    const dLat = rad(b.lat - a.lat), dLon = rad(b.lng - a.lng);
    const x = Math.sin(dLat / 2) ** 2
      + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(x));
  };

  const formatDistance = (km) => (km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(1).replace('.', ',')} km`);

  function demanderPosition() {
    if (!navigator.geolocation) {
      els.count.textContent = 'Votre appareil ne sait pas donner sa position.';
      return Promise.resolve(null);
    }
    els.count.textContent = 'Recherche de votre position…';
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (p) => { maPosition = { lat: p.coords.latitude, lng: p.coords.longitude }; resolve(maPosition); },
        () => {
          // Refus ou échec : on le dit et on revient au tri par nom plutôt que d'afficher une liste muette.
          maPosition = null;
          state.sort = 'name';
          els.sort.value = 'name';
          render();
          els.count.textContent = 'Position indisponible — tri par nom rétabli. Autorisez la localisation pour trier par distance.';
          resolve(null);
        },
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
      );
    });
  }

  // --- filtrage ----------------------------------------------------------
  function filtered() {
    const terms = fold(state.q).trim().split(/\s+/).filter(Boolean);
    const list = DATA.entries.filter((e) => {
      if (state.cat && e.category !== state.cat) return false;
      if (state.commune && (e.commune || '') !== state.commune) return false;
      return terms.every((t) => hit(e._hay, t));
    });
    const byName = (a, b) => a.name.localeCompare(b.name, 'fr');
    if (state.sort === 'proche' && maPosition) {
      list.forEach((e) => { e._d = (e.lat && e.lng) ? distanceKm(maPosition, e) : Infinity; });
      list.sort((a, b) => a._d - b._d || byName(a, b));
      return list;
    }
    if (state.sort === 'verified') {
      list.sort((a, b) => Number(!!b.source?.verified) - Number(!!a.source?.verified) || byName(a, b));
      return list;
    }
    if (state.sort === 'cat') list.sort((a, b) => (a.category + a.name).localeCompare(b.category + b.name, 'fr'));
    else if (state.sort === 'recent') {
      const d = (e) => e.source?.verified || e.source?.date || '';
      list.sort((a, b) => d(b).localeCompare(d(a)) || byName(a, b));
    }
    else list.sort(byName);
    return list;
  }

  // --- rendu -------------------------------------------------------------
  const ICONS = {
    route: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.3-6-11a6 6 0 0 1 12 0c0 5.7-6 11-6 11Z"/><circle cx="12" cy="10" r="2.2"/></svg>',
    web: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    mail: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    share: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7M12 15V3m0 0-4 4m4-4 4 4"/></svg>',
    flag: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 21V4m0 0h11l-1.5 3L16 10H5"/></svg>',
    wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.4.1-.2 0-.3 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4 5.2 5.2 0 0 0 3.1.6 2.6 2.6 0 0 0 1.7-1.2 2.1 2.1 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/></svg>',
  };

  function renderCard(e) {
    const node = els.tpl.content.firstElementChild.cloneNode(true);
    node.id = `f-${e.id}`;
    const cat = DATA.categories[e.category];
    const badge = $('.badge', node);
    // Libellé court en vue liste : « Administrations & agences » occupait 147 px et
    // chassait la commune, alors que les puces de filtre portent déjà le nom complet.
    badge.textContent = cat?.short || cat?.label || e.category;
    badge.title = cat?.label || '';
    badge.dataset.cat = e.category;
    $('.commune', node).textContent = e.commune || '';
    $('.row-title', node).textContent = e.name;
    if (state.sort === 'proche' && Number.isFinite(e._d)) {
      const d = $('.distance', node);
      d.textContent = formatDistance(e._d);
      d.hidden = false;
    }

    // Le premier numéro est composable sans déplier : c'est la raison d'être de l'annuaire.
    const premier = (e.phones || [])[0];
    if (premier) {
      const info = phoneInfo(typeof premier === 'string' ? premier : premier.number);
      const appel = document.createElement('a');
      appel.className = 'appel';
      appel.href = `tel:${info.tel}`;
      appel.textContent = info.display;
      appel.setAttribute('aria-label', `Appeler ${e.name} au ${info.display}`);
      // Sans cela, composer un numéro déplierait aussi la fiche.
      appel.addEventListener('click', (ev) => ev.stopPropagation());
      $('.row-call', node).appendChild(appel);
    }
    // Distingue les fiches recoupées à la main de celles reprises telles quelles de l'annuaire source.
    if (e.source?.verified) {
      const v = $('.verif', node);
      v.hidden = false;
      v.title = `Coordonnées recoupées à la main le ${fmtDate(e.source.verified)}`;
      v.setAttribute('aria-label', `Fiche vérifiée le ${fmtDate(e.source.verified)}`);
      v.setAttribute('role', 'img');
    }
    // Le libellé complet revient dans le dépliage : la liste abrège pour tenir, le détail explique.
    $('.card-sub', node).textContent = [cat?.label, e.type, e.quartier].filter(Boolean).join(' · ');
    $('.card-addr', node).textContent = e.address || '';
    $('.card-hours', node).textContent = e.hours || '';

    const ul = $('.card-phones', node);
    (e.phones || []).forEach((p) => {
      const number = typeof p === 'string' ? p : p.number;
      const label = typeof p === 'object' ? p.label : '';
      const info = phoneInfo(number);
      const li = document.createElement('li');
      li.innerHTML = `<a class="tel" href="tel:${esc(info.tel)}">${esc(info.display)}${label ? ` <span class="lbl">${esc(label)}</span>` : ''}</a>`
        + (info.wa ? ` <a class="wa" href="https://wa.me/${info.wa}" target="_blank" rel="noopener" aria-label="WhatsApp ${esc(info.display)}" title="WhatsApp">${ICONS.wa}</a>` : '');
      ul.appendChild(li);
    });
    if (!e.phones?.length) ul.innerHTML = '<li class="card-sub">Téléphone non disponible</li>';
    if (e.fax) {
      const li = document.createElement('li');
      li.className = 'fax';
      li.textContent = `Fax ${phoneInfo(e.fax).display}`;
      ul.appendChild(li);
    }

    const a = (href, icon, txt, extra = '') => `<a class="act" href="${esc(href)}" ${extra}>${icon}<span>${esc(txt)}</span></a>`;
    let html = a(mapsUrl(e), ICONS.route, 'Itinéraire', 'target="_blank" rel="noopener"');
    if (e.website) html += a(e.website, ICONS.web, 'Site web', 'target="_blank" rel="noopener"');
    if (e.email) html += a(`mailto:${e.email}`, ICONS.mail, 'E-mail');
    html += `<button class="act" type="button" data-share="${esc(e.id)}">${ICONS.share}<span>Partager</span></button>`;
    const flag = suggestUrl(e);
    if (flag) html += a(flag, ICONS.flag, 'Signaler', 'target="_blank" rel="noopener"');
    $('.card-actions', node).innerHTML = html;

    const s = e.source || {};
    const src = s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name || 'source')}</a>` : esc(s.name || 'source inconnue');
    const when = s.verified ? ` · vérifié le ${fmtDate(s.verified)}` : s.date ? ` · fiche du ${fmtDate(s.date)}` : '';
    $('.card-source', node).innerHTML = `Source : ${src}${when}${s.note ? ` · ${esc(s.note)}` : ''}`;
    return node;
  }

  const LOT = 60;               // premier écran rendu tout de suite, la suite à l'approche
  let reste = [], sentinelle = null;

  function rendreLot() {
    if (!reste.length) { if (sentinelle) sentinelle.remove(); return; }
    const lot = reste.splice(0, LOT);
    const frag = document.createDocumentFragment();
    lot.forEach((e) => frag.appendChild(renderCard(e)));
    els.grid.insertBefore(frag, sentinelle);
    if (!reste.length && sentinelle) { sentinelle.remove(); sentinelle = null; }
  }

  const observateur = ('IntersectionObserver' in window)
    ? new IntersectionObserver((ents) => { if (ents.some((x) => x.isIntersecting)) rendreLot(); }, { rootMargin: '600px' })
    : null;

  function render() {
    const list = filtered();
    // Rendre les 386 fiches à chaque frappe reconstruisait ~9000 nœuds : intenable
    // sur les téléphones que vise cette application.
    reste = list.slice(LOT);
    const premiers = list.slice(0, LOT).map(renderCard);
    if (observateur) observateur.disconnect();
    sentinelle = null;
    if (reste.length) {
      sentinelle = document.createElement('div');
      sentinelle.className = 'sentinelle';
      sentinelle.setAttribute('aria-hidden', 'true');
      els.grid.replaceChildren(...premiers, sentinelle);
      if (observateur) observateur.observe(sentinelle);
      else rendreLot();
    } else {
      els.grid.replaceChildren(...premiers);
    }
    els.empty.hidden = list.length > 0;
    const n = list.length;
    els.count.textContent = n === DATA.entries.length ? `${n} structures` : `${n} résultat${n > 1 ? 's' : ''} sur ${DATA.entries.length}`;
    document.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.cat === state.cat)));
    els.qClear.hidden = !state.q;
    if (state.map) updateMarkers(list);
    writeUrl();
  }

  function renderChips() {
    const counts = {};
    DATA.entries.forEach((e) => { counts[e.category] = (counts[e.category] || 0) + 1; });
    const cats = Object.entries(DATA.categories).filter(([k]) => counts[k]);
    const chip = (k, label, n) => `<button class="chip" type="button" data-cat="${esc(k)}" aria-pressed="false">${esc(label)} <small>${n}</small></button>`;
    els.chips.innerHTML = chip('', 'Tout', DATA.entries.length) + cats.map(([k, c]) => chip(k, c.label, counts[k])).join('');
    els.chips.addEventListener('click', (ev) => {
      const b = ev.target.closest('.chip');
      if (!b) return;
      state.cat = b.dataset.cat === state.cat ? '' : b.dataset.cat;
      render();
    });
  }

  function renderCommunes() {
    const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI'];
    const order = (c) => { const m = /Commune (\w+)/.exec(c); return m ? ROMAN.indexOf(m[1]) : 10; };
    const set = [...new Set(DATA.entries.map((e) => e.commune).filter(Boolean))]
      .sort((a, b) => order(a) - order(b) || a.localeCompare(b, 'fr'));
    set.forEach((c) => { const o = document.createElement('option'); o.value = c; o.textContent = c; els.commune.appendChild(o); });
    els.commune.value = state.commune;
  }

  function renderUrgences() {
    const list = DATA.urgences || [];
    // Le libellé complet occupait 300 px : sur un écran de 375 px un seul numéro tenait,
    // et les trois autres numéros vitaux sortaient de l'écran sans aucun indice.
    const pill = (u) => {
      const info = phoneInfo(u.number);
      const titre = [u.label, u.note].filter(Boolean).join(' — ');
      const court = u.short || u.label;
      return `<a class="urg" href="tel:${esc(info.tel)}" title="${esc(titre)}" `
        + `aria-label="${esc(court)} — ${esc(info.display)}">`
        + `<b>${esc(info.display)}</b><span>${esc(court)}</span></a>`;
    };
    const vitaux = list.filter((u) => u.primary);
    const autres = list.filter((u) => !u.primary);
    els.urg.innerHTML = (vitaux.length ? vitaux : list).map(pill).join('')
      + (autres.length
        ? `<button class="urg urg-more" type="button" aria-expanded="false">+${autres.length} autres</button>`
          + `<span class="urg-extra" hidden>${autres.map(pill).join('')}</span>`
        : '');
    const more = els.urg.querySelector('.urg-more');
    if (more) more.addEventListener('click', () => {
      const extra = els.urg.querySelector('.urg-extra');
      const open = !extra.hidden;
      extra.hidden = open;
      more.setAttribute('aria-expanded', String(!open));
      more.hidden = !open;
    });
  }

  // --- carte -------------------------------------------------------------
  // Leaflet n'est tiré qu'à la première ouverture de la carte : la majorité des visites
  // cherchent un numéro et n'ouvriront jamais le plan.
  let leafletDemande = false;
  function chargerLeaflet() {
    if (leafletDemande) return;
    leafletDemande = true;
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    css.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    css.crossOrigin = '';
    document.head.appendChild(css);
    const js = document.createElement('script');
    js.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    js.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    js.crossOrigin = '';
    js.onload = () => { if (state.map) toggleMap(true); };
    document.head.appendChild(js);
  }
  function toggleMap(on) {
    state.map = on;
    els.mapPanel.hidden = !on;
    els.btnCarte.setAttribute('aria-pressed', String(on));
    if (on) {
      chargerLeaflet();
      if (!window.L) {
        $('.map-note', els.mapPanel).textContent = 'La carte ne peut pas se charger (connexion indisponible ?).';
        writeUrl();
        return;
      }
      if (!map) {
        map = L.map('map', { scrollWheelZoom: false }).setView([12.63, -8.0], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(map);
        layer = L.layerGroup().addTo(map);
      }
      updateMarkers(filtered());
      setTimeout(() => map.invalidateSize(), 50);
    }
    writeUrl();
  }

  function updateMarkers(list) {
    if (!map) return;
    layer.clearLayers();
    const pts = list.filter((e) => e.lat && e.lng);
    pts.forEach((e) => {
      L.marker([e.lat, e.lng]).addTo(layer)
        .bindPopup(`<b>${esc(e.name)}</b>${esc(e.address || e.quartier || '')}<br><a href="#f-${esc(e.id)}" data-goto="${esc(e.id)}">Voir la fiche</a>`);
    });
    if (pts.length) map.fitBounds(L.latLngBounds(pts.map((e) => [e.lat, e.lng])).pad(0.15), { maxZoom: 15 });
  }

  // --- événements --------------------------------------------------------
  function bind() {
    let t;
    els.q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { state.q = els.q.value; render(); }, 120); });
    els.qClear.addEventListener('click', () => { els.q.value = ''; state.q = ''; render(); els.q.focus(); });
    els.commune.addEventListener('change', () => { state.commune = els.commune.value; render(); });
    els.sort.addEventListener('change', async () => {
      state.sort = els.sort.value;
      if (state.sort === 'proche' && !maPosition) {
        writeUrl();
        if (!(await demanderPosition())) return;
      }
      render();
    });
    const reset = () => {
      Object.assign(state, { q: '', cat: '', commune: '', sort: 'name' });
      els.q.value = ''; els.commune.value = ''; els.sort.value = 'name';
      render();
    };
    els.reset.addEventListener('click', reset);
    els.emptyReset.addEventListener('click', reset);
    els.btnCarte.addEventListener('click', () => toggleMap(!state.map));

    document.addEventListener('click', async (ev) => {
      const share = ev.target.closest('[data-share]');
      if (share) {
        const e = DATA.entries.find((x) => x.id === share.dataset.share);
        const url = `${location.origin}${location.pathname}?q=${encodeURIComponent(e.name)}`;
        const tels = (e.phones || []).map((p) => phoneInfo(typeof p === 'string' ? p : p.number).display).join(' / ');
        const text = `${e.name}${e.address ? ' — ' + e.address : ''}${tels ? ' — Tél. ' + tels : ''}`;
        try {
          if (navigator.share) await navigator.share({ title: e.name, text, url });
          else {
            await navigator.clipboard.writeText(`${text}\n${url}`);
            const span = share.querySelector('span');
            span.textContent = 'Copié !';
            setTimeout(() => { span.textContent = 'Partager'; }, 1500);
          }
        } catch (_) { /* partage annulé */ }
      }
      const goto = ev.target.closest('[data-goto]');
      if (goto) {
        ev.preventDefault();
        const card = document.getElementById(`f-${goto.dataset.goto}`);
        if (card) {
          card.open = true;              // arriver depuis la carte doit montrer le détail
          const doux = !matchMedia('(prefers-reduced-motion: reduce)').matches;
          card.scrollIntoView({ behavior: doux ? 'smooth' : 'auto', block: 'center' });
          card.classList.add('flash');
          setTimeout(() => card.classList.remove('flash'), 1800);
        }
      }
    });
  }

  // Le bandeau d'urgence colle sous l'en-tête : sa hauteur est mesurée, car elle change
  // avec le contenu (attribution, retour à la ligne du titre sur petit écran).
  function mesurerEntete() {
    const h = document.querySelector('.top')?.offsetHeight;
    if (h) document.documentElement.style.setProperty('--head-h', `${h}px`);
  }

  // --- démarrage ---------------------------------------------------------
  async function init() {
    readUrl();
    els.q.value = state.q;
    els.sort.value = state.sort;
    try {
      const r = await fetch('data/annuaire.json', { cache: 'no-cache' });
      DATA = await r.json();
    } catch (err) {
      // Panne de chargement : dire quoi faire, et laisser les numéros d'urgence accessibles.
      els.grid.innerHTML = '';
      els.count.textContent = 'Annuaire indisponible';
      els.empty.hidden = false;
      els.empty.firstElementChild.innerHTML =
        `<strong>Les fiches n'ont pas pu être chargées.</strong> Vérifiez votre connexion et rechargez la page.
         Les numéros d'urgence en haut de l'écran restent composables.`;
      return;
    }
    DATA.entries.forEach((e) => {
      const phones = (e.phones || []).map((p) => (typeof p === 'string' ? p : p.number));
      e._hay = hayOf([e.name, e.acronym, e.type, e.address, e.quartier, e.commune,
        DATA.categories[e.category]?.label, e.hours, ...(e.tags || []), ...phones].join(' '));
    });
    const href = suggestUrl(null);
    els.suggest.forEach((a) => {
      if (!href) return;                       // la phrase reste masquée tant que meta.repo est vide
      a.href = href;
      a.closest('.suggest-line').hidden = false;
    });
    renderUrgences(); renderChips(); renderCommunes(); bind();
    mesurerEntete();
    addEventListener('resize', mesurerEntete, { passive: true });
    const n = DATA.entries.length;
    const withGeo = DATA.entries.filter((e) => e.lat && e.lng).length;
    const verif = DATA.entries.filter((e) => e.source?.verified).length;
    const heures = DATA.entries.filter((e) => e.hours).length;
    // La fiabilité est ce que cet annuaire promet : le chiffre doit être affiché, pas déduit.
    els.stats.textContent = `${n} structures, dont ${verif} recoupées à la main et ${withGeo} géolocalisées. `
      + `Horaires connus pour ${heures} d'entre elles seulement. Base mise à jour le ${fmtDate(DATA.meta.generated)}.`;
    if (state.map) toggleMap(true);
    render();
    if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => {});
  }
  init();
})();
