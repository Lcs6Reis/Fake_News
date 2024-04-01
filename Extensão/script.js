// Função para enviar o texto da notícia para o servidor Flask
function sendNewsTextToServer(newsText) {
  fetch('http://localhost:5000/detect-fake-news', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ news_text: newsText }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Erro ao detectar fake news:', data.error);
      return;
    }
    const fakeProbability = data.fake_probability;
    const confidencePercentage = (fakeProbability * 100).toFixed(2);
    if (fakeProbability >= 0.5) {
      alert(`Esta notícia parece ser falsa com ${confidencePercentage}% de confiança.`);
    } else {
      alert(`Esta notícia parece ser verdadeira com ${(100 - confidencePercentage).toFixed(2)}% de confiança.`);
    }
  })
  .catch(error => {
    console.error('Erro ao enviar texto da notícia para o servidor:', error);
  });
}

// Função principal para configurar a extensão
function setupExtension() {
  const analyzeButton = document.getElementById('analyze-button');

  analyzeButton.addEventListener('click', function() {
    const newsText = document.getElementById('news-text').value;
    sendNewsTextToServer(newsText);
  });
}

// Executa a função principal quando a página terminar de carregar
window.addEventListener('load', function() {
  setupExtension(); // Chama a função setupExtension após o carregamento completo da página
});
