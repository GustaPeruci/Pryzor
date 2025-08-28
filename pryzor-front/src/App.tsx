import { useState, useEffect } from 'react'
import './App.css'

// Tipos TypeScript para nossos dados (como interfaces em outras linguagens)
interface Game {
  id?: number;
  steam_id: string;
  name: string;
  current_price?: number;
  price?: number; // Fallback caso venha como 'price'
}

interface Prediction {
  game: string;
  current_price: number;
  predicted_price: number;
  trend_percent: number;
  recommendation: string;
}

function App() {
  // Estados para armazenar dados da API
  const [games, setGames] = useState<Game[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);

  // useEffect executa quando o componente carrega (como __init__ em Python)
  useEffect(() => {
    // Função para buscar dados da nossa API Flask
    const fetchData = async () => {
      try {
        console.log('🔄 Buscando dados da API...');
        
        // Buscar lista de jogos
        console.log('📡 Fazendo requisição para /api/games...');
        const gamesResponse = await fetch('http://127.0.0.1:5000/api/games');
        console.log('📡 Resposta games:', gamesResponse.status);
        const gamesData = await gamesResponse.json();
        console.log('📊 Dados games:', gamesData);
        
        // Buscar predições
        console.log('📡 Fazendo requisição para /api/predictions...');
        const predictionsResponse = await fetch('http://127.0.0.1:5000/api/predictions');
        console.log('📡 Resposta predictions:', predictionsResponse.status);
        const predictionsData = await predictionsResponse.json();
        console.log('📊 Dados predictions:', predictionsData);
        
        if (gamesData.success) {
          setGames(gamesData.data);
          console.log('✅ Games carregados:', gamesData.data.length);
        } else {
          console.error('❌ Erro nos dados de games:', gamesData);
        }
        
        if (predictionsData.success) {
          setPredictions(predictionsData.data);
          console.log('✅ Predictions carregadas:', predictionsData.data.length);
        } else {
          console.error('❌ Erro nos dados de predictions:', predictionsData);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('❌ Erro ao buscar dados:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []); // [] significa "execute apenas uma vez quando carregar"

  return (
    <div className="app">
      <header className="header">
        <h1>🎮 PRYZOR - Análise de Preços Steam</h1>
        <p>Dashboard de análise e predição de preços de jogos</p>
      </header>

      {loading ? (
        <div className="loading">
          <p>⏳ Carregando dados...</p>
        </div>
      ) : (
        <main className="main-content">
          {/* Seção de Estatísticas */}
          <section className="stats-section">
            <h2>📊 Estatísticas Gerais</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>🎯 Total de Jogos</h3>
                <p className="stat-number">{games.length}</p>
              </div>
              <div className="stat-card">
                <h3>🔮 Predições Ativas</h3>
                <p className="stat-number">{predictions.length}</p>
              </div>
            </div>
          </section>

          {/* Seção de Predições */}
          <section className="predictions-section">
            <h2>🔮 Predições de Preços (7 dias)</h2>
            <div className="predictions-grid">
              {predictions.slice(0, 6).map((pred, index) => (
                <div key={index} className="prediction-card">
                  <h4>{pred.game}</h4>
                  <p>💰 Atual: R$ {pred.current_price.toFixed(2)}</p>
                  <p>📈 Predito: R$ {pred.predicted_price.toFixed(2)}</p>
                  <p className={`trend ${pred.trend_percent < 0 ? 'negative' : 'positive'}`}>
                    📊 {pred.trend_percent > 0 ? '+' : ''}{pred.trend_percent}%
                  </p>
                  <p className="recommendation">🎯 {pred.recommendation}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Seção de Jogos */}
          <section className="games-section">
            <h2>🎮 Lista de Jogos Monitorados</h2>
            <div className="games-list">
              {games.map((game, index) => {
                // Determina o preço a ser exibido
                const price = game.current_price || game.price;
                const priceDisplay = price ? `R$ ${Number(price).toFixed(2)}` : 'Preço não disponível';
                
                return (
                  <div key={game.steam_id || index} className="game-item">
                    <h4>{game.name}</h4>
                    <p>💰 {priceDisplay}</p>
                  </div>
                );
              })}
            </div>
          </section>
        </main>
      )}
    </div>
  )
}

export default App
