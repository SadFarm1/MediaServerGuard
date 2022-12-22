from typing import Union

import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import constants


class WatchlistReport:
    def __init__(self, server: str, details: str):
        self.server = server
        self.details = details


class WatchlistMatch:
    def __init__(self, username: str, user_id: str, reports: list[WatchlistReport]):
        self.username = username
        self.user_id = user_id
        self.reports = reports

    @property
    def embed(self):
        embed = discord.Embed(
            title="Guard Alert",
            description=f"Scan Report for {self.username} ``{self.user_id}``",
            color=0xff0000
        )
        for report in self.reports:
            embed.add_field(
                name=f"Reported in {report.server}",
                value=report.details,
                inline=False
            )
        return embed


class Watchlist:
    def __init__(self, creds_json_file_path: str):
        self._creds = ServiceAccountCredentials.from_json_keyfile_name(
            filename=creds_json_file_path,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive'
            ])

    def _get_danger_sheet(self):
        client = gspread.authorize(self._creds)
        return client.open(constants.WATCHLIST_WORKBOOK).worksheet(constants.WATCHLIST_WORKBOOK_SHEET)

    def add_entry(self, username: str, user_id: str, details: str, guild_name: str):
        danger_sheet = self._get_danger_sheet()
        danger_sheet.append_row([username, user_id, details, guild_name])

    def get_watchlist_match(self, member: discord.Member, danger_sheet=None,
                            danger_usernames_filtered=None) -> Union[WatchlistMatch, None]:
        member = str(member)

        if not danger_sheet:
            danger_sheet = self._get_danger_sheet()  # only get the sheet if we need to, save on API calls

        if not danger_usernames_filtered:  # only get the filtered list if we need to, save on filtering process
            danger_usernames = [item for item in danger_sheet.col_values(1) if item]
            danger_usernames_filtered = []
            [danger_usernames_filtered.append(x) for x in danger_usernames if x not in danger_usernames_filtered]

        if member in danger_usernames_filtered:
            reports = []
            user_id = 0
            username_entries = danger_sheet.findall(str(member))
            for entry in username_entries:
                row = entry.row
                report = WatchlistReport(
                    server=danger_sheet.cell(row, 4).value,
                    details=danger_sheet.cell(row, 3).value
                )
                reports.append(report)
                user_id = danger_sheet.cell(row, 2).value  # only need to get this once
            return WatchlistMatch(
                username=member,
                user_id=user_id,
                reports=reports
            )

        return None

    def get_all_watchlist_matches(self, members: list) -> list[WatchlistMatch]:
        danger_sheet = self._get_danger_sheet()
        danger_usernames = [item for item in danger_sheet.col_values(1) if item]

        danger_usernames_filtered = []
        [danger_usernames_filtered.append(x) for x in danger_usernames if x not in danger_usernames_filtered]

        matches = []
        for member in members:
            match = self.get_watchlist_match(member, danger_sheet, danger_usernames_filtered)
            if match:
                matches.append(match)

        return matches
