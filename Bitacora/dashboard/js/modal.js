/**
 * Controlador del Modal Interactivo "Bajo el Capó"
 * Soporta navegación entre los 7 puntos, cambio de pestañas y atajos de teclado.
 */
let puntoActualModal = 1;
let tabActualModal = 'todo';

function abrirModal(puntoNum) {
  puntoActualModal = parseInt(puntoNum) || 1;
  actualizarContenidoModal();
  const modal = document.getElementById('modal-detalle');
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function cerrarModal() {
  const modal = document.getElementById('modal-detalle');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

function clickBackdrop(e) {
  if (e.target.id === 'modal-detalle') {
    cerrarModal();
  }
}

function navegarModal(delta) {
  let nuevo = puntoActualModal + delta;
  if (nuevo < 1) nuevo = 7;
  if (nuevo > 7) nuevo = 1;
  puntoActualModal = nuevo;
  actualizarContenidoModal();
}

function cambiarTabModal(tab) {
  tabActualModal = tab;
  
  const secScripts = document.getElementById('modal-sec-scripts');
  const secArchivos = document.getElementById('modal-sec-archivos');
  
  const btnTodo = document.getElementById('modal-tab-todo-btn');
  const btnScripts = document.getElementById('modal-tab-scripts-btn');
  const btnArchivos = document.getElementById('modal-tab-archivos-btn');

  if (!btnTodo || !btnScripts || !btnArchivos) return;

  // reset styles
  [btnTodo, btnScripts, btnArchivos].forEach(b => {
    b.className = 'py-2.5 border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer';
  });

  if (tab === 'todo') {
    if (secScripts) secScripts.classList.remove('hidden');
    if (secArchivos) secArchivos.classList.remove('hidden');
    btnTodo.className = 'py-2.5 border-b-2 border-cyan-400 text-cyan-400 font-semibold flex items-center gap-1.5 transition-colors cursor-pointer';
  } else if (tab === 'scripts') {
    if (secScripts) secScripts.classList.remove('hidden');
    if (secArchivos) secArchivos.classList.add('hidden');
    btnScripts.className = 'py-2.5 border-b-2 border-cyan-400 text-cyan-400 font-semibold flex items-center gap-1.5 transition-colors cursor-pointer';
  } else if (tab === 'archivos') {
    if (secScripts) secScripts.classList.add('hidden');
    if (secArchivos) secArchivos.classList.remove('hidden');
    btnArchivos.className = 'py-2.5 border-b-2 border-cyan-400 text-cyan-400 font-semibold flex items-center gap-1.5 transition-colors cursor-pointer';
  }
}

function actualizarContenidoModal() {
  if (typeof DETALLES_PUNTOS === 'undefined') return;
  const data = DETALLES_PUNTOS[puntoActualModal];
  if (!data) return;

  const numEl = document.getElementById('modal-punto-num');
  const titEl = document.getElementById('modal-titulo');
  const subEl = document.getElementById('modal-subtitulo');
  if (numEl) numEl.innerText = data.num;
  if (titEl) titEl.innerText = data.titulo;
  if (subEl) subEl.innerText = data.subtitulo;

  // Render Scripts
  const scriptsCont = document.getElementById('modal-scripts-container');
  if (scriptsCont) {
    scriptsCont.innerHTML = data.scripts.map(s => {
      const badgeColor = s.color === 'emerald' ? 'bg-emerald-500/20 text-emerald-300' :
                         s.color === 'cyan' ? 'bg-cyan-500/20 text-cyan-300' :
                         s.color === 'purple' ? 'bg-purple-500/20 text-purple-300' :
                         s.color === 'amber' ? 'bg-amber-500/20 text-amber-300' :
                         s.color === 'blue' ? 'bg-blue-500/20 text-blue-300' : 'bg-slate-700 text-slate-300';
      return `
        <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white font-mono">${s.path}</span>
            <span class="text-[9px] px-1.5 py-0.5 rounded ${badgeColor} font-semibold">${s.rol}</span>
          </div>
          <p class="text-slate-300 text-[11px] leading-relaxed">${s.desc}</p>
        </div>
      `;
    }).join('');
  }

  // Render Archivos Antes
  const antesCont = document.getElementById('modal-archivos-antes');
  if (antesCont) {
    antesCont.innerHTML = data.archivosAntes.map(a => `
      <div class="text-slate-300 flex items-start gap-1.5">
        <span class="text-slate-500 shrink-0">📄</span>
        <span><code>${a}</code></span>
      </div>
    `).join('');
  }

  // Render Archivos Despues
  const despuesCont = document.getElementById('modal-archivos-despues');
  if (despuesCont) {
    despuesCont.innerHTML = data.archivosDespues.map(d => `
      <div class="text-slate-300 flex items-start gap-1.5">
        <span class="shrink-0">${d.icon}</span>
        <span><code>${d.path}</code> <span class="text-slate-400 font-sans text-[10px]">${d.note}</span></span>
      </div>
    `).join('');
  }

  // Render Comando
  const cmdLbl = document.getElementById('modal-comando-label');
  const cmdCode = document.getElementById('modal-comando-code');
  if (cmdLbl) cmdLbl.innerHTML = `<span>💻</span> ${data.comandoLabel}`;
  if (cmdCode) cmdCode.innerText = data.comando;

  // Mantener pestaña actual
  cambiarTabModal(tabActualModal);
}

function copiarComandoModal() {
  if (typeof DETALLES_PUNTOS === 'undefined') return;
  const data = DETALLES_PUNTOS[puntoActualModal];
  if (data && data.comando) {
    navigator.clipboard.writeText(data.comando).then(() => {
      const btn = document.getElementById('modal-copiar-btn');
      if (btn) {
        const original = btn.innerHTML;
        btn.innerHTML = '<span>✔</span> ¡Copiado!';
        btn.classList.add('text-emerald-400');
        setTimeout(() => {
          btn.innerHTML = original;
          btn.classList.remove('text-emerald-400');
        }, 1800);
      }
    });
  }
}

// Atajos de teclado: Esc para cerrar, Flechas para navegar
document.addEventListener('keydown', (e) => {
  const modal = document.getElementById('modal-detalle');
  if (modal && !modal.classList.contains('hidden')) {
    if (e.key === 'Escape') {
      cerrarModal();
    } else if (e.key === 'ArrowLeft') {
      navegarModal(-1);
    } else if (e.key === 'ArrowRight') {
      navegarModal(1);
    }
  }
});
