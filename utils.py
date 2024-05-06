import json
import os
import re
from datetime import datetime
from typing import Dict, Optional

import pandas as pd


def read_all_matches(files_dir: str, puuid: str) -> pd.DataFrame:
    files = os.listdir(files_dir)
    all_data = []

    for file_name in files:
        file_name = os.path.join(files_dir, file_name)
        data = read_match_info(file_name, puuid)
        if data:
            all_data.append(data)

    df = pd.DataFrame(all_data)
    df["Day_of_Week"] = pd.to_datetime(df["Date"]).dt.day_name()
    df["Time_Interval"] = df["Time"].apply(lambda x: int(re.search(r"\d+", x).group(0)))
    return df


def read_match_info(file_name: str, puuid: str) -> Optional[Dict]:
    partner_dict = {
        "BOTTOM": "UTILITY",
        "UTILITY": "BOTTOM",
        "MIDDLE": "JUNGLE",
        "JUNGLE": "MIDDLE",
        "TOP": "JUNGLE",
    }

    with open(file_name) as f:
        data = json.load(f)

    if data["info"]["gameDuration"] <= 900:
        return None

    # get my info
    for participant in data["info"]["participants"]:
        if participant["puuid"] == puuid:
            position = participant["teamPosition"]
            champion = participant["championName"]
            kills = participant["kills"]
            deaths = participant["deaths"]
            assists = participant["assists"]
            minions_killed = participant["totalMinionsKilled"]
            win = 1 if participant["win"] else 0
            team_id = participant["teamId"]
            elder_dragons = participant["challenges"]["teamElderDragonKills"]
            damage_percentage = participant["challenges"]["teamDamagePercentage"]

    # get my team info
    for team in data["info"]["teams"]:
        if team["teamId"] == team_id:
            rift_herald = team["objectives"]["riftHerald"]["kills"]
            first_tower = 1 if team["objectives"]["tower"]["first"] else 0
            towers = team["objectives"]["tower"]["kills"]
            first_dragon = 1 if team["objectives"]["dragon"]["first"] else 0
            dragons = team["objectives"]["dragon"]["kills"]
            grubs = team["objectives"]["horde"]["kills"]
            first_baron = 1 if team["objectives"]["baron"]["first"] else 0
            barons = team["objectives"]["baron"]["kills"]

    # get my partner, enemy and enemy partner info
    partner_position = partner_dict[position]

    for participant in data["info"]["participants"]:
        if (
            participant["teamId"] == team_id
            and participant["teamPosition"] == partner_position
        ):
            partner_champion = participant["championName"]

        if participant["teamId"] != team_id and participant["teamPosition"] == position:
            enemy_champion = participant["championName"]

        if (
            participant["teamId"] != team_id
            and participant["teamPosition"] == partner_position
        ):
            enemy_partner_champion = participant["championName"]

    return {
        "Match_ID": data["metadata"]["matchId"],
        "Version": re.search(r"\d+\.\d+", data["info"]["gameVersion"]).group(0),
        "Date": datetime.fromtimestamp(data["info"]["gameCreation"] // 1000).strftime(
            "%Y-%m-%d"
        ),
        "Time": datetime.fromtimestamp(data["info"]["gameCreation"] // 1000).strftime(
            "%H:%M:%S"
        ),
        "Duration": data["info"]["gameDuration"],
        "Win": win,
        "Position": position,
        "Champion": champion,
        "Partner_Position": partner_position,
        "Partner_Champion": partner_champion,
        "Kills": kills,
        "Deaths": deaths,
        "Assists": assists,
        "Minions_Killed": minions_killed,
        "Damage_Percentage": damage_percentage,
        "Enemy_Champion": enemy_champion,
        "Enemy_Partner_Champion": enemy_partner_champion,
        "Rift_Herald": rift_herald,
        "First_Tower": first_tower,
        "Towers": towers,
        "First_Dragon": first_dragon,
        "Dragons": dragons - elder_dragons,
        "Grubs": grubs,
        "First_Baron": first_baron,
        "Barons": barons,
        "Elder_Dragons": elder_dragons,
    }
