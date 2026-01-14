(function () {
    const API = (window.API_URL || (location.origin.replace(/:\d+$/, ':8000')));
    const btn = document.getElementById('btn');
    const img = document.getElementById('plot');
    const tInput = document.getElementById('tIndex');


    btn.addEventListener('click', async () => {
        const t = Math.max(0, parseInt(tInput.value || '0', 10));
        const url = `${API}/plot?t=${t}&_=${Date.now()}`; // cache buster
        try {
            btn.disabled = true;
            img.alt = 'Loading…';
            // You can also just set img.src = url; this preflight catches errors
            const res = await fetch(url);
            if (!res.ok) throw new Error(`Backend returned ${res.status}`);
            const blob = await res.blob();
            img.src = URL.createObjectURL(blob);
            img.alt = `VAR_2T t=${t}`;
        } catch (e) {
            alert(e.message || 'Failed to fetch plot');
        } finally {
            btn.disabled = false;
        }
    });
})();