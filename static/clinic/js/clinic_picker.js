// static/js/clinic_picker.js
(() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  const elPrompt = document.getElementById('location-prompt');
  const btnUseLocation = document.getElementById('btn-use-location');
  const btnEnterLocation = document.getElementById('btn-enter-location');
  const radiusSelect = document.getElementById('radius-select');
  const clinicsWrap = document.getElementById('clinics-wrap');
  const locationStatus = document.getElementById('location-status');
  const otherClinics = document.getElementById('other-clinics');
  const showAllLink = document.getElementById('show-all-clinics');

  // Config
  const API_URL = '/api/clinics/nearby/'; // make sure this is routed in Django
  const CACHE_KEY = 'ss_user_loc_v1'; // localStorage key
  const CACHE_TTL_MS = 1000 * 60 * 60 * 24; // 24 hours

  // Helpers
  function setStatus(msg) { locationStatus.textContent = msg || ''; }
  function showPrompt() { elPrompt.classList.remove('hidden'); }
  function hidePrompt() { elPrompt.classList.add('hidden'); }
  function renderSkeletons() {
    clinicsWrap.innerHTML = '';
    for (let i=0;i<3;i++){
      const s = document.createElement('div');
      s.className = 'skeleton p-4 rounded-lg h-28';
      clinicsWrap.appendChild(s);
    }
  }
  function showError(msg) {
    clinicsWrap.innerHTML = `<div class="p-4 bg-yellow-50 rounded text-sm">${msg}</div>`;
  }

  // render clinics array (from API)
  function renderClinics(clinics) {
    clinicsWrap.innerHTML = '';
    if (!clinics || clinics.length === 0) {
      clinicsWrap.innerHTML = `<div class="p-4 bg-white rounded text-sm text-slate-600">No clinics found within the selected radius.</div>`;
      otherClinics.classList.add('hidden');
      return;
    }

    clinics.forEach(clinic => {
      const card = document.createElement('div');
      card.className = 'clinic-card bg-white p-4 rounded-lg';

      // main row
      const mainRow = document.createElement('div');
      mainRow.className = 'flex justify-between items-start';
      mainRow.innerHTML = `
        <div>
          <div class="font-medium text-lg">${escapeHtml(clinic.name)}</div>
          <div class="text-xs text-slate-500">${clinic.open_now ? 'Open now' : 'Closed'}</div>
          <div class="mt-2 flex flex-wrap gap-2" aria-hidden="true"></div>
        </div>
        <div class="text-right">
          <div class="text-sm">${clinic.distance_km !== undefined ? clinic.distance_km.toFixed(1) + ' km' : ''}</div>
          <button class="mt-2 px-3 py-1 bg-blue-600 text-white rounded select-clinic">View services</button>
        </div>
      `;
      card.appendChild(mainRow);

      // chips area
      const chipsArea = mainRow.querySelector('div > div > div.mt-2 > div') || mainRow.querySelector('.mt-2.flex');
      const services = clinic.top_services || [];
      services.slice(0,3).forEach(s => {
        const btn = document.createElement('button');
        btn.className = 'text-xs border rounded px-2 py-1';
        btn.textContent = s.name;
        btn.addEventListener('click', (ev) => {
          ev.stopPropagation();
          // direct-select => go to booking with clinic+service
          goToBooking(clinic.id, s.id);
        });
        chipsArea.appendChild(btn);
      });

      // "View all services" placeholder
      const viewAll = document.createElement('button');
      viewAll.className = 'text-xs underline ml-2';
      viewAll.textContent = 'View all services';
      viewAll.addEventListener('click', () => toggleExpand(card, clinic));
      chipsArea.appendChild(viewAll);

      clinicsWrap.appendChild(card);
    });

    // show "other clinics" link if there are many results
    if (clinics.length > 8) otherClinics.classList.remove('hidden');
    else otherClinics.classList.add('hidden');
  }

  // Expand the clinic card to show full list of services (lazy)
  function toggleExpand(cardEl, clinic) {
    // If already expanded, collapse
    if (cardEl.querySelector('.services-expanded')) {
      cardEl.querySelector('.services-expanded').remove();
      return;
    }

    const expanded = document.createElement('div');
    expanded.className = 'services-expanded mt-3 border-t pt-3';
    expanded.innerHTML = '<div class="grid gap-2"></div>';
    const grid = expanded.querySelector('div');

    // If full services already present in payload, use them. Else fetch them.
    const servicesList = clinic.services || clinic.top_services || [];
    if (servicesList && servicesList.length > 0) {
      servicesList.forEach(s => grid.appendChild(serviceRow(s, clinic)));
      cardEl.appendChild(expanded);
    } else {
      // Fetch full services for clinic
      grid.innerHTML = '<div class="text-sm text-slate-500">Loading services…</div>';
      cardEl.appendChild(expanded);
      fetch(`/api/clinics/${clinic.id}/services/`) // add this endpoint on backend or adapt to your route
        .then(r => r.json())
        .then(data => {
          grid.innerHTML = '';
          (data.services || []).forEach(s => grid.appendChild(serviceRow(s, clinic)));
        })
        .catch(err => {
          grid.innerHTML = `<div class="text-sm text-red-500">Could not load services.</div>`;
        });
    }
  }

  function serviceRow(s, clinic) {
    const row = document.createElement('div');
    row.className = 'flex justify-between items-center';
    row.innerHTML = `
      <div>
        <div class="font-medium">${escapeHtml(s.name)}</div>
        <div class="text-xs text-slate-500">${s.duration_mins || ''} mins ${s.price ? ' • KES ' + s.price : ''}</div>
      </div>
    `;
    const bookWrap = document.createElement('div');
    const bookBtn = document.createElement('button');
    bookBtn.className = 'px-3 py-1 bg-green-600 text-white rounded';
    bookBtn.textContent = 'Book';
    bookBtn.addEventListener('click', () => goToBooking(clinic.id, s.id));
    bookWrap.appendChild(bookBtn);
    row.appendChild(bookWrap);
    return row;
  }

  // Redirect to booking page with clinic + service as query params (hand-off)
  function goToBooking(clinicId, serviceId) {
    // Adjust this URL to your existing booking flow - use query params for convenience
    const url = `/patients/book/?clinic_id=${encodeURIComponent(clinicId)}&service_id=${encodeURIComponent(serviceId)}`;
    window.location.href = url;
  }

  // Basic escape
  function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c])); }

  // Fetch nearby clinics using lat/lng & radius
  async function fetchNearby(lat, lng, radiusKm) {
    setStatus('Finding nearby clinics…');
    renderSkeletons();
    try {
      const url = `${API_URL}?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}&radius_km=${encodeURIComponent(radiusKm)}&limit=50`;
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Server error');
      const data = await res.json();
      renderClinics(data);
      setStatus('');
    } catch (err) {
      console.error(err);
      showError('Unable to fetch clinics right now. Try again later.');
      setStatus('');
    }
  }

  // Try from cached loc or ask geolocation
  function getCachedLocation() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const obj = JSON.parse(raw);
      if (!obj.t) return null;
      if ((Date.now() - obj.t) > (CACHE_TTL_MS)) {
        localStorage.removeItem(CACHE_KEY);
        return null;
      }
      return obj;
    } catch (e) { return null; }
  }
  function cacheLocation(lat, lng) {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ lat, lng, t: Date.now() }));
  }

  // Geolocation with timeout
  function runGeolocation(timeout = 8000) {
    setStatus('Detecting location…');
    renderSkeletons();
    const onError = (err) => {
      console.warn('geoloc error', err);
      setStatus('');
      showPrompt();
      showError('Location not available. Enter location manually.');
    };
    if (!navigator.geolocation) {
      onError({ message: 'Geolocation not supported' });
      return;
    }
    const timerId = setTimeout(() => onError({ message: 'Location timeout' }), timeout);
    navigator.geolocation.getCurrentPosition(pos => {
      clearTimeout(timerId);
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      cacheLocation(lat, lng);
      setStatus('');
      hidePrompt();
      fetchNearby(lat, lng, radiusSelect.value);
    }, onError, { enableHighAccuracy: true, maximumAge: 60000, timeout });
  }

  // Manual location fallback - simple prompt (replace with better UI/Geocoding if you have an API)
  function manualLocationFlow() {
    const entry = prompt('Enter a city or area (e.g., Nairobi, Westlands). Note: this will use approximate results.');
    if (!entry) return;
    // If you have a geocoding endpoint, call it here. For now: ask server to resolve text -> lat/lng
    setStatus('Resolving location…');
    renderSkeletons();
    fetch(`/api/geocode/?q=${encodeURIComponent(entry)}`)
      .then(r => r.json())
      .then(data => {
        if (data.lat && data.lng) {
          cacheLocation(data.lat, data.lng);
          fetchNearby(data.lat, data.lng, radiusSelect.value);
          setStatus('');
          hidePrompt();
        } else {
          showError('Could not find that location.');
          setStatus('');
        }
      })
      .catch(err => {
        console.error(err);
        showError('Could not resolve location.');
        setStatus('');
      });
  }

  // Toggle expand when View services clicked (some "select-clinic" buttons added)
  clinicsWrap.addEventListener('click', (e) => {
    const button = e.target.closest('.select-clinic');
    if (!button) return;
    const card = button.closest('.clinic-card');
    // find the clinic's data by name (we attach name in DOM, but better: store id in data attributes; for brevity we'll call toggleExpand with minimal info)
    // Better approach: store clinics in window._ss_clinics after fetch
    const name = card.querySelector('.font-medium').textContent;
    const clinic = (window._ss_clinics || []).find(c => c.name === name);
    if (clinic) toggleExpand(card, clinic);
  });

  // store clinics globally after fetch for quick lookup
  function storeGlobalClinics(arr) { window._ss_clinics = arr; }

  // Boot
  function boot() {
    // Setup handlers
    showPrompt(); // show by default (user can click "Use my location")
    btnUseLocation.addEventListener('click', () => {
      hidePrompt();
      runGeolocation();
    });
    btnEnterLocation.addEventListener('click', manualLocationFlow);
    radiusSelect.addEventListener('change', () => {
      const loc = getCachedLocation();
      if (loc && loc.lat && loc.lng) fetchNearby(loc.lat, loc.lng, radiusSelect.value);
    });
    showAllLink.addEventListener('click', (e) => {
      e.preventDefault();
      // show all by increasing radius and re-running
      radiusSelect.value = 25;
      const loc = getCachedLocation();
      if (loc && loc.lat && loc.lng) fetchNearby(loc.lat, loc.lng, 25);
    });

    // Try cached location first
    const cached = getCachedLocation();
    if (cached) {
      hidePrompt();
      fetchNearby(cached.lat, cached.lng, radiusSelect.value);
    } else {
      // show prompt; user action required for privacy best practice
      showPrompt();
      clinicsWrap.innerHTML = ''; // remove skeleton
    }

    // Intercept fetchNearby to store clinics globally
    const origFetchNearby = fetchNearby;
    fetchNearby = async function(lat, lng, radius) {
      renderSkeletons();
      try {
        const url = `${API_URL}?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}&radius_km=${encodeURIComponent(radius)}&limit=50`;
        const res = await fetch(url, { credentials: 'same-origin' });
        if (!res.ok) throw new Error('Server error');
        const data = await res.json();
        storeGlobalClinics(data);
        renderClinics(data);
        setStatus('');
      } catch (err) {
        console.error(err);
        showError('Unable to fetch clinics right now. Try again later.');
        setStatus('');
      }
    };
  }

  // run
  boot();

})();
