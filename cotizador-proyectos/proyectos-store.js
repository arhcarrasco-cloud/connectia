/* ============================================================
   Connectia · Cotizador de Proyectos
   Store compartido de PROYECTOS SELLADOS + documentos
   - Registros de proyecto  -> localStorage  (clave CX_PROJECTS_KEY)
   - Documentos (PDF/JPG...) -> IndexedDB    (sin límite de 5 MB)
   Usado por index.html (cotizador) y proyectos.html (tabla maestra)
   ============================================================ */
(function (global) {
  'use strict';

  const PROJECTS_KEY = 'connectiaProyectosSellados';
  const DB_NAME = 'connectiaCotizadorDocs';
  const DB_STORE = 'docs';
  const DB_VERSION = 1;

  /* ---------- Catálogo de documentos ---------- */
  const DOC_SLOTS = [
    { key: 'ocCliente',        label: 'OC Cliente → Connectia',   short: 'OC Cli' },
    { key: 'ocProveedor',      label: 'OC Connectia → Proveedor', short: 'OC Prov' },
    { key: 'facturaCliente',   label: 'Factura a Cliente',        short: 'Fac Cli' },
    { key: 'facturaProveedor', label: 'Factura del Proveedor',    short: 'Fac Prov' }
  ];

  /* ---------- Utilidades de formato ---------- */
  function money(n) {
    if (n === null || n === undefined || isNaN(n)) return '—';
    return '$' + Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function pct(n) {
    if (n === null || n === undefined || isNaN(n)) return '—';
    return Number(n).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
  }
  function today() {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }
  function parseDate(iso) {
    if (!iso) return null;
    const parts = String(iso).slice(0, 10).split('-');
    if (parts.length !== 3) return null;
    const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return isNaN(d.getTime()) ? null : d;
  }
  function fmtDate(iso) {
    const d = parseDate(iso);
    if (!d) return '—';
    return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: '2-digit' });
  }
  function addDays(iso, days) {
    const d = parseDate(iso);
    if (!d || days === null || days === undefined || days === '' || isNaN(days)) return '';
    d.setDate(d.getDate() + Number(days));
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }
  function daysBetween(isoA, isoB) {
    const a = parseDate(isoA), b = parseDate(isoB);
    if (!a || !b) return null;
    return Math.round((b - a) / 86400000);
  }
  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* ---------- Persistencia de proyectos ---------- */
  function listProjects() {
    try {
      const raw = localStorage.getItem(PROJECTS_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) {
      console.warn('[CX] No se pudo leer la base de proyectos', e);
      return [];
    }
  }
  function persist(list) {
    localStorage.setItem(PROJECTS_KEY, JSON.stringify(list));
  }
  function getProject(id) {
    return listProjects().find(p => p.id === id) || null;
  }
  function saveProject(project) {
    const list = listProjects();
    const now = new Date().toISOString();
    project.updatedAt = now;
    const idx = list.findIndex(p => p.id === project.id);
    if (idx === -1) {
      project.sealedAt = project.sealedAt || now;
      list.unshift(project);
    } else {
      list[idx] = project;
    }
    persist(list);
    return project;
  }
  function deleteProject(id) {
    const p = getProject(id);
    if (p && p.docs) {
      Object.keys(p.docs).forEach(k => { if (p.docs[k] && p.docs[k].docId) deleteDoc(p.docs[k].docId); });
    }
    persist(listProjects().filter(x => x.id !== id));
  }
  function newId() {
    return 'p_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  }

  /* ---------- Documentos en IndexedDB ---------- */
  function openDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(DB_STORE)) db.createObjectStore(DB_STORE, { keyPath: 'id' });
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  async function putDoc(file, meta) {
    const db = await openDB();
    const id = 'd_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
    const record = {
      id, blob: file, name: file.name, type: file.type || 'application/octet-stream',
      size: file.size, uploadedAt: new Date().toISOString(), ...(meta || {})
    };
    await new Promise((resolve, reject) => {
      const tx = db.transaction(DB_STORE, 'readwrite');
      tx.objectStore(DB_STORE).put(record);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    db.close();
    return { docId: id, name: record.name, type: record.type, size: record.size, uploadedAt: record.uploadedAt };
  }
  async function getDoc(docId) {
    const db = await openDB();
    const rec = await new Promise((resolve, reject) => {
      const req = db.transaction(DB_STORE, 'readonly').objectStore(DB_STORE).get(docId);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
    db.close();
    return rec;
  }
  async function deleteDoc(docId) {
    if (!docId) return;
    const db = await openDB();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(DB_STORE, 'readwrite');
      tx.objectStore(DB_STORE).delete(docId);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    db.close();
  }
  async function openDocInTab(docId) {
    const rec = await getDoc(docId);
    if (!rec) { alert('El archivo ya no está disponible en este navegador.'); return; }
    const url = URL.createObjectURL(rec.blob);
    window.open(url, '_blank');
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  async function downloadDoc(docId) {
    const rec = await getDoc(docId);
    if (!rec) { alert('El archivo ya no está disponible en este navegador.'); return; }
    const url = URL.createObjectURL(rec.blob);
    const a = document.createElement('a');
    a.href = url; a.download = rec.name || 'documento';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }

  /* ---------- Semáforo de vencimiento ---------- */
  // Devuelve {level:'paid'|'ok'|'soon'|'due'|'none', dias, texto}
  function pagoStatus(fechaPago, pagado, refDate) {
    if (pagado) return { level: 'paid', dias: null, texto: 'Pagado' };
    if (!fechaPago) return { level: 'none', dias: null, texto: 'Sin fecha' };
    const hoy = refDate || today();
    const d = daysBetween(hoy, fechaPago); // >0 faltan, <0 vencido
    if (d < 0) return { level: 'due', dias: d, texto: 'Vencido ' + Math.abs(d) + ' d' };
    if (d === 0) return { level: 'soon', dias: 0, texto: 'Vence hoy' };
    if (d <= 7) return { level: 'soon', dias: d, texto: 'Vence en ' + d + ' d' };
    return { level: 'ok', dias: d, texto: 'En ' + d + ' d' };
  }

  // Semáforo consolidado del proyecto (lo peor de cliente / proveedor / comisiones)
  function projectAlert(p) {
    const partes = [
      { k: 'Cliente',    s: pagoStatus(p.clientePago && p.clientePago.fechaPago, p.clientePago && p.clientePago.pagado) },
      { k: 'Proveedor',  s: pagoStatus(p.proveedor && p.proveedor.fechaPago, p.proveedor && p.proveedor.pagado) },
      { k: 'Comisiones', s: pagoStatus(p.comisionesPago && p.comisionesPago.fecha, p.comisionesPago && p.comisionesPago.pagado) }
    ];
    const rank = { due: 3, soon: 2, ok: 1, paid: 0, none: 0 };
    let peor = { level: 'paid', dias: null, texto: '' }, quien = '';
    partes.forEach(x => { if (rank[x.s.level] > rank[peor.level]) { peor = x.s; quien = x.k; } });
    const vencidos = partes.filter(x => x.s.level === 'due');
    return {
      level: peor.level,
      texto: peor.level === 'paid' ? 'Al corriente' : (quien ? quien + ': ' + peor.texto : peor.texto),
      detalle: partes.map(x => x.k + ' — ' + x.s.texto).join(' · '),
      vencidos: vencidos.map(x => x.k)
    };
  }

  /* ---------- Totales ---------- */
  function projectTotals(p) {
    const t = p.totals || {};
    return {
      costoProveedor: Number(t.costoProveedor) || 0,
      precioCliente: Number(t.precioCliente) || 0,
      comisiones: Number(t.comisiones) || 0,
      utilidad: Number(t.utilidad) || 0,
      margenPct: (t.precioCliente ? (Number(t.utilidad) / Number(t.precioCliente)) * 100 : null),
      iva: Number(t.iva) || 0,
      total: Number(t.total) || 0
    };
  }
  function sumTotals(list) {
    const acc = { costoProveedor: 0, precioCliente: 0, comisiones: 0, utilidad: 0, iva: 0, total: 0 };
    list.forEach(p => {
      const t = projectTotals(p);
      acc.costoProveedor += t.costoProveedor;
      acc.precioCliente += t.precioCliente;
      acc.comisiones += t.comisiones;
      acc.utilidad += t.utilidad;
      acc.iva += t.iva;
      acc.total += t.total;
    });
    acc.margenPct = acc.precioCliente > 0 ? (acc.utilidad / acc.precioCliente) * 100 : null;
    return acc;
  }

  global.CX = {
    PROJECTS_KEY, DOC_SLOTS,
    money, pct, today, fmtDate, addDays, daysBetween, parseDate, esc,
    listProjects, getProject, saveProject, deleteProject, newId,
    putDoc, getDoc, deleteDoc, openDocInTab, downloadDoc,
    pagoStatus, projectAlert, projectTotals, sumTotals
  };
})(window);
