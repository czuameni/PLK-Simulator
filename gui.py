import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QListWidget,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor

from main import load_teams, run_postseason
from schedule import generate_schedule
from models import Game
from engine import simulate_game
from league import update_standings, get_standings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PLK Simulator")
        self.setWindowIcon(QIcon("assets/plk.ico"))
        self.setGeometry(100, 100, 1000, 650)

        self.teams = load_teams()
        self.schedule = generate_schedule(self.teams)
        self.current_round = 0
        self.round_history = []

        self.phase = "regular"

        self.playin_data = None
        self.playoff_data = None

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout()
        central.setLayout(layout)

        self.menu = QListWidget()
        self.menu.addItems(["Fixtures", "Standings", "Play-In", "Playoff"])
        self.menu.currentRowChanged.connect(self.change_view)

        right = QVBoxLayout()

        self.title = QLabel("PLK Simulator")
        self.title.setAlignment(Qt.AlignCenter)

        self.info = QLabel("Start sezonu")
        self.info.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()

        self.next_btn = QPushButton("NEXT ROUND")
        self.next_btn.clicked.connect(self.play_next_round)

        right.addWidget(self.title)
        right.addWidget(self.info)
        right.addWidget(self.table)
        right.addWidget(self.next_btn)

        layout.addWidget(self.menu, 1)
        layout.addLayout(right, 4)

        self.menu.setCurrentRow(0)

    # =========================
    def play_next_round(self):

        if self.phase == "regular":

            if self.current_round >= len(self.schedule):
                self.start_postseason()
                return

            round_games = self.schedule[self.current_round]
            results = []

            for home, away in round_games:
                game = Game(home, away)
                simulate_game(game)
                update_standings(game)
                results.append(game)

            self.round_history.append(results)
            self.current_round += 1

            self.show_fixtures()

        else:
            self.info.setText("POSTSEASON FINISHED")

    # =========================
    def change_view(self, index):
        if index == 0:
            self.show_fixtures()
        elif index == 1:
            self.show_standings()
        elif index == 2:
            self.show_playin()
        elif index == 3:
            self.show_playoff()

    def show_fixtures(self):
        if self.current_round == 0:
            self.info.setText("No games yet")
            self.table.setRowCount(0)
            return

        games = self.round_history[self.current_round - 1]

        self.table.clear()
        self.table.setRowCount(len(games) * 3)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Team", "Score"])

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(1, 80)

        row = 0

        for g in games:
            home = QTableWidgetItem(g.home.name)
            home.setIcon(QIcon(self.get_logo(g.home.name)))
            self.table.setItem(row, 0, home)
            self.table.setItem(row, 1, QTableWidgetItem(str(g.home_score)))

            away = QTableWidgetItem(g.away.name)
            away.setIcon(QIcon(self.get_logo(g.away.name)))
            self.table.setItem(row + 1, 0, away)
            self.table.setItem(row + 1, 1, QTableWidgetItem(str(g.away_score)))

            self.table.setItem(row + 2, 0, QTableWidgetItem(""))
            self.table.setItem(row + 2, 1, QTableWidgetItem(""))

            row += 3

        self.info.setText(f"Round {self.current_round}")

    def show_standings(self):
        standings = get_standings(self.teams)

        self.table.clear()
        self.table.setRowCount(len(standings))
        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels(
            ["#", "Team", "G", "W", "L", "PF", "PA", "PTS"]
        )

        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        for i in range(2, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 220)

        for row, t in enumerate(standings):
            pos = QTableWidgetItem(str(row + 1))
            pos.setTextAlignment(Qt.AlignCenter)

            if row < 6:
                pos.setBackground(QColor("#1f4fbf"))
                pos.setForeground(Qt.white)
            elif row < 10:
                pos.setBackground(QColor("#4fa3ff"))
            elif row == len(standings) - 1:
                pos.setBackground(QColor("#d32f2f"))
                pos.setForeground(Qt.white)

            self.table.setItem(row, 0, pos)

            team = QTableWidgetItem(t.name)
            team.setIcon(QIcon(self.get_logo(t.name)))
            self.table.setItem(row, 1, team)

            self.table.setItem(row, 2, QTableWidgetItem(str(t.games_played)))
            self.table.setItem(row, 3, QTableWidgetItem(str(t.wins)))
            self.table.setItem(row, 4, QTableWidgetItem(str(t.losses)))
            self.table.setItem(row, 5, QTableWidgetItem(str(t.scored)))
            self.table.setItem(row, 6, QTableWidgetItem(str(t.conceded)))
            self.table.setItem(row, 7, QTableWidgetItem(str(t.points)))

        self.info.setText("Standings")

    def show_playin(self):
        self.table.clear()

        if not self.playin_data:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Play-In"])
            self.info.setText("Play-In not started")
            return

        rows = []

        for matchup in self.playin_data["matchups"]:
            t1, t2 = matchup["teams"]

            rows.append((f"{t1.name} vs {t2.name}", ""))

            for g in matchup["games"]:
                rows.append((g.home.name, str(g.home_score)))
                rows.append((g.away.name, str(g.away_score)))
                rows.append(("", ""))  # odstęp

            rows.append((f"Winner: {matchup['winner'].name}", ""))
            rows.append(("", ""))

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Team", "Score"])

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(1, 80)

        for i, (team, score) in enumerate(rows):
            item = QTableWidgetItem(team)

            if team and not team.startswith("Winner") and "vs" not in team:
                item.setIcon(QIcon(self.get_logo(team)))

            self.table.setItem(i, 0, item)

            self.table.setItem(i, 1, QTableWidgetItem(score))

        self.info.setText("Play-In")

    def show_playoff(self):
        self.table.clear()

        if not self.playoff_data:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Playoff"])
            self.info.setText("Playoff not started")
            return

        rows = []

        rows.append(("=== QUARTERFINALS ===", ""))
        rows.append(("", ""))

        for matchup in self.playoff_data["quarterfinals"]:
            t1, t2 = matchup["teams"]
            rows.append((f"{t1.name} vs {t2.name}", ""))

            for g in matchup["games"]:
                rows.append((g.home.name, str(g.home_score)))
                rows.append((g.away.name, str(g.away_score)))
                rows.append(("", ""))

            rows.append((f"Winner: {matchup['winner'].name}", ""))
            rows.append(("", ""))

        rows.append(("=== SEMIFINALS ===", ""))
        rows.append(("", ""))

        for matchup in self.playoff_data["semifinals"]:
            t1, t2 = matchup["teams"]
            rows.append((f"{t1.name} vs {t2.name}", ""))

            for g in matchup["games"]:
                rows.append((g.home.name, str(g.home_score)))
                rows.append((g.away.name, str(g.away_score)))
                rows.append(("", ""))

            rows.append((f"Winner: {matchup['winner'].name}", ""))
            rows.append(("", ""))

        rows.append(("=== FINAL ===", ""))
        rows.append(("", ""))

        final = self.playoff_data["final"]
        t1, t2 = final["teams"]

        rows.append((f"{t1.name} vs {t2.name}", ""))

        for g in final["games"]:
            rows.append((g.home.name, str(g.home_score)))
            rows.append((g.away.name, str(g.away_score)))
            rows.append(("", ""))

        rows.append((f"🏆 Champion: {final['winner'].name}", ""))
        rows.append(("", ""))

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Team", "Score"])

        for i, (team, score) in enumerate(rows):
            item = QTableWidgetItem(team)

            if team and not team.startswith("Winner") and "Champion" not in team and "vs" not in team and "===" not in team:
                item.setIcon(QIcon(self.get_logo(team)))

            self.table.setItem(i, 0, item)

            self.table.setItem(i, 1, QTableWidgetItem(score))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(1, 80)

        self.info.setText("Playoff")

    def start_postseason(self):
        self.phase = "postseason"

        champion, playin_data, playoff_data = run_postseason(self.teams)

        self.playin_data = playin_data
        self.playoff_data = playoff_data

        self.info.setText(f"Round finished – postseason started")

    # =========================
    def get_logo(self, name):
        n = name.lower().replace(" ", "_")

        repl = {
            "ą": "a", "ć": "c", "ę": "e",
            "ł": "l", "ń": "n", "ó": "o",
            "ś": "s", "ż": "z", "ź": "z"
        }

        for k, v in repl.items():
            n = n.replace(k, v)

        return os.path.join("assets", "logos", f"{n}.png")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())