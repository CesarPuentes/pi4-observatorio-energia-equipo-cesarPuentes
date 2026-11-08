/**
 * Controlador interactivo para el Glosario de Ingeniería de Datos (Bronce · Plata · Oro).
 * Filtra por capa y por búsqueda de texto en tiempo real.
 */

let capaActivaGlosario = 'todos';

function seleccionarCapaGlosario(capa) {
  capaActivaGlosario = capa;
  
  // Actualizar estilos de los botones de filtro
  const botones = document.querySelectorAll('.btn-filtro-glosario');
  botones.forEach(btn => {
    if (btn.getAttribute('data-capa') === capa) {
      btn.className = 'btn-filtro-glosario px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500 text-slate-950 transition-all shadow-md cursor-pointer';
    } else {
      btn.className = 'btn-filtro-glosario px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all cursor-pointer';
    }
  });

  filtrarGlosario();
}

function filtrarGlosario() {
  const searchInput = document.getElementById('glosario-buscador');
  const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
  const tarjetas = document.querySelectorAll('.tarjeta-concepto');
  let visibles = 0;

  tarjetas.forEach(card => {
    const capaCard = card.getAttribute('data-capa');
    const textoCard = card.innerText.toLowerCase();

    const coincideCapa = (capaActivaGlosario === 'todos' || capaCard === capaActivaGlosario);
    const coincideTexto = (query === '' || textoCard.includes(query));

    if (coincideCapa && coincideTexto) {
      card.classList.remove('hidden');
      visibles++;
    } else {
      card.classList.add('hidden');
    }
  });

  // Contador de resultados
  const contadorEl = document.getElementById('glosario-contador');
  if (contadorEl) {
    contadorEl.innerText = `Mostrando ${visibles} de ${tarjetas.length} conceptos`;
  }

  // Mensaje si no hay resultados
  const vacioEl = document.getElementById('glosario-vacio');
  if (vacioEl) {
    if (visibles === 0) {
      vacioEl.classList.remove('hidden');
    } else {
      vacioEl.classList.add('hidden');
    }
  }
}
