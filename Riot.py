import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

import requests


@dataclass
class Riot:
    api_key: str
    puuid: str
    headers: dict
    window_size: int = 10
    match_data_path: str = "match_data"
    start_time: int = 1709211600  # 2024-03-01 12:00:00 AM
    end_time: Optional[int] = None

    def __post_init__(self) -> None:
        self.set_start_time()
        self.set_end_time()
        self.time_windows = self.get_time_windows()
        self.match_ids = self.get_match_ids()

    def info(self) -> None:
        ready_for_download = self.prepare_match_ids_for_download()
        num_matches = len(self.match_ids)
        print(
            f"{num_matches} games played between {self.start_time_str} and {self.end_time_str}."
        )
        num_ready_for_download = len(ready_for_download)
        num_downloaded = num_matches - num_ready_for_download
        print(
            f"{num_downloaded} downloaded, {num_ready_for_download} ready for download."
        )

    def refresh(self) -> None:
        self.end_time = int(time.time())
        self.end_time_str = self.epoch_to_datetime_str(self.end_time)
        self.time_windows = self.get_time_windows()
        self.match_ids = self.get_match_ids()
        self.info()

    def epoch_to_datetime_str(self, epoch: int) -> str:
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def set_start_time(self) -> None:
        self.start_time_str = self.epoch_to_datetime_str(self.start_time)

    def set_end_time(self) -> None:
        if not self.end_time:
            self.end_time = int(time.time())
            self.end_time_str = self.epoch_to_datetime_str(self.end_time)

    def get_time_windows(self) -> List[Tuple]:
        step = 60 * 60 * 24 * self.window_size  # 10 days
        time_windows = []
        if self.end_time:
            for i in range(self.start_time, self.end_time, step):
                start = i
                end = i + step
                if end > self.end_time:
                    end = self.end_time
                time_windows.append((start, end))
        return time_windows

    def get_match_ids(self) -> List[str]:
        match_ids = []

        for window in self.time_windows:
            start_time = window[0]
            end_time = window[1]

            url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?startTime={start_time}&endTime={end_time}&count=100"
            response = requests.get(url=url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                match_ids += data
        return match_ids

    def get_local_match_ids(self) -> List[str]:
        existing = []
        for file_name in os.listdir(self.match_data_path):
            if ".json" in file_name:
                match_id = file_name.replace(".json", "")
                existing.append(match_id)
        return existing

    def prepare_match_ids_for_download(self) -> List[str]:
        existing = self.get_local_match_ids()
        download = [i for i in self.match_ids if i not in existing]
        return download

    def download(self) -> None:
        ready_for_download = self.prepare_match_ids_for_download()

        for match_id in ready_for_download:
            url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{match_id}"

            response = requests.get(url=url, headers=self.headers)

            if response.status_code == 200:
                print(f"Downloading {match_id}...")
                data = response.json()
                with open(f"match_data/{match_id}.json", "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Done!")
            else:
                print(f"Error: {response.status_code}")

            time.sleep(0.5)
