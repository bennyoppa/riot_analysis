import os

from dotenv import load_dotenv

from Riot import Riot
from utils import read_all_matches

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("API_KEY")
    # puuid = os.getenv("PUUID")
    # match_data_dir = "match_data/"

    puuid = os.getenv("PUUID_SUPERGENIUS")
    match_data_dir = "match_data_supergenius/"

    if api_key is None or puuid is None:
        raise ValueError("API_KEY and PUUID environment variables must be set.")

    riot = Riot(
        start_time=1746057600,
        api_key=api_key,
        puuid=puuid,
        match_data_path=match_data_dir,
        headers={"X-Riot-Token": api_key},
    )

    riot.info()
    riot.download()

    df = read_all_matches(match_data_dir, puuid)
    df.to_csv("output/match_output_supergenius.csv", index=False)
