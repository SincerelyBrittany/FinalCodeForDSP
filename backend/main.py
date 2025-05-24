from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize(text):
    return str(text).strip().lower()

@app.post("/match-songs")
async def match_songs(writers_file: UploadFile = File(...), youtube_file: UploadFile = File(...)):
    writers_content = await writers_file.read()
    youtube_content = await youtube_file.read()

    writers_df = pd.read_csv(io.StringIO(writers_content.decode("utf-8")))
    youtube_df = pd.read_csv(io.StringIO(youtube_content.decode("utf-8")))

    # Precompute a lowercase text blob from YouTube data for faster matching
    youtube_df["search_blob"] = (
        youtube_df["sr_title"].astype(str).str.lower().fillna('') + " " +
        youtube_df["sr_artist"].astype(str).str.lower().fillna('')
    )
    youtube_df["related_asset_id"] = youtube_df["related_asset_id"].astype(str)

    related_ids = []
    checkpoint_path = "checkpoint_partial_results.csv"

    for index, (_, writer_row) in enumerate(writers_df.iterrows()):
        print(f"🔄 Matching writer row {index + 1} of {len(writers_df)}: {writer_row.get('Display Title', '')}")

        raw_title = normalize(writer_row.get("Display Title", ""))
        writer_title = raw_title.split(" - ")[0].strip()
        writer_artist = normalize(writer_row.get("artist", ""))
        asset_id = str(writer_row.get("Asset ID", "")).strip()

        search_term = f"{writer_title} {writer_artist}"

        matches = youtube_df[youtube_df["search_blob"].apply(lambda x: search_term in x)]

        if not matches.empty:
            asset_ids = matches["related_asset_id"].dropna().tolist()
            filtered_ids = [rid for rid in asset_ids if rid.strip() != asset_id]
            related_ids.append(" | ".join(filtered_ids))
        else:
            related_ids.append("")

        # Save progress every 25 rows
        if (index + 1) % 25 == 0:
            partial_df = writers_df.iloc[:index+1].copy()
            partial_df["related_asset_id"] = related_ids
            partial_df.to_csv(checkpoint_path, index=False)
            print(f"💾 Saved checkpoint after row {index + 1} to {checkpoint_path}")

    writers_df["related_asset_id"] = related_ids

    final_path = "results.csv"
    writers_df.to_csv(final_path, index=False)
    print(f"✅ Final results saved to {final_path}")

    output = io.StringIO()
    writers_df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=matched_songs.csv"})


