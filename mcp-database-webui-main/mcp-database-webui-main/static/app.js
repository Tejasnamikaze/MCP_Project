document.getElementById('query-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const query = document.getElementById('query').value;
  const resultEl = document.getElementById('result');
  resultEl.textContent = 'Loading...';
  try {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    if (data.status === 'success') {
      resultEl.textContent = data.result;
    } else {
      resultEl.textContent = data.message || 'Error occurred.';
    }
  } catch (err) {
    resultEl.textContent = 'Network error.';
  }
}); 