import os

from dotenv import load_dotenv

from Riot import Riot
from utils import read_all_matches

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("API_KEY")
    puuid = os.getenv("PUUID")
    match_data_dir = "match_data/"

    riot = Riot(
        api_key=api_key,
        puuid=puuid,
        headers={"X-Riot-Token": api_key},
    )

    df = read_all_matches(match_data_dir, puuid)
    df.to_csv("output/match_output.csv", index=False)
