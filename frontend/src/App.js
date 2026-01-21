import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const API_BASE = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

const STATE_LABELS = {
  stress: 'Стрес', sleep: 'Сон', energy: 'Енергія',
  focus: 'Фокус', immunity: 'Імунітет', recovery: 'Відновлення'
};

const LIFESTYLE_LABELS = {
  high_achiever: 'High Achievers', creative_professional: 'Креативні',
  biohacker: 'Біохакери', wellness_enthusiast: 'Wellness',
  fitness_focused: 'Фітнес', holistic_believer: 'Холістики',
  conscious_consumer: 'Свідомі споживачі', skeptic: 'Скептики'
};

function App() {
  const [hypothesis, setHypothesis] = useState('');
  const [questionType, setQuestionType] = useState('scale');
  const [options, setOptions] = useState(['Варіант A', 'Варіант B', 'Варіант C']);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [segments, setSegments] = useState({ state: [], lifestyle: [], city: [] });
  const [activeTab, setActiveTab] = useState('hypothesis');
  const [personasCount, setPersonasCount] = useState(0);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then(r => r.json())
      .then(d => setPersonasCount(d.personas))
      .catch(e => console.error('API not available:', e));
    
    fetch(`${API_BASE}/api/results`)
      .then(r => r.json())
      .then(d => setHistory(d.results || []))
      .catch(() => {});
  }, []);

  const runTest = useCallback(async () => {
    if (!hypothesis.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hypothesis,
          question_type: questionType,
          options: questionType === 'choice' ? options.filter(o => o.trim()) : null,
          segments: {
            state: segments.state.length > 0 ? segments.state : null,
            lifestyle: segments.lifestyle.length > 0 ? segments.lifestyle : null,
            city: segments.city.length > 0 ? segments.city : null
          }
        })
      });
      
      if (!response.ok) throw new Error('API error');
      
      const data = await response.json();
      setResults(data.results);
      setHistory(prev => [data, ...prev]);
      setActiveTab('results');
    } catch (e) {
      setError('Помилка з\'єднання з сервером. Перевірте, чи запущений backend.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [hypothesis, questionType, options, segments]);

  const toggleSegment = (type, value) => {
    setSegments(prev => ({
      ...prev,
      [type]: prev[type].includes(value) 
        ? prev[type].filter(v => v !== value)
        : [...prev[type], value]
    }));
  };

  const generateSummary = () => {
    if (!results || results.type !== 'scale') return '';
    
    const avg = parseFloat(results.average);
    let sentiment = avg >= 7 ? 'позитивне' : avg >= 5 ? 'нейтральне' : 'негативне';
    
    const sortedStates = [...results.by_state].sort((a, b) => b.avg - a.avg);
    const topState = sortedStates[0];
    const bottomState = sortedStates[sortedStates.length - 1];
    
    return `
**Загальний результат:** ${results.average}/10 (${sentiment} сприйняття)

**Розподіл:**
• Позитивні (7-10): ${results.positive} осіб (${Math.round(results.positive / results.total * 100)}%)
• Нейтральні (4-6): ${results.neutral} осіб (${Math.round(results.neutral / results.total * 100)}%)  
• Негативні (1-3): ${results.negative} осіб (${Math.round(results.negative / results.total * 100)}%)

**Найбільш зацікавлені:** ${STATE_LABELS[topState?.state] || topState?.state} (${topState?.avg}/10)
**Найменш зацікавлені:** ${STATE_LABELS[bottomState?.state] || bottomState?.state} (${bottomState?.avg}/10)

**Рекомендація:** ${avg >= 6 
  ? '✅ Гіпотеза має потенціал. Рекомендується A/B тест на реальній аудиторії.' 
  : '⚠️ Потребує доопрацювання. Зверніть увагу на сегменти з низькими оцінками.'}
    `.trim();
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #064e3b 100%)',
      fontFamily: "'Inter', -apple-system, sans-serif"
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 16px' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h1 style={{ 
            fontSize: '2.5rem', fontWeight: 700, color: '#fff', marginBottom: '8px',
            background: 'linear-gradient(90deg, #fff, #10b981)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
          }}>
            Synthetic Focus Group
          </h1>
          <p style={{ color: '#10b981', fontSize: '1.1rem' }}>
            HUMANIST • {personasCount || 50} персон на основі реальних даних GA4
          </p>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '32px' }}>
          {[
            { id: 'hypothesis', icon: '📝', label: 'Гіпотеза' },
            { id: 'segments', icon: '👥', label: 'Сегменти' },
            { id: 'results', icon: '📊', label: 'Результати' },
            { id: 'history', icon: '📋', label: 'Історія' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '12px 24px',
                borderRadius: '12px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: 500,
                fontSize: '0.95rem',
                transition: 'all 0.2s',
                background: activeTab === tab.id ? '#10b981' : 'rgba(51, 65, 85, 0.5)',
                color: activeTab === tab.id ? '#fff' : '#94a3b8',
                boxShadow: activeTab === tab.id ? '0 4px 20px rgba(16, 185, 129, 0.3)' : 'none'
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '24px',
            color: '#fca5a5'
          }}>
            {error}
          </div>
        )}

        {/* Hypothesis Tab */}
        {activeTab === 'hypothesis' && (
          <div style={{
            background: 'rgba(30, 41, 59, 0.5)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            padding: '32px',
            border: '1px solid rgba(51, 65, 85, 0.5)'
          }}>
            <h2 style={{ color: '#fff', marginBottom: '24px', fontSize: '1.25rem' }}>
              Створіть тест гіпотези
            </h2>
            
            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', color: '#94a3b8', marginBottom: '8px' }}>
                Гіпотеза / Питання
              </label>
              <textarea
                value={hypothesis}
                onChange={e => setHypothesis(e.target.value)}
                placeholder="Наприклад: Наскільки вам цікава підписка на CBD продукти зі знижкою 15%?"
                style={{
                  width: '100%',
                  height: '120px',
                  padding: '16px',
                  background: 'rgba(15, 23, 42, 0.5)',
                  border: '1px solid #334155',
                  borderRadius: '12px',
                  color: '#fff',
                  fontSize: '1rem',
                  resize: 'vertical',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
              <div>
                <label style={{ display: 'block', color: '#94a3b8', marginBottom: '8px' }}>
                  Тип питання
                </label>
                <select
                  value={questionType}
                  onChange={e => setQuestionType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: 'rgba(15, 23, 42, 0.5)',
                    border: '1px solid #334155',
                    borderRadius: '12px',
                    color: '#fff',
                    fontSize: '1rem',
                    outline: 'none'
                  }}
                >
                  <option value="scale">Шкала 1-10</option>
                  <option value="choice">Вибір варіанту</option>
                </select>
              </div>

              {questionType === 'choice' && (
                <div>
                  <label style={{ display: 'block', color: '#94a3b8', marginBottom: '8px' }}>
                    Варіанти
                  </label>
                  {options.map((opt, i) => (
                    <input
                      key={i}
                      value={opt}
                      onChange={e => {
                        const newOpts = [...options];
                        newOpts[i] = e.target.value;
                        setOptions(newOpts);
                      }}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        marginBottom: '8px',
                        background: 'rgba(15, 23, 42, 0.5)',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '0.9rem',
                        outline: 'none'
                      }}
                    />
                  ))}
                  <button
                    onClick={() => setOptions([...options, `Варіант ${String.fromCharCode(65 + options.length)}`])}
                    style={{
                      padding: '6px 12px',
                      background: 'transparent',
                      border: '1px dashed #334155',
                      borderRadius: '6px',
                      color: '#64748b',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}
                  >
                    + Додати варіант
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={runTest}
              disabled={!hypothesis.trim() || isLoading}
              style={{
                width: '100%',
                padding: '16px',
                background: isLoading ? '#334155' : 'linear-gradient(90deg, #10b981, #14b8a6)',
                border: 'none',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '1rem',
                fontWeight: 600,
                cursor: hypothesis.trim() && !isLoading ? 'pointer' : 'not-allowed',
                opacity: hypothesis.trim() ? 1 : 0.5,
                transition: 'all 0.2s'
              }}
            >
              {isLoading ? '⏳ Опитування персон...' : '🚀 Запустити тест'}
            </button>
          </div>
        )}

        {/* Segments Tab */}
        {activeTab === 'segments' && (
          <div style={{
            background: 'rgba(30, 41, 59, 0.5)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            padding: '32px',
            border: '1px solid rgba(51, 65, 85, 0.5)'
          }}>
            <h2 style={{ color: '#fff', marginBottom: '24px' }}>Фільтр за сегментами</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
              <div>
                <h3 style={{ color: '#10b981', marginBottom: '16px', fontSize: '1rem' }}>
                  За станом (STATE)
                </h3>
                {Object.entries(STATE_LABELS).map(([key, label]) => (
                  <label key={key} style={{ 
                    display: 'flex', alignItems: 'center', gap: '12px', 
                    marginBottom: '12px', cursor: 'pointer', color: '#cbd5e1'
                  }}>
                    <input
                      type="checkbox"
                      checked={segments.state.includes(key)}
                      onChange={() => toggleSegment('state', key)}
                      style={{ width: '18px', height: '18px', accentColor: '#10b981' }}
                    />
                    {label}
                  </label>
                ))}
              </div>
              
              <div>
                <h3 style={{ color: '#10b981', marginBottom: '16px', fontSize: '1rem' }}>
                  За стилем життя
                </h3>
                {Object.entries(LIFESTYLE_LABELS).map(([key, label]) => (
                  <label key={key} style={{ 
                    display: 'flex', alignItems: 'center', gap: '12px', 
                    marginBottom: '12px', cursor: 'pointer', color: '#cbd5e1'
                  }}>
                    <input
                      type="checkbox"
                      checked={segments.lifestyle.includes(key)}
                      onChange={() => toggleSegment('lifestyle', key)}
                      style={{ width: '18px', height: '18px', accentColor: '#10b981' }}
                    />
                    {label}
                  </label>
                ))}
              </div>
            </div>

            <div style={{
              marginTop: '24px',
              padding: '16px',
              background: 'rgba(15, 23, 42, 0.5)',
              borderRadius: '12px'
            }}>
              <p style={{ color: '#64748b' }}>
                <span style={{ color: '#10b981', fontWeight: 500 }}>
                  {segments.state.length === 0 && segments.lifestyle.length === 0
                    ? 'Обрано всіх персон'
                    : `Фільтри: ${[
                        ...segments.state.map(s => STATE_LABELS[s]),
                        ...segments.lifestyle.map(l => LIFESTYLE_LABELS[l])
                      ].join(', ')}`
                  }
                </span>
              </p>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div>
            {!results ? (
              <div style={{
                background: 'rgba(30, 41, 59, 0.5)',
                borderRadius: '16px',
                padding: '64px',
                textAlign: 'center',
                border: '1px solid rgba(51, 65, 85, 0.5)'
              }}>
                <p style={{ color: '#64748b', fontSize: '1.1rem' }}>
                  Запустіть тест, щоб побачити результати
                </p>
              </div>
            ) : (
              <>
                {/* Summary Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
                  <div style={{
                    background: 'rgba(30, 41, 59, 0.5)',
                    borderRadius: '12px',
                    padding: '20px',
                    border: '1px solid rgba(51, 65, 85, 0.5)'
                  }}>
                    <p style={{ color: '#64748b', fontSize: '0.85rem' }}>Всього</p>
                    <p style={{ color: '#fff', fontSize: '2rem', fontWeight: 700 }}>{results.total}</p>
                  </div>
                  
                  {results.type === 'scale' && (
                    <>
                      <div style={{
                        background: 'rgba(16, 185, 129, 0.1)',
                        borderRadius: '12px',
                        padding: '20px',
                        border: '1px solid rgba(16, 185, 129, 0.3)'
                      }}>
                        <p style={{ color: '#10b981', fontSize: '0.85rem' }}>Середня</p>
                        <p style={{ color: '#10b981', fontSize: '2rem', fontWeight: 700 }}>{results.average}/10</p>
                      </div>
                      <div style={{
                        background: 'rgba(34, 197, 94, 0.1)',
                        borderRadius: '12px',
                        padding: '20px',
                        border: '1px solid rgba(34, 197, 94, 0.3)'
                      }}>
                        <p style={{ color: '#22c55e', fontSize: '0.85rem' }}>Позитивні (7+)</p>
                        <p style={{ color: '#22c55e', fontSize: '2rem', fontWeight: 700 }}>
                          {Math.round(results.positive / results.total * 100)}%
                        </p>
                      </div>
                      <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        borderRadius: '12px',
                        padding: '20px',
                        border: '1px solid rgba(239, 68, 68, 0.3)'
                      }}>
                        <p style={{ color: '#ef4444', fontSize: '0.85rem' }}>Негативні (1-3)</p>
                        <p style={{ color: '#ef4444', fontSize: '2rem', fontWeight: 700 }}>
                          {Math.round(results.negative / results.total * 100)}%
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* Charts */}
                {results.type === 'scale' && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                    <div style={{
                      background: 'rgba(30, 41, 59, 0.5)',
                      borderRadius: '16px',
                      padding: '24px',
                      border: '1px solid rgba(51, 65, 85, 0.5)'
                    }}>
                      <h3 style={{ color: '#fff', marginBottom: '16px' }}>Розподіл оцінок</h3>
                      <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={results.distribution}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                          <XAxis dataKey="score" stroke="#94a3b8" />
                          <YAxis stroke="#94a3b8" />
                          <Tooltip 
                            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                            labelStyle={{ color: '#fff' }}
                          />
                          <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    <div style={{
                      background: 'rgba(30, 41, 59, 0.5)',
                      borderRadius: '16px',
                      padding: '24px',
                      border: '1px solid rgba(51, 65, 85, 0.5)'
                    }}>
                      <h3 style={{ color: '#fff', marginBottom: '16px' }}>За сегментами</h3>
                      <ResponsiveContainer width="100%" height={280}>
                        <BarChart 
                          data={results.by_state.map(s => ({ ...s, label: STATE_LABELS[s.state] || s.state }))} 
                          layout="vertical"
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                          <XAxis type="number" domain={[0, 10]} stroke="#94a3b8" />
                          <YAxis dataKey="label" type="category" stroke="#94a3b8" width={80} />
                          <Tooltip 
                            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                          />
                          <Bar dataKey="avg" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {results.type === 'choice' && (
                  <div style={{
                    background: 'rgba(30, 41, 59, 0.5)',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '24px',
                    border: '1px solid rgba(51, 65, 85, 0.5)'
                  }}>
                    <h3 style={{ color: '#fff', marginBottom: '16px' }}>Розподіл відповідей</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={results.choices}
                          dataKey="count"
                          nameKey="choice"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          label={({ choice, pct }) => `${choice}: ${pct}%`}
                        >
                          {results.choices.map((_, i) => (
                            <Cell key={i} fill={COLORS[i % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Summary */}
                <div style={{
                  background: 'rgba(30, 41, 59, 0.5)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid rgba(51, 65, 85, 0.5)'
                }}>
                  <h3 style={{ color: '#fff', marginBottom: '16px' }}>📋 Саммарі та рекомендації</h3>
                  <pre style={{ 
                    color: '#cbd5e1', 
                    whiteSpace: 'pre-wrap', 
                    fontFamily: 'inherit',
                    fontSize: '0.95rem',
                    lineHeight: 1.6
                  }}>
                    {generateSummary()}
                  </pre>
                </div>
              </>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div style={{
            background: 'rgba(30, 41, 59, 0.5)',
            borderRadius: '16px',
            padding: '32px',
            border: '1px solid rgba(51, 65, 85, 0.5)'
          }}>
            <h2 style={{ color: '#fff', marginBottom: '24px' }}>Історія тестів</h2>
            
            {history.length === 0 ? (
              <p style={{ color: '#64748b' }}>Поки немає збережених тестів</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {history.map((item, i) => (
                  <div 
                    key={i}
                    onClick={() => { setResults(item.results); setActiveTab('results'); }}
                    style={{
                      padding: '16px',
                      background: 'rgba(15, 23, 42, 0.5)',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      border: '1px solid transparent'
                    }}
                    onMouseEnter={e => e.target.style.borderColor = '#10b981'}
                    onMouseLeave={e => e.target.style.borderColor = 'transparent'}
                  >
                    <p style={{ color: '#fff', marginBottom: '4px' }}>{item.hypothesis}</p>
                    <p style={{ color: '#64748b', fontSize: '0.85rem' }}>
                      {item.created_at} • {item.results?.total || 0} відповідей
                      {item.results?.average && ` • Середня: ${item.results.average}/10`}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div style={{ textAlign: 'center', marginTop: '48px', color: '#475569', fontSize: '0.85rem' }}>
          <p>Synthetic Focus Group v1.0 • HUMANIST</p>
          <p style={{ marginTop: '4px' }}>50 персон • 64% Ж / 36% Ч • Дані GA4</p>
        </div>
      </div>
    </div>
  );
}

export default App;
