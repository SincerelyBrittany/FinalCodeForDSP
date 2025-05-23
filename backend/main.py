from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io

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

    # Normalize YouTube artist and title
    youtube_df["sr_title_clean"] = youtube_df["sr_title"].astype(str).str.lower()
    youtube_df["sr_artist_clean"] = youtube_df["sr_artist"].astype(str).str.lower()

    related_ids = []

    for index, (_, writer_row) in enumerate(writers_df.iterrows()):
        print(f"🔄 Matching writer row {index + 1} of {len(writers_df)}: {writer_row.get('Display Title', '')}")

        raw_title = normalize(writer_row.get("Display Title", ""))
        writer_title = raw_title.split(" - ")[0].strip()
        writer_artist = normalize(writer_row.get("artist", ""))

        matches = youtube_df[
            youtube_df["sr_title_clean"].str.contains(writer_title, na=False, regex=False) &
            youtube_df["sr_artist_clean"].str.contains(writer_artist, na=False, regex=False)
        ]

        asset_id = str(writer_row.get("Asset ID", "")).strip()
        if not matches.empty:
            asset_ids = matches["related_asset_id"].dropna().astype(str).tolist()
            filtered_ids = [rid for rid in asset_ids if rid.strip() != asset_id]
            related_ids.append(" | ".join(filtered_ids))
        else:
            related_ids.append("")

    writers_df["related_asset_id"] = related_ids

    output = io.StringIO()
    writers_df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=matched_songs.csv"})


# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import pandas as pd
# import io

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def normalize(text):
#     return str(text).strip().lower()

# @app.post("/match-songs")
# async def match_songs(writers_file: UploadFile = File(...), youtube_file: UploadFile = File(...)):
#     writers_content = await writers_file.read()
#     youtube_content = await youtube_file.read()

#     writers_df = pd.read_csv(io.StringIO(writers_content.decode("utf-8")))
#     youtube_df = pd.read_csv(io.StringIO(youtube_content.decode("utf-8")))

#     # Normalize YouTube artist and title
#     youtube_df["sr_title_clean"] = youtube_df["sr_title"].astype(str).str.lower()
#     youtube_df["sr_artist_clean"] = youtube_df["sr_artist"].astype(str).str.lower()

#     related_ids = []

#     for index, (_, writer_row) in enumerate(writers_df.iterrows()):
#         print(f"🔄 Matching writer row {index + 1} of {len(writers_df)}: {writer_row.get('Display Title', '')}")
        
#         raw_title = normalize(writer_row.get("Display Title", ""))
#         writer_title = raw_title.split(" - ")[0].strip()
#         writer_artist = normalize(writer_row.get("artist", ""))
    
#         # Basic partial match (both fields must contain)
#         matches = youtube_df[
#             youtube_df["sr_title_clean"].str.contains(writer_title, na=False, regex=False) &
#             youtube_df["sr_artist_clean"].str.contains(writer_artist, na=False, regex=False)
#         ]

#         # Get pipe-separated related_asset_id values
#         if not matches.empty:
#             asset_ids = matches["related_asset_id"].dropna().astype(str).tolist()
#             related_ids.append(" | ".join(asset_ids))
#         else:
#             related_ids.append("")

#     # Add related_asset_id column to writers_df
#     writers_df["related_asset_id"] = related_ids

#     # Convert to CSV
#     output = io.StringIO()
#     writers_df.to_csv(output, index=False)
#     output.seek(0)

#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=matched_songs.csv"})
