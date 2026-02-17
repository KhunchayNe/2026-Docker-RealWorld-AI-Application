import { useState } from 'react'
import './App.css'

const API_BASE = '/api'

type ApiResponse = {
  status?: string
  message?: string
  [key: string]: any
}

function App() {
  const [fuelType, setFuelType] = useState('diesel')
  const [horizon, setHorizon] = useState(7)
  const [searchPrice, setSearchPrice] = useState('32.5')
  const [searchLimit, setSearchLimit] = useState(5)
  const [csvUrl, setCsvUrl] = useState('https://catalog.eppo.go.th/dataset/b15f2fe3-14f0-4de5-b90e-2a5b63b4e717/resource/7d56918d-adbf-42b7-bd36-e4b33d425027/download/dataset_11_86.csv')
  const [retrain, setRetrain] = useState(true)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [result, setResult] = useState<ApiResponse | null>(null)
  const [error, setError] = useState('')
  const [priceDate, setPriceDate] = useState(new Date().toISOString().split('T')[0])
  const [dieselPrice, setDieselPrice] = useState('')
  const [gasohol95Price, setGasohol95Price] = useState('')
  const [gasohol91Price, setGasohol91Price] = useState('')
  const [gasoholE20Price, setGasoholE20Price] = useState('')
  const [dieselB7Price, setDieselB7Price] = useState('')
  const [lpgPrice, setLpgPrice] = useState('')

  const apiCall = async (endpoint: string, method = 'GET', body?: any) => {
    setLoading(true)
    setError('')
    setSuccess('')
    setResult(null)

    try {
      const options: RequestInit = { method }
      if (body) {
        options.headers = { 'Content-Type': 'application/json' }
        options.body = JSON.stringify(body)
      }

      const response = await fetch(`${API_BASE}${endpoint}`, options)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'API Error' }))
        throw new Error(errorData.detail || errorData.message || 'API Error')
      }

      const data: ApiResponse = await response.json()
      setResult(data)

      // Set success message based on response
      if (data.status === 'success' || data.status === 'trained' || response.ok) {
        const messages = {
          '/generate-sample-data': `✅ Generated ${data.records_added || 'sample'} data records`,
          '/train': `✅ Model trained for ${fuelType} with ${data.samples || 'N/A'} samples`,
          '/predict': `✅ Prediction generated for ${data.fuel_type || fuelType}`,
          '/prices/latest': '✅ Latest prices retrieved',
          '/prices': '✅ Price entry added successfully',
          '/upload-csv-url': `✅ CSV uploaded successfully`,
          '/': '✅ API is healthy'
        }

        const key = Object.keys(messages).find(k => endpoint.includes(k.replace('/generate-sample-data', '/generate-sample-data')))
        setSuccess(messages[key as keyof typeof messages] || '✅ Operation completed successfully')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>🛢️ Oil Price Predictor</h1>

      <div className="sections">
        <section className="card">
          <h2>1. Generate Sample Data</h2>
          <button onClick={() => apiCall('/generate-sample-data', 'POST')}>
            Generate Sample Data
          </button>
        </section>

        <section className="card">
          <h2>2. Train Model</h2>
          <div className="form-group">
            <label>Fuel Type:</label>
            <select value={fuelType} onChange={(e) => setFuelType(e.target.value)}>
              <option value="diesel">Diesel</option>
              <option value="gasohol_95">Gasohol 95</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="gasohol_e20">Gasohol E20</option>
              <option value="gasohol_e85">Gasohol E85</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="diesel_b7">Diesel B7</option>
              <option value="lpg">LPG</option>
            </select>
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={retrain}
                onChange={(e) => setRetrain(e.target.checked)}
              />
              Retrain Model
            </label>
          </div>
          <button onClick={() => apiCall('/train', 'POST', { fuel_type: fuelType, retrain })}>
            Train Model
          </button>
        </section>

        <section className="card">
          <h2>3. Predict Prices</h2>
          <div className="form-group">
            <label>Fuel Type:</label>
            <select value={fuelType} onChange={(e) => setFuelType(e.target.value)}>
              <option value="diesel">Diesel</option>
              <option value="gasohol_95">Gasohol 95</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="gasohol_e20">Gasohol E20</option>
              <option value="gasohol_e85">Gasohol E85</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="diesel_b7">Diesel B7</option>
              <option value="lpg">LPG</option>
            </select>
          </div>
          <div className="form-group">
            <label>Horizon (days):</label>
            <input
              type="number"
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              min="1"
              max="30"
            />
          </div>
          <button onClick={() => apiCall('/predict', 'POST', { fuel_type: fuelType, horizon })}>
            Predict Prices
          </button>
        </section>

        <section className="card">
          <h2>4. Search Similar Prices</h2>
          <div className="form-group">
            <label>Price:</label>
            <input
              type="number"
              step="0.01"
              value={searchPrice}
              onChange={(e) => setSearchPrice(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Fuel Type:</label>
            <select value={fuelType} onChange={(e) => setFuelType(e.target.value)}>
              <option value="diesel">Diesel</option>
              <option value="gasohol_95">Gasohol 95</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="gasohol_e20">Gasohol E20</option>
              <option value="gasohol_e85">Gasohol E85</option>
              <option value="gasohol_91">Gasohol 91</option>
              <option value="diesel_b7">Diesel B7</option>
              <option value="lpg">LPG</option>
            </select>
          </div>
          <div className="form-group">
            <label>Limit:</label>
            <input
              type="number"
              value={searchLimit}
              onChange={(e) => setSearchLimit(Number(e.target.value))}
              min="1"
              max="50"
            />
          </div>
          <button onClick={() => apiCall(`/search?price=${searchPrice}&fuel_type=${fuelType}&limit=${searchLimit}`)}>
            Search
          </button>
        </section>

        <section className="card">
          <h2>5. Add Price Entry</h2>
          <div className="form-group">
            <label>Date:</label>
            <input
              type="date"
              value={priceDate}
              onChange={(e) => setPriceDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Diesel Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="32.50"
              value={dieselPrice}
              onChange={(e) => setDieselPrice(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Gasohol 95 Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="42.80"
              value={gasohol95Price}
              onChange={(e) => setGasohol95Price(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Gasohol 91 Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="40.50"
              value={gasohol91Price}
              onChange={(e) => setGasohol91Price(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Gasohol E20 Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="39.20"
              value={gasoholE20Price}
              onChange={(e) => setGasoholE20Price(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Diesel B7 Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="33.00"
              value={dieselB7Price}
              onChange={(e) => setDieselB7Price(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>LPG Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="21.50"
              value={lpgPrice}
              onChange={(e) => setLpgPrice(e.target.value)}
            />
          </div>
          <button onClick={() => {
            if (!dieselPrice && !gasohol95Price && !gasohol91Price && !gasoholE20Price && !dieselB7Price && !lpgPrice) {
              setError('Please enter at least one fuel price')
              return
            }

            if (!priceDate) {
              setError('Please select a date')
              return
            }

            const data: any = {
              date: priceDate
            }
            if (dieselPrice) data.diesel = parseFloat(dieselPrice)
            if (gasohol95Price) data.gasohol_95 = parseFloat(gasohol95Price)
            if (gasohol91Price) data.gasohol_91 = parseFloat(gasohol91Price)
            if (gasoholE20Price) data.gasohol_e20 = parseFloat(gasoholE20Price)
            if (dieselB7Price) data.diesel_b7 = parseFloat(dieselB7Price)
            if (lpgPrice) data.lpg = parseFloat(lpgPrice)

            apiCall('/prices', 'POST', data).then(() => {
              // Clear form on success
              setDieselPrice('')
              setGasohol95Price('')
              setGasohol91Price('')
              setGasoholE20Price('')
              setDieselB7Price('')
              setLpgPrice('')
            })
          }}>
            Add Price
          </button>
        </section>

        <section className="card">
          <h2>6. Get Latest Prices</h2>
          <button onClick={() => apiCall('/prices/latest')}>
            Get Latest Prices
          </button>
        </section>

        <section className="card">
          <h2>7. Upload Data from EPPO</h2>
          <div className="form-group">
            <label>CSV URL:</label>
            <input
              type="text"
              value={csvUrl}
              onChange={(e) => setCsvUrl(e.target.value)}
              style={{ width: '100%', fontSize: '12px' }}
            />
          </div>
          <button onClick={() => apiCall('/upload-csv-url?url=' + encodeURIComponent(csvUrl), 'POST')}>
            Load from EPPO
          </button>
        </section>

        <section className="card">
          <h2>8. Health Check</h2>
          <button onClick={() => apiCall('/')}>
            Check API Health
          </button>
        </section>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing request...</p>
        </div>
      )}

      {success && (
        <div className="success">
          <p>{success}</p>
        </div>
      )}

      {error && (
        <div className="error">
          <h3>❌ Error:</h3>
          <pre>{error}</pre>
        </div>
      )}

      {result && (
        <div className="result">
          <h3>📊 Response Data:</h3>
          {result.predictions && Array.isArray(result.predictions) ? (
            <div className="predictions">
              <p><strong>Current Price:</strong> ฿{result.current_price}</p>
              <p><strong>Fuel Type:</strong> {result.fuel_type}</p>
              <h4>Predictions:</h4>
              <table className="prediction-table">
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Date</th>
                    <th>Predicted Price</th>
                    <th>Range</th>
                  </tr>
                </thead>
                <tbody>
                  {result.predictions.map((p: any) => (
                    <tr key={p.day}>
                      <td>{p.day}</td>
                      <td>{p.date}</td>
                      <td>฿{p.predicted_price.toFixed(2)}</td>
                      <td>฿{p.lower_bound.toFixed(2)} - ฿{p.upper_bound.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : result.latest_prices ? (
            <div className="latest-prices">
              <h4>Latest Prices:</h4>
              {Object.entries(result.latest_prices).map(([fuel, data]: [string, any]) => (
                <div key={fuel} className="price-item">
                  <strong>{fuel}:</strong> ฿{data.price} <span className="date">({data.date})</span>
                </div>
              ))}
            </div>
          ) : result.similar_dates ? (
            <div className="similar-dates">
              <h4>Similar Prices:</h4>
              {result.similar_dates.map((d: any, idx: number) => (
                <div key={idx} className="price-item">
                  <strong>{d.date}:</strong> ฿{d.price}
                  <span className="similarity"> (similarity: {(d.similarity_score * 100).toFixed(1)}%)</span>
                </div>
              ))}
            </div>
          ) : (
            <pre>{JSON.stringify(result, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  )
}

export default App
