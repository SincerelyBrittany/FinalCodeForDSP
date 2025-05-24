import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export default function SongMatcher() {
  const [writersFile, setWritersFile] = useState(null);
  const [youtubeFile, setYoutubeFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!writersFile || !youtubeFile) return;

    const formData = new FormData();
    formData.append('writers_file', writersFile);
    formData.append('youtube_file', youtubeFile);

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/match-songs`, formData, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'matched_songs.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
      console.log('✅ File download triggered successfully.');
    } catch (error) {
      console.error('Upload error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">🎵 Song Matcher</h1>
      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <div>
          <label className="block font-semibold">Writers CSV:</label>
          <input type="file" accept=".csv" onChange={(e) => setWritersFile(e.target.files[0])} />
        </div>
        <div>
          <label className="block font-semibold">YouTube CSV:</label>
          <input type="file" accept=".csv" onChange={(e) => setYoutubeFile(e.target.files[0])} />
        </div>
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">
          {loading ? 'Matching...' : 'Match Songs & Download'}
        </button>
      </form>
    </div>
  );
}
