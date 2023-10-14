#! python3

"""
Version: MPL 1.1

The contents of this file are subject to the Mozilla Public License Version
1.1 the "License"; you may not use this file except in compliance with
the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
for the specific language governing rights and limitations under the
License.

The Original Code is the open.mp server browser.

The Initial Developer of the Original Code is Adib "adib_yg".
Portions created by the Initial Developer are Copyright (c) 2023
the Initial Developer. All Rights Reserved.

Contributor(s):
  -

Special Thanks to:
  open.mp team
  icons8.com
"""

from PyQt5 import QtWidgets, QtGui, QtCore, QtTest, uic
import os.path
import sys
import requests
import resources_rc


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        uic.loadUi(resource_path('form.ui'), self)

        self.iconOpenMp = QtGui.QIcon()
        self.iconOpenMp.addPixmap(
            QtGui.QPixmap(":/newPrefix/open-mp-icon.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)

        self.iconSamp = QtGui.QIcon()
        self.iconSamp.addPixmap(
            QtGui.QPixmap(":/newPrefix/samp-icon.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On)

        self.setWindowTitle("open.mp server browser")
        self.setWindowIcon(self.iconOpenMp)

        self.tableWidget.setColumnWidth(0, 130)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(3, 170)
        self.tableWidget.setColumnWidth(4, 100)

        self.tableWidget.clicked.connect(self.on_clicked_row)

        self.pushButtonRefresh.clicked.connect(self.on_clicked_button_refresh)

        self.lineEdit.textChanged.connect(self.on_line_edit_changed)

        self.checkBoxOpenMpServers.stateChanged.connect(
            self.on_omp_check_box_state_changed)

        self.checkBoxSampServers.stateChanged.connect(
            self.on_samp_check_box_state_changed)

        servers_count, players_count = self.loadServerList()

        self.labelOnlineServers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Servers:
                        <span style=\" font-weight:600;\">
                            {servers_count}
                        </span>
                    </p>
                </body>
            </html>""")

        self.labelOnlinePlayers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Players:
                        <span style=\" font-weight:600;\">
                            {players_count}
                        </span>
                    </p>
                </body>
            </html>""")

        if CHECK_FOR_UPDATES:
            self.checkForUpdates()

    def addServer(
            self,
            ip: str,
            hostname: str,
            players_count: int,
            players_max: int,
            gamemode: str,
            version: str,
            language: str,
            password: bool,
            omp: bool) -> None:

        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        numcols = self.tableWidget.columnCount()
        numrows = self.tableWidget.rowCount()
        row = numrows - 1

        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)

        self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(ip))

        self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(hostname))

        self.tableWidget.setItem(
            row,
            2,
            QtWidgets.QTableWidgetItem(
                f"{str(players_count)}/{str(players_max)}"))

        self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(gamemode))

        self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(language))

        self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(version))

        if password:
            item = QtWidgets.QTableWidgetItem("Yes")

            item.setTextAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)

            self.tableWidget.setItem(row, 6, item)
        else:
            item = QtWidgets.QTableWidgetItem("No")
            self.tableWidget.setItem(row, 6, item)

        if omp:
            item = QtWidgets.QTableWidgetItem("Yes")

            item.setTextAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)

            self.tableWidget.setItem(row, 7, item)

            item = QtWidgets.QTableWidgetItem()
            item.setIcon(self.iconOpenMp)
            self.tableWidget.setVerticalHeaderItem(row, item)

            if self.checkBoxOpenMpServers.isChecked():
                self.tableWidget.setRowHidden(row, False)
            else:
                self.tableWidget.setRowHidden(row, True)
        else:
            item = QtWidgets.QTableWidgetItem("No")
            self.tableWidget.setItem(row, 7, item)

            item = QtWidgets.QTableWidgetItem()
            item.setIcon(self.iconSamp)
            self.tableWidget.setVerticalHeaderItem(row, item)

            if self.checkBoxSampServers.isChecked():
                self.tableWidget.setRowHidden(row, False)
            else:
                self.tableWidget.setRowHidden(row, True)

    def loadServerList(self) -> int:
        url = "https://api.open.mp/servers"
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Critical)
            message.setWindowIcon(self.iconOpenMp)
            message.setWindowTitle("Error")
            message.setText("Could not get server list.\t\t")
            message.setInformativeText(
                "Failed to resolve 'api.open.mp'\n"
                "Please check your connection.")
            message.exec_()

            raise SystemExit(e)

        if response.status_code != 200:
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Critical)
            message.setWindowIcon(self.iconOpenMp)
            message.setWindowTitle("Error")
            message.setText("Could not get server list.\t\t")
            message.setInformativeText(
                "Internal server error 'api.open.mp'\n"
                "Please try again later.")
            message.exec_()

            sys.exit(0)
            return

        servers_count = int()
        players_count = int()

        json = response.json()

        for i in json:
            servers_count += 1
            players_count += i["pc"]

            self.addServer(
                i["ip"],
                i["hn"],
                i["pc"],
                i["pm"],
                i["gm"],
                i["vn"],
                i["la"],
                i["pa"],
                i["omp"])

        return servers_count, players_count

    def filterRows(self, text: str) -> None:
        if len(text) > 2:
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if (not self.checkBoxOpenMpServers.isChecked() and
                        item.text() == "Yes"):
                    continue
                if (not self.checkBoxSampServers.isChecked() and
                        item.text() == "No"):
                    continue

                for col in [0, 1, 3, 4, 5]:
                    item = self.tableWidget.item(row, col)
                    if text.casefold() not in item.text().casefold():
                        if col == 5:
                            self.tableWidget.setRowHidden(row, True)
                    else:
                        self.tableWidget.setRowHidden(row, False)
                        break
        else:
            if self.checkBoxOpenMpServers.isChecked():
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        if self.checkBoxSampServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)
            else:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 7)
                    if item.text() == "Yes":
                        self.tableWidget.setRowHidden(row, True)
                    else:
                        if self.checkBoxSampServers.isChecked():
                            self.tableWidget.setRowHidden(row, False)
                        else:
                            self.tableWidget.setRowHidden(row, True)

    def checkForUpdates(self) -> None:
        """
        version.json
        {
            "version": "1.0.0",
            "new_version_link": "https://..."
        }
        """

        url = (
            "https://raw.githubusercontent.com/adib-yg/"
            "openmp-server-browser/main/version.json")

        try:
            response = requests.get(url)
        except requests.exceptions.RequestException:
            return

        if response.status_code != 200:
            return

        try:
            json = response.json()

            if json["version"] == __version__:
                pass
            elif json["version"] > __version__:
                message = QtWidgets.QMessageBox()
                message.setIcon(QtWidgets.QMessageBox.Information)
                message.setWindowIcon(self.iconOpenMp)
                message.addButton("Later", QtWidgets.QMessageBox.YesRole)
                downloadButton = message.addButton(
                    "Download", QtWidgets.QMessageBox.ActionRole)
                message.setWindowTitle("A newer version is available!")
                message.setText(
                    "A newer version of "
                    "omp-server-browser is available!\t\t")
                message.setInformativeText(
                    "Click the \"Download\" button to get the new version.")
                message.exec_()

                if message.clickedButton() == downloadButton:
                    url = QtCore.QUrl(json["new_version_link"])
                    QtGui.QDesktopServices.openUrl(url)

        except Exception:
            pass

    def on_clicked_row(self, item):
        if item.column() == 0:  # Clicked on a row in the "IP Address" column
            cell_content = item.data()

            if len(cell_content):
                QtWidgets.QApplication.clipboard().setText(cell_content)

    def on_clicked_button_refresh(self):
        self.pushButtonRefresh.setEnabled(False)

        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: self.pushButtonRefresh.setEnabled(True))
        timer.start(30000)

        self.tableWidget.setRowCount(0)  # Remove all rows

        self.labelOnlineServers.setText("""
            <html>
                <head/>
                <body>
                    <p>Online Servers:
                        <span style=\" font-weight:600;\">
                            -
                        </span>
                    </p>
                </body>
            </html>""")

        self.labelOnlinePlayers.setText("""
            <html>
                <head/>
                <body>
                    <p>Online Players:
                        <span style=\" font-weight:600;\">
                            -
                        </span>
                    </p>
                </body>
            </html>""")

        QtTest.QTest.qWait(500)

        servers_count, players_count = self.loadServerList()

        self.labelOnlineServers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Servers:
                        <span style=\" font-weight:600;\">
                            {servers_count}
                        </span>
                    </p>
                </body>
            </html>""")

        self.labelOnlinePlayers.setText(f"""
            <html>
                <head/>
                <body>
                    <p>Online Players:
                        <span style=\" font-weight:600;\">
                            {players_count}
                        </span>
                    </p>
                </body>
            </html>""")

        # Check filter again
        text = self.lineEdit.text()
        if len(text) > 2:
            self.filterRows(text)

    def on_line_edit_changed(self):
        text = self.lineEdit.text()
        self.filterRows(text)

    def on_omp_check_box_state_changed(self):
        if self.checkBoxOpenMpServers.isChecked():
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if item.text() == "Yes":
                    self.tableWidget.setRowHidden(row, False)
                else:
                    if self.checkBoxSampServers.isChecked():
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)
        else:
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if item.text() == "Yes":
                    self.tableWidget.setRowHidden(row, True)
                else:
                    if self.checkBoxSampServers.isChecked():
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)

        # Check filter again
        text = self.lineEdit.text()
        if len(text) > 2:
            self.filterRows(text)

    def on_samp_check_box_state_changed(self):
        if self.checkBoxSampServers.isChecked():
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if item.text() == "No":
                    self.tableWidget.setRowHidden(row, False)
                else:
                    if self.checkBoxOpenMpServers.isChecked():
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)
        else:
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 7)
                if item.text() == "No":
                    self.tableWidget.setRowHidden(row, True)
                else:
                    if self.checkBoxOpenMpServers.isChecked():
                        self.tableWidget.setRowHidden(row, False)
                    else:
                        self.tableWidget.setRowHidden(row, True)

        # Check filter again
        text = self.lineEdit.text()
        if len(text) > 2:
            self.filterRows(text)


if __name__ == '__main__':
    __version__ = "1.0.0"

    CHECK_FOR_UPDATES = True

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
