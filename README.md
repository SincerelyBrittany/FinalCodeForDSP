# FinalCodeForDSP

# 🎵 Song Matcher

This is a full-stack web application that allows users to upload two CSV files — one from a writers database and another from YouTube — and matches songs based on partial title and artist matches. The results are then downloaded in a standardized CSV format.

---

## 🧱 Project Structure

FinalCodeForDSP/

- backend/ # FastAPI service that performs CSV matching logic
- frontend/ # React interface for file upload and download
- README.md # Master readme


## Backend Dependencies 
Inside backend/requirements.txt:
- fastapi
- uvicorn
- pandas
- python-multipart



## Running locally 

### backend 
1. Navigate to the backend directory
  ``cd backend``
2. Create a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend server
   ``uvicorn main:app --reload``


### frontend

1. Navigate to the frontend directory
  ``cd frontend``
2.  Create or edit a file named .env and add this line:
   ``VITE_API_URL=https://your-backend-name.onrender.com or http://localhost:8000``
    Replace your-backend-name with your actual backend URL.
3. Install dependencies
   ```bash
   npm install
   ```
4. Run the frontend development server
   ```bash
   npm run dev
   ```

- Then go to: http://localhost:5173

# Example Workflow
Upload Writers CSV (includes song title and artist)

Upload YouTube CSV (includes sr_title, sr_artist, related_asset_id)

Click “Match Songs & Download”

The frontend sends a `POST` request to the backend using Axios:

```js
const response = await axios.post(`${API_URL}/match-songs`, formData, {
  responseType: 'blob'
});
```

Backend performs matching and returns a matched_songs.csv file

Final CSV is automatically downloaded