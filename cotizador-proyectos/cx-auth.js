/* ============================================================
   Connectia · Cotizador de Proyectos
   Capa de identidad y nube (Supabase)
   - Login / alta de usuario con correo y contraseña propia
   - Cada usuario ve y edita SOLO sus proyectos
   - El admin (Roger) ve, edita y elimina todo
   - Las sesiones viven en la tabla cx_sesiones (RLS)
   - Los documentos viven en el bucket cx-docs
   ============================================================ */
(function (global) {
  'use strict';

  const SUPABASE_URL = 'https://mduxlmnlwycwknyapwsx.supabase.co';
  const SUPABASE_KEY = 'sb_publishable_lqa9WdRYSvYZ1elBbkN_ZQ_pMCGJdxL';
  const TABLA = 'cx_sesiones';
  const BUCKET = 'cx-docs';
  const LOCAL_KEY = 'cotizadorConnectiaSessions';

  let sb = null;
  let user = null;
  let perfil = null;
  let cache = [];           // sesiones en memoria (mismo shape que el localStorage anterior)
  let cuentas = [];         // catálogo de cuentas/marcas con su responsable
  let snapshot = new Map(); // id -> JSON, para detectar cambios
  let readyCbs = [];
  let booted = false;

  /* ---------------- UI: pantalla de acceso ---------------- */
  function injectStyles() {
    if (document.getElementById('cxAuthStyles')) return;
    const s = document.createElement('style');
    s.id = 'cxAuthStyles';
    s.textContent = `
    #cxAuthOverlay{position:fixed;inset:0;z-index:9999;background:#1B1036;display:flex;align-items:center;justify-content:center;padding:24px;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}
    #cxAuthOverlay.hidden{display:none}
    .cxa-card{width:100%;max-width:420px;background:#fff;border-radius:18px;padding:34px 32px 28px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
    .cxa-brand{font-size:26px;font-weight:800;letter-spacing:-.5px;color:#1B1036;margin:0}
    .cxa-eyebrow{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#6030A0;font-weight:700;margin:0 0 6px}
    .cxa-sub{font-size:13px;color:#6b6880;margin:6px 0 22px;line-height:1.5}
    .cxa-tabs{display:flex;gap:6px;background:#f2f0f7;padding:4px;border-radius:10px;margin-bottom:20px}
    .cxa-tab{flex:1;border:0;background:transparent;padding:9px 8px;border-radius:8px;font:600 13px Inter,sans-serif;color:#6b6880;cursor:pointer}
    .cxa-tab.active{background:#fff;color:#1B1036;box-shadow:0 1px 3px rgba(0,0,0,.12)}
    .cxa-field{margin-bottom:14px}
    .cxa-field label{display:block;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#6b6880;margin-bottom:6px}
    .cxa-field input{width:100%;box-sizing:border-box;padding:11px 12px;border:1px solid #ddd9e8;border-radius:9px;font:400 14px Inter,sans-serif;color:#1B1036;background:#fff}
    .cxa-field input:focus{outline:0;border-color:#6030A0;box-shadow:0 0 0 3px rgba(96,48,160,.14)}
    .cxa-btn{width:100%;border:0;border-radius:10px;padding:12px;font:700 14px Inter,sans-serif;cursor:pointer;background:#6030A0;color:#fff;margin-top:6px}
    .cxa-btn:hover{background:#4d2682}
    .cxa-btn[disabled]{opacity:.6;cursor:default}
    .cxa-link{display:block;width:100%;background:none;border:0;color:#6030A0;font:600 12px Inter,sans-serif;cursor:pointer;margin-top:14px;text-align:center}
    .cxa-msg{margin-top:14px;padding:10px 12px;border-radius:9px;font-size:12.5px;line-height:1.45;display:none}
    .cxa-msg.err{display:block;background:#fdecec;color:#a4262c;border:1px solid #f5c6c6}
    .cxa-msg.ok{display:block;background:#eaf7ee;color:#1c7c3c;border:1px solid #bfe6cb}
    .cxa-foot{margin-top:20px;font-size:11px;color:#9a97ab;text-align:center;line-height:1.5}
    /* barra de usuario */
    .cx-userbar{display:flex;align-items:center;justify-content:flex-end;gap:12px;padding:8px 18px;background:#1B1036;color:#fff;font:500 12.5px Inter,sans-serif}
    .cx-userbar .cx-u-mail{font-weight:600}
    .cx-userbar .cx-u-rol{font-size:10px;letter-spacing:.1em;text-transform:uppercase;background:#6030A0;padding:3px 8px;border-radius:20px;font-weight:700}
    .cx-userbar .cx-u-rol.user{background:rgba(255,255,255,.18)}
    .cx-userbar button{background:rgba(255,255,255,.14);border:0;color:#fff;font:600 12px Inter,sans-serif;padding:6px 12px;border-radius:7px;cursor:pointer}
    .cx-userbar button:hover{background:rgba(255,255,255,.26)}
    .cx-sync{font-size:11px;color:#c9c2e4;min-width:90px;text-align:right}
    `;
    document.head.appendChild(s);
  }

  function buildOverlay() {
    injectStyles();
    const el = document.createElement('div');
    el.id = 'cxAuthOverlay';
    el.innerHTML = `
      <div class="cxa-card">
        <p class="cxa-eyebrow">Connectia</p>
        <h1 class="cxa-brand">Cotizador de Proyectos</h1>
        <p class="cxa-sub" id="cxaSub">Entra con tu correo. Cada quien ve y edita sus propios proyectos.</p>
        <div class="cxa-tabs">
          <button class="cxa-tab active" id="cxaTabLogin" type="button">Entrar</button>
          <button class="cxa-tab" id="cxaTabSignup" type="button">Crear cuenta</button>
        </div>
        <form id="cxaForm" autocomplete="on">
          <div class="cxa-field" id="cxaNombreWrap" style="display:none">
            <label for="cxaNombre">Nombre</label>
            <input type="text" id="cxaNombre" autocomplete="name" placeholder="Tu nombre">
          </div>
          <div class="cxa-field">
            <label for="cxaEmail">Correo</label>
            <input type="email" id="cxaEmail" autocomplete="username" placeholder="tucorreo@connectia.mx" required>
          </div>
          <div class="cxa-field" id="cxaPassWrap">
            <label for="cxaPass">Contraseña</label>
            <input type="password" id="cxaPass" autocomplete="current-password" placeholder="Mínimo 8 caracteres" required>
          </div>
          <button class="cxa-btn" id="cxaSubmit" type="submit">Entrar</button>
        </form>
        <button class="cxa-link" id="cxaForgot" type="button">¿Olvidaste tu contraseña?</button>
        <div class="cxa-msg" id="cxaMsg"></div>
        <p class="cxa-foot">Tus proyectos son privados. Solo tú —y la dirección— pueden verlos.</p>
      </div>`;
    document.body.appendChild(el);

    const tabL = el.querySelector('#cxaTabLogin'), tabS = el.querySelector('#cxaTabSignup');
    tabL.onclick = () => setMode('login');
    tabS.onclick = () => setMode('signup');
    el.querySelector('#cxaForgot').onclick = onForgot;
    el.querySelector('#cxaForm').onsubmit = onSubmit;
    return el;
  }

  let mode = 'login';
  function setMode(m) {
    mode = m;
    const q = id => document.getElementById(id);
    q('cxaTabLogin').classList.toggle('active', m === 'login');
    q('cxaTabSignup').classList.toggle('active', m === 'signup');
    q('cxaNombreWrap').style.display = m === 'signup' ? '' : 'none';
    q('cxaPassWrap').style.display = '';
    q('cxaSubmit').textContent = m === 'signup' ? 'Crear mi cuenta' : 'Entrar';
    q('cxaPass').setAttribute('autocomplete', m === 'signup' ? 'new-password' : 'current-password');
    q('cxaSub').textContent = m === 'signup'
      ? 'Regístrate con tu correo y define tu propia contraseña.'
      : 'Entra con tu correo. Cada quien ve y edita sus propios proyectos.';
    msg('');
  }

  function msg(text, kind) {
    const el = document.getElementById('cxaMsg');
    if (!el) return;
    el.className = 'cxa-msg' + (text ? ' ' + (kind || 'err') : '');
    el.textContent = text || '';
  }

  function traduceError(e) {
    const m = (e && e.message ? e.message : String(e || '')).toLowerCase();
    if (m.includes('invalid login')) return 'Correo o contraseña incorrectos.';
    if (m.includes('email not confirmed')) return 'Tu correo aún no está confirmado. Revisa tu bandeja (y spam).';
    if (m.includes('already registered') || m.includes('already been registered')) return 'Ese correo ya tiene cuenta. Usa "Entrar" o recupera tu contraseña.';
    if (m.includes('password should be at least')) return 'La contraseña debe tener al menos 8 caracteres.';
    if (m.includes('rate limit') || m.includes('too many')) return 'Demasiados intentos. Espera un minuto e inténtalo de nuevo.';
    return e && e.message ? e.message : 'Ocurrió un error. Inténtalo de nuevo.';
  }

  async function onSubmit(ev) {
    ev.preventDefault();
    const btn = document.getElementById('cxaSubmit');
    const email = document.getElementById('cxaEmail').value.trim().toLowerCase();
    const pass = document.getElementById('cxaPass').value;
    const nombre = (document.getElementById('cxaNombre').value || '').trim();
    if (!email || !pass) return;
    if (mode === 'signup' && pass.length < 8) { msg('La contraseña debe tener al menos 8 caracteres.'); return; }
    btn.disabled = true; btn.textContent = 'Un momento…'; msg('');
    try {
      if (mode === 'signup') {
        const { data, error } = await sb.auth.signUp({
          email, password: pass,
          options: { data: { nombre: nombre || email.split('@')[0] }, emailRedirectTo: location.href.split('#')[0] }
        });
        if (error) throw error;
        if (data.session) { await afterLogin(); return; }
        msg('Cuenta creada. Te mandamos un correo de confirmación: ábrelo y luego entra aquí con tu contraseña.', 'ok');
        setMode('login');
      } else {
        const { error } = await sb.auth.signInWithPassword({ email, password: pass });
        if (error) throw error;
        await afterLogin();
        return;
      }
    } catch (e) {
      msg(traduceError(e));
    } finally {
      btn.disabled = false;
      btn.textContent = mode === 'signup' ? 'Crear mi cuenta' : 'Entrar';
    }
  }

  async function onForgot() {
    const email = (document.getElementById('cxaEmail').value || '').trim().toLowerCase();
    if (!email) { msg('Escribe tu correo arriba y vuelve a dar clic.'); return; }
    try {
      const { error } = await sb.auth.resetPasswordForEmail(email, { redirectTo: location.href.split('#')[0] });
      if (error) throw error;
      msg('Te enviamos un correo para restablecer tu contraseña.', 'ok');
    } catch (e) { msg(traduceError(e)); }
  }

  /* ---------------- barra de usuario ---------------- */
  function renderUserBar() {
    let bar = document.getElementById('cxUserBar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'cxUserBar';
      bar.className = 'cx-userbar';
      document.body.insertBefore(bar, document.body.firstChild);
    }
    const admin = isAdmin();
    bar.innerHTML = `
      <span class="cx-sync" id="cxSyncState"></span>
      <span class="cx-u-mail">${esc(perfil && perfil.nombre ? perfil.nombre : (user ? user.email : ''))}</span>
      <span class="cx-u-rol ${admin ? '' : 'user'}">${admin ? 'Admin · ve todo' : 'Mis cuentas'}</span>
      ${admin ? '<button type="button" onclick="CXAUTH.panelCuentas()">Cuentas</button>' : ''}
      <button type="button" onclick="CXAUTH.logout()">Salir</button>`;
  }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function sync(txt) {
    const el = document.getElementById('cxSyncState');
    if (!el) return;
    el.textContent = txt || '';
    if (txt && txt.indexOf('Guardado') === 0) setTimeout(() => { if (el.textContent === txt) el.textContent = ''; }, 2500);
  }

  /* ---------------- datos ---------------- */
  function rowToSession(r) {
    return {
      id: r.id, name: r.nombre || 'Sin nombre',
      savedAt: r.saved_at, lastOpenedAt: r.last_opened_at || r.saved_at,
      data: r.data || {}, ownerId: r.owner_id, ownerEmail: r.owner_email || ''
    };
  }
  function sessionToRow(s) {
    const resp = (s.data && s.data.responsable) || null;
    return {
      id: s.id, owner_id: s.ownerId || (user && user.id), owner_email: s.ownerEmail || (user && user.email),
      responsable_email: resp && resp.email ? String(resp.email).toLowerCase() : null,
      nombre: s.name || 'Sin nombre', data: s.data || {},
      saved_at: s.savedAt || new Date().toISOString(),
      last_opened_at: s.lastOpenedAt || s.savedAt || new Date().toISOString(),
      actualizado_en: new Date().toISOString()
    };
  }
  function snap(s) { return JSON.stringify({ n: s.name, d: s.data, sa: s.savedAt, lo: s.lastOpenedAt }); }

  /* ------- cuentas y responsables ------- */
  function norm(t) {
    return String(t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
  }
  function responsableDe(texto) {
    const t = norm(texto);
    if (!t) return null;
    for (const c of cuentas) {
      const claves = [c.cuenta].concat(c.alias || []).map(norm).filter(Boolean);
      for (const k of claves) {
        if (k && (t.indexOf(k) !== -1 || k.indexOf(t) === 0)) {
          return { cuenta: c.cuenta, nombre: c.responsable_nombre || '', email: (c.responsable_email || '').toLowerCase() };
        }
      }
    }
    return null;
  }
  /* Fija el responsable del proyecto según la cuenta del cliente (si no se asignó a mano) */
  function asignarResponsable(ses) {
    ses.data = ses.data || {};
    const actual = ses.data.responsable;
    if (actual && actual.manual) return actual;
    const h = ses.data.header || {};
    const r = responsableDe(h.clienteNombre) || responsableDe(h.razonSocial) || responsableDe(ses.name) || responsableDe(h.conceptoGeneral);
    if (r) { ses.data.responsable = { cuenta: r.cuenta, nombre: r.nombre, email: r.email, manual: false }; }
    else if (!actual) { ses.data.responsable = { cuenta: '', nombre: (perfil && perfil.nombre) || (user && user.email) || '', email: (user && user.email) || '', manual: false }; }
    return ses.data.responsable;
  }

  async function hydrate() {
    const cts = await sb.from('cx_cuentas').select('*').order('cuenta');
    if (!cts.error) cuentas = cts.data || [];
    const { data, error } = await sb.from(TABLA).select('*').order('saved_at', { ascending: false });
    if (error) { console.error('[CX] No se pudieron leer los proyectos', error); return; }
    cache.length = 0;
    snapshot.clear();
    (data || []).forEach(r => { const s = rowToSession(r); cache.push(s); snapshot.set(s.id, snap(s)); });
  }

  let cola = Promise.resolve();
  function encolar(fn) { cola = cola.then(fn).catch(e => console.error('[CX] sync', e)); return cola; }

  /* Recibe la lista completa (el código del cotizador la muta) y manda a la nube lo que cambió */
  function syncFromList(list) {
    if (!Array.isArray(list)) return;
    if (list !== cache) { cache.length = 0; list.forEach(s => cache.push(s)); }
    const vistos = new Set();
    const cambios = [];
    cache.forEach(s => {
      if (!s.ownerId) { s.ownerId = user.id; s.ownerEmail = user.email; }
      vistos.add(s.id);
      asignarResponsable(s);
      const sig = snap(s);
      if (snapshot.get(s.id) !== sig) { cambios.push(sessionToRow(s)); snapshot.set(s.id, sig); }
    });
    const borrar = [];
    snapshot.forEach((_, id) => { if (!vistos.has(id)) borrar.push(id); });
    borrar.forEach(id => snapshot.delete(id));
    if (!cambios.length && !borrar.length) return;
    sync('Guardando…');
    encolar(async () => {
      if (cambios.length) {
        const { error } = await sb.from(TABLA).upsert(cambios, { onConflict: 'id' });
        if (error) { sync('⚠ Error al guardar'); alert('No se pudo guardar en la nube: ' + error.message); return; }
      }
      if (borrar.length) {
        const { error } = await sb.from(TABLA).delete().in('id', borrar);
        if (error) { sync('⚠ Error al eliminar'); alert('No se pudo eliminar: ' + error.message); return; }
      }
      sync('Guardado ✓');
    });
  }

  function puedeEditar(s) {
    if (!s) return false;
    if (isAdmin()) return true;
    const oid = s.ownerId || (s.sesion && s.sesion.ownerId);
    if (!oid || oid === (user && user.id)) return true;
    const r = s.responsable || (s.data && s.data.responsable) || (s.sesion && s.sesion.data && s.sesion.data.responsable);
    return !!(r && r.email && user && r.email.toLowerCase() === user.email.toLowerCase());
  }
  function isAdmin() { return !!(perfil && perfil.rol === 'admin'); }

  /* ---------------- documentos en Supabase Storage ---------------- */
  function instalarDocs() {
    if (!global.CX) return;
    const legacy = { getDoc: CX.getDoc, deleteDoc: CX.deleteDoc, putDoc: CX.putDoc };

    CX.putDoc = async function (file, meta) {
      meta = meta || {};
      const ses = cache.find(s => s.id === meta.projectId);
      const dueno = (ses && ses.ownerId) || user.id;
      const limpio = (file.name || 'archivo').replace(/[^\w.\-]+/g, '_').slice(-60);
      const path = dueno + '/' + (meta.projectId || 'general') + '/' + Date.now() + '_' + limpio;
      const { error } = await sb.storage.from(BUCKET).upload(path, file, { upsert: true, contentType: file.type || 'application/octet-stream' });
      if (error) throw new Error(error.message);
      return { docId: path, name: file.name, type: file.type || 'application/octet-stream', size: file.size, uploadedAt: new Date().toISOString() };
    };

    CX.getDoc = async function (docId) {
      if (!docId) return null;
      if (docId.indexOf('d_') === 0) return legacy.getDoc(docId); // archivos viejos guardados en este navegador
      const { data, error } = await sb.storage.from(BUCKET).download(docId);
      if (error) return null;
      return { id: docId, blob: data, name: docId.split('/').pop().replace(/^\d+_/, ''), type: data.type };
    };

    CX.deleteDoc = async function (docId) {
      if (!docId) return;
      if (docId.indexOf('d_') === 0) return legacy.deleteDoc(docId);
      await sb.storage.from(BUCKET).remove([docId]);
    };
  }

  /* ---------------- migración de lo que ya estaba en el navegador ---------------- */
  async function migrarLocal() {
    let locales = [];
    try { locales = JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]'); } catch (e) { locales = []; }
    locales = (locales || []).filter(s => s && s.id);
    // Los proyectos de ejemplo solo se suben para el admin (son su base real de trabajo)
    if (!isAdmin()) locales = locales.filter(s => !String(s.id).startsWith('s_seed_'));
    if (!locales.length) return;
    const nuevos = locales.filter(s => !snapshot.has(s.id));
    if (!nuevos.length) return;
    sync('Subiendo ' + nuevos.length + '…');
    const filas = nuevos.map(s => {
      const ses = {
        id: s.id, name: s.name, data: s.data || {}, savedAt: s.savedAt, lastOpenedAt: s.lastOpenedAt,
        ownerId: user.id, ownerEmail: user.email
      };
      asignarResponsable(ses);
      return sessionToRow(ses);
    });
    const { error } = await sb.from(TABLA).upsert(filas, { onConflict: 'id' });
    if (error) { console.error('[CX] migración', error); sync('⚠ No se pudieron subir'); return; }
    localStorage.setItem(LOCAL_KEY + '_migrado', new Date().toISOString());
    await hydrate();
    sync('Guardado ✓');
  }

  /* ---------------- arranque ---------------- */
  async function cargarPerfil() {
    const { data } = await sb.from('cx_perfiles').select('*').eq('id', user.id).maybeSingle();
    perfil = data || { id: user.id, email: user.email, nombre: (user.user_metadata || {}).nombre || user.email.split('@')[0], rol: 'user' };
  }

  async function afterLogin() {
    const { data: { user: u } } = await sb.auth.getUser();
    user = u;
    if (!user) return;
    await cargarPerfil();
    await hydrate();
    instalarDocs();
    await migrarLocal();
    const ov = document.getElementById('cxAuthOverlay');
    if (ov) ov.classList.add('hidden');
    renderUserBar();
    if (!booted) {
      booted = true;
      readyCbs.forEach(fn => { try { fn(); } catch (e) { console.error(e); } });
      readyCbs = [];
    } else if (global.renderBoard) {
      try { global.renderSessionsList && global.renderSessionsList(); global.renderBoard(); } catch (e) {}
    }
  }

  async function init() {
    if (!global.supabase || !global.supabase.createClient) {
      console.error('[CX] No cargó supabase-js');
      alert('No se pudo cargar la librería de acceso. Revisa tu conexión y recarga la página.');
      return;
    }
    sb = global.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
    });
    buildOverlay();
    const { data: { session } } = await sb.auth.getSession();
    if (session) { await afterLogin(); }
    else {
      const em = localStorage.getItem('cxUltimoCorreo');
      if (em) document.getElementById('cxaEmail').value = em;
    }
    sb.auth.onAuthStateChange((evt) => {
      if (evt === 'SIGNED_OUT') location.reload();
      if (evt === 'PASSWORD_RECOVERY') {
        const np = prompt('Escribe tu nueva contraseña (mínimo 8 caracteres):');
        if (np && np.length >= 8) sb.auth.updateUser({ password: np }).then(() => alert('Contraseña actualizada. Ya puedes entrar.'));
      }
    });
  }

  /* ---------------- panel de cuentas (solo admin) ---------------- */
  function panelCuentas() {
    if (!isAdmin()) return;
    let el = document.getElementById('cxCuentasModal');
    if (!el) {
      el = document.createElement('div');
      el.id = 'cxCuentasModal';
      el.style.cssText = 'position:fixed;inset:0;z-index:9000;background:rgba(27,16,54,.55);display:flex;align-items:center;justify-content:center;padding:24px;font-family:Inter,sans-serif';
      el.onclick = e => { if (e.target === el) el.remove(); };
      document.body.appendChild(el);
    }
    const filas = cuentas.map(c => `
      <tr data-id="${c.id}">
        <td style="font-weight:700;color:#1B1036">${esc(c.cuenta)}</td>
        <td style="font-size:11px;color:#8b88a0">${esc((c.alias || []).join(', '))}</td>
        <td><input class="cxc-nom" value="${esc(c.responsable_nombre || '')}" placeholder="Nombre" style="width:100%;padding:7px 8px;border:1px solid #ddd9e8;border-radius:7px;font:400 13px Inter"></td>
        <td><input class="cxc-mail" value="${esc(c.responsable_email || '')}" placeholder="correo@connectia.mx" style="width:100%;padding:7px 8px;border:1px solid #ddd9e8;border-radius:7px;font:400 13px Inter"></td>
      </tr>`).join('');
    el.innerHTML = `
      <div style="background:#fff;border-radius:16px;max-width:860px;width:100%;max-height:86vh;overflow:auto;padding:26px 28px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px">
          <div>
            <p style="margin:0 0 4px;font:700 11px Inter;letter-spacing:.16em;text-transform:uppercase;color:#6030A0">Administración</p>
            <h2 style="margin:0;font:800 20px Inter;color:#1B1036">Cuentas y responsables</h2>
            <p style="margin:6px 0 0;font:400 12.5px Inter;color:#6b6880;max-width:620px">El correo define quién puede ver y editar los proyectos de esa cuenta. Debe ser el mismo con el que esa persona entra al cotizador.</p>
          </div>
          <button onclick="document.getElementById('cxCuentasModal').remove()" style="border:0;background:none;font-size:20px;cursor:pointer;color:#8b88a0">✕</button>
        </div>
        <table style="width:100%;border-collapse:collapse;margin-top:18px;font:400 13px Inter">
          <thead><tr style="text-align:left;color:#6b6880;font:700 10.5px Inter;letter-spacing:.08em;text-transform:uppercase">
            <th style="padding:8px 6px">Cuenta</th><th style="padding:8px 6px">Se detecta como</th><th style="padding:8px 6px;width:200px">Responsable</th><th style="padding:8px 6px;width:250px">Correo (acceso)</th>
          </tr></thead>
          <tbody id="cxcBody">${filas}</tbody>
        </table>
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:20px">
          <span id="cxcMsg" style="font:400 12px Inter;color:#1c7c3c"></span>
          <div style="display:flex;gap:10px">
            <button onclick="document.getElementById('cxCuentasModal').remove()" style="border:1px solid #ddd9e8;background:#fff;color:#1B1036;font:600 13px Inter;padding:10px 16px;border-radius:9px;cursor:pointer">Cerrar</button>
            <button id="cxcSave" style="border:0;background:#6030A0;color:#fff;font:700 13px Inter;padding:10px 18px;border-radius:9px;cursor:pointer">Guardar cambios</button>
          </div>
        </div>
      </div>`;
    document.getElementById('cxcSave').onclick = async () => {
      const filas = [...document.querySelectorAll('#cxcBody tr')];
      const cambios = filas.map(tr => ({
        id: tr.dataset.id,
        responsable_nombre: tr.querySelector('.cxc-nom').value.trim(),
        responsable_email: tr.querySelector('.cxc-mail').value.trim().toLowerCase() || null
      }));
      for (const c of cambios) {
        const { error } = await sb.from('cx_cuentas').update({ responsable_nombre: c.responsable_nombre, responsable_email: c.responsable_email }).eq('id', c.id);
        if (error) { alert('No se pudo guardar: ' + error.message); return; }
      }
      await hydrate();
      document.getElementById('cxcMsg').textContent = 'Guardado ✓';
      if (global.renderBoard) try { global.renderBoard(); } catch (e) {}
    };
  }

  global.CXAUTH = {
    cloud: true,
    get user() { return user; },
    get perfil() { return perfil; },
    isAdmin,
    puedeEditar,
    all() { return cache; },
    cuentas() { return cuentas; },
    responsableDe,
    asignarResponsable,
    panelCuentas,
    syncFromList,
    hydrate,
    onReady(fn) { if (booted) fn(); else readyCbs.push(fn); },
    async logout() {
      if (user) localStorage.setItem('cxUltimoCorreo', user.email);
      await sb.auth.signOut();
      location.reload();
    },
    async usuarios() {
      const { data } = await sb.from('cx_perfiles').select('*').order('creado_en');
      return data || [];
    },
    sync
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})(window);
