import { useState } from 'react'
import './App.css'

// Change this to your actual Vercel backend URL
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://arabic-morfologi-backend.vercel.app' 
  : 'http://localhost:5000'

function App() {
  const [arabicText, setArabicText] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [tasrif, setTasrif] = useState(null)
  const [activeDropdown, setActiveDropdown] = useState(null)

  const fetchTasrif = async (root, mode) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasrif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ root, mode })
      })
      const data = await response.json()
      if (data.success) {
        setTasrif({ mode, data: data.tasrif, root })
        setActiveDropdown(null)
      }
    } catch (err) {
      console.error("Error fetching tasrif:", err)
      setError('خطأ في جلب التصريف')
    }
  }

  const analyzeText = async () => {
    if (!arabicText.trim()) {
      setError('يرجى إدخال نص عربي للتحليل')
      return
    }

    setLoading(true)
    setError('')
    setAnalysis(null)

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: arabicText })
      })

      const data = await response.json()

      if (data.success) {
        setAnalysis(data.result)
      } else {
        setError(data.message || 'حدث خطأ في التحليل')
      }
    } catch (err) {
      setError('فشل في الاتصال بالخادم')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const clearAll = () => {
    setArabicText('')
    setAnalysis(null)
    setError('')
    setTasrif(null)
    setActiveDropdown(null)
  }

  const toggleDropdown = (index) => {
    setActiveDropdown(activeDropdown === index ? null : index)
  }

  const getTasrifTitle = (mode) => {
    switch (mode) {
      case 'istilahi':
        return '📘 التصريف الاصطلاحي'
      case 'lughowiy':
        return '📗 التصريف اللغوي'
      case 'isim':
        return '📚 تصريف الأسماء'
      default:
        return 'التصريف'
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h2>تحليل المورفولوجي العربي</h2>
        <p className="subtitle">Arabic Morphological Analysis</p>
      </header>

      <main className="main-content">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="arabicInput">أدخل النص العربي:</label>
            <textarea
              id="arabicInput"
              value={arabicText}
              onChange={(e) => setArabicText(e.target.value)}
              placeholder="اكتب أو الصق النص العربي هنا..."
              rows={4}
              dir="rtl"
              className="arabic-input"
            />
          </div>

          <div className="button-group">
            <button
              onClick={analyzeText}
              disabled={loading}
              className="analyze-btn"
            >
              {loading ? 'جاري التحليل...' : 'تحليل النص'}
            </button>
            <button
              onClick={clearAll}
              className="clear-btn"
            >
              مسح الكل
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>جاري تحليل النص باستخدام الذكاء الاصطناعي...</p>
          </div>
        )}

        {analysis && (
          <div className="analysis-results">
            <h2>نتائج التحليل</h2>

            {analysis.summary && (
              <div className="summary-section">
                <h3>الملخص العام</h3>
                <p dir="rtl">{analysis.summary}</p>
              </div>
            )}

            {analysis.analysis && analysis.analysis.length > 0 ? (
              <div className="words-analysis">
                <h3>تحليل الكلمات</h3>
                <div className="words-grid">
                  {analysis.analysis.map((word, index) => (
                    <div key={index} className="word-card">
                      <div className="word-header">
                        <h4 dir="rtl">{word.word}</h4>
                      </div>

                      <div className="word-details">
                        {word.root && (
                          <div className="detail-item">
                            <span className="label">الجذر:</span>
                            <span className="value" dir="rtl">{word.root}</span>
                          </div>
                        )}

                        {word.extra_letters && word.extra_letters.length > 0 && (
                          <div className="detail-item">
                            <span className="label">حرف الزيادة:</span>
                            <span className="value" dir="rtl">
                              {Array.isArray(word.extra_letters)
                                ? word.extra_letters.join('، ')
                                : word.extra_letters}
                            </span>
                          </div>
                        )}

                        {word.pattern && (
                          <div className="detail-item">
                            <span className="label">الوزن:</span>
                            <span className="value" dir="rtl">{word.pattern}</span>
                          </div>
                        )}

                        {word.type && (
                          <div className="detail-item">
                            <span className="label">النوع:</span>
                            <span className="value" dir="rtl">{word.type}</span>
                          </div>
                        )}

                        {word.tense && (
                          <div className="detail-item">
                            <span className="label">الزمن:</span>
                            <span className="value" dir="rtl">{word.tense}</span>
                          </div>
                        )}

                        {word.meaning_arabic && (
                          <div className="detail-item">
                            <span className="label">المعنى:</span>
                            <span className="value" dir="rtl">{word.meaning_arabic}</span>
                          </div>
                        )}

                        {word.meaning_english && (
                          <div className="detail-item">
                            <span className="label">English:</span>
                            <span className="value">{word.meaning_english}</span>
                          </div>
                        )}

                        {word.related_words && word.related_words.length > 0 && (
                          <div className="detail-item">
                            <span className="label">كلمة مشتقة:</span>
                            <span className="value" dir="rtl">
                              {word.related_words[0]}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="tasrif-dropdown">
                        <button
                          className="tasrif-main-btn"
                          onClick={() => toggleDropdown(index)}
                        >
                          <span>التصريف</span>
                          <span className={`dropdown-arrow ${activeDropdown === index ? 'open' : ''}`}>
                            ▼
                          </span>
                        </button>

                        {activeDropdown === index && (
                          <div className="dropdown-menu">
                            <button
                              className="dropdown-item"
                              onClick={() => fetchTasrif(word.root, "istilahi")}
                            >
                              📘 التصريف الاصطلاحي
                            </button>
                            <button
                              className="dropdown-item"
                              onClick={() => fetchTasrif(word.root, "lughowiy")}
                            >
                              📗 التصريف اللغوي
                            </button>
                            <button
                              className="dropdown-item"
                              onClick={() => fetchTasrif(word.root, "isim")}
                            >
                              📚 تصريف الأسماء
                            </button>
                          </div>
                        )}
                      </div>

                      {tasrif && tasrif.root === word.root && (
                        <div className="tasrif-result">
                          <h5 dir="rtl">{getTasrifTitle(tasrif.mode)}</h5>
                          <div className="tasrif-content" dir="rtl">
                            {Array.isArray(tasrif.data) ? (
                              <ul>
                                {tasrif.data.map(([key, val], idx) => (
                                  <li key={idx}>
                                    <strong>{key}:</strong> {val}
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <div>
                                {Object.entries(tasrif.data).map(([key, val], idx) => (
                                  <p key={idx}>
                                    <strong>{key}:</strong> {val}
                                  </p>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      <br />
                      <br />
                      <br />
                      <br />
                      <br />                                                                          
                    </div>
                  ))}
                </div>
              </div>
            ) : analysis.raw_response ? (
              <div className="raw-response">
                <h3>الاستجابة الخام</h3>
                <pre dir="rtl">{analysis.raw_response}</pre>
              </div>
            ) : null}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Universitas Darussalam Gontor</p>
      </footer>
    </div>
  )
}

export default App
