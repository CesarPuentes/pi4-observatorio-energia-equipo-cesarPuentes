/**
 * Funciones de interacción rápida y simulador en vivo de contratos Pandera.
 */
function copiarComando(texto) {
  navigator.clipboard.writeText(texto).then(() => {
    alert('Comando copiado al portapapeles: ' + texto);
  });
}

function probarPandera(tipo) {
  const p = document.getElementById('pantalla-pandera');
  if (!p) return;
  if (tipo === 'malo') {
    p.innerHTML = `
      <div class="text-rose-400 font-bold">❌ SchemaErrors detectado por Pandera (3 violaciones de contrato):</div>
      <div class="text-slate-300 mt-1 pl-2 border-l-2 border-rose-500 space-y-1">
        <div>1. columna 'divipola': valor <span class="text-rose-400 font-bold">'9999999'</span> no cumple regex <span class="text-cyan-300">'^\\d{5}$'</span> (debe tener 5 dígitos).</div>
        <div>2. columna 'tipo_compra': valor <span class="text-rose-400 font-bold">'ModalidadInventada'</span> no está en <span class="text-cyan-300">['Bolsa', 'Contrato']</span>.</div>
        <div>3. columna 'energia_kwh': valor <span class="text-rose-400 font-bold">-250.0</span> viola restricción <span class="text-cyan-300">greater_than_or_equal_to(0)</span>.</div>
      </div>
      <div class="text-amber-400 mt-2">➔ ¡La tabla corrupta es rechazada de inmediato y no toca la Capa Plata!</div>
    `;
  } else {
    p.innerHTML = `
      <div class="text-emerald-400 font-bold">✔ Validación con Pandera: OK (ESQUEMA_VENTAS exitoso)</div>
      <div class="text-slate-300 mt-1 pl-2 border-l-2 border-emerald-500 space-y-1">
        <div>• periodo: '2024-03' (formato YYYY-MM válido)</div>
        <div>• divipola: '05001' (5 dígitos, municipio Medellín)</div>
        <div>• tipo_compra: 'Bolsa' | segmento: 'Residencial'</div>
        <div>• energia_kwh: 125,400.0 &gt; 0 | valor_cop: 125,000,000.0 | clientes: 1,200</div>
      </div>
      <div class="text-emerald-300 mt-2">➔ Tabla aprobada para guardarse en <code class="text-cyan-300">data/silver/enerandes_ventas.parquet</code>.</div>
    `;
  }
}
