import sys
from ui_code import Ui_MainWindow  # Import the generated UI code
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLabel
import pandas as pd
import sorting
import copy
import Web_Scraping
import des_sorting
from PyQt5.QtCore import QThread, pyqtSignal
import searching
from searching import *
import os


class data:
    def __init__(self):
        self.title = []
        self.answers = []
        self.views = []
        self.votes = []
        self.reputation = []
        self.time_stamp = []
        self.summary = []
        self.users = []


class WebScraping_thread(QThread):
    finished = pyqtSignal()
    stop_requested = False
    value = 0
    count = 0
    Scrape_data = None

    def run(self):
        self.stop_requested = False
        start = Web_Scraping.get_start_index()
        for x in range(start, 32185):
            if self.stop_requested:
                break
            scrap_data = Web_Scraping.web_scraping(x)
            self.Scrape_data = combine_data(self.Scrape_data, scrap_data)
            self.value = self.value + 50
            self.count = self.count + 1
        self.finished.emit()

    def stop(self):
        print(f" Wb_scraping has been stopped")
        self.stop_requested = True
        return self.value, self.count, self.Scrape_data


def combine_data(data1, data2):
    if data1 is None:
        data1 = copy.deepcopy(data2)
        return data1
    else:
        data1.title.extend(data2.title)
        data1.answers.extend(data2.answers)
        data1.views.extend(data2.views)
        data1.votes.extend(data2.votes)
        data1.reputation.extend(data2.reputation)
        data1.time_stamp.extend(data2.time_stamp)
        data1.summary.extend(data2.summary)
        data1.users.extend(data2.users)
    return data1


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.frameSearch.hide()
        self.ui.frameSort.hide()
        self.ui.frameScrap.hide()
        self.ui.tableWidget.hide()
        # Connect the button click event to the slot (function)
        self.ui.Sorting.clicked.connect(self.toggle_frame)
        self.ui.Searching.clicked.connect(self.toggle_frame1)
        self.ui.Scraping.clicked.connect(self.toggle_frame2)
        self.datas = self.loaddata()  # load data into list
        if self.datas is not None:
            self.loadtable(self.datas, self.ui.tableWidget)  # load data into table
        self.ui.btn_sort_2.clicked.connect(self.sorting_algo)

        self.ui.btn_car_contains.clicked.connect(self.simplesearch)
        self.ui.btn_search.clicked.connect(self.searcha)
        self.ui.btn_search_2.clicked.connect(self.filter_search)
        self.ui.btn_clr_search.clicked.connect(self.clear_search)  # clear button of searching
        self.ui.btn_clr_search_2.clicked.connect(self.clear_search)  # clear button of searching

        # scraping buttons
        self.web_scraping = WebScraping_thread()
        self.ui.btn_scrap.clicked.connect(self.start_thread)
        self.ui.btn_resume_scrap.clicked.connect(self.start_thread)
        self.ui.btn_pause_scrap.clicked.connect(self.stop_thread)
        self.ui.btn_clr_sort_2.clicked.connect(self.clear_sort)  # clear button of sorting
        self.ui.btn_reset.clicked.connect(self.reset_table)
        self.changetextoflabel()
        self.ui.progressBar_scrap.setValue(0)

    def simplesearch(self):
        at = self.ui.txt_car_contains_2.toPlainText()
        searching.dataa(data, at , self.ui.tableWidget, 'Title')
    def searcha(self):
        af = self.ui.combo_attribute_search.currentText()
        at = self.ui.filtersearch.toPlainText()
        searching.dataa(data, at, self.ui.tableWidget, af)

    def filter_search(self):
        search_word = self.ui.txt_contain_search.toPlainText()
        af = self.ui.combo_attribute_search.currentText()

        if self.ui.combo_attribute_search_2.currentText() == 'Starts with':
            searching.search_start_as(data, search_word, self.ui.tableWidget, af)
        elif self.ui.combo_attribute_search_2.currentText() == 'Contains':
            searching.search_contain(data, search_word, self.ui.tableWidget, af)
        elif self.ui.combo_attribute_search_2.currentText() == 'Ends as':
            searching.search_end_as(data, search_word, self.ui.tableWidget, af)

    def clear_search(self):  # clear bitton of sorting panel
        self.ui.txt_car_contains_2.clear()
        self.ui.filtersearch.clear()
        self.ui.txt_contain_search.clear()
        self.loaddata()
        self.loadtable(self.datas, self.ui.tableWidget)

    def start_thread(self):
        if self.ui.radioButton.isChecked():
            self.web_scraping.stop_requested = False
            self.web_scraping.start()
        if self.ui.radioButton_2.isChecked():
            self.web_scraping.stop_requested = False
            print(f' in abc')
            url=self.ui.txt_url.toPlainText()
            data2 = Web_Scraping.scrape_Data(url)
            if data2:
                self.loadTableUrlScraped(data2, self.ui.scrap_table)

    def stop_thread(self):
        val, count, scraped_data = self.web_scraping.stop()
        self.ui.lbl_entites_scrapped.setText(str(val))
        cal = (count * 100) / 300  # 300 is variable depend on total pages
        self.ui.progressBar_scrap.setValue(count)
        self.datas = combine_data(self.datas, scraped_data)
        self.loadtable(scraped_data, self.ui.scrap_table)
        self.loadtable(self.datas, self.ui.tableWidget)

    def reset_button(self):
        self.ui.combo_algo_sort.setCurrentIndex(0)
        self.ui.col_name.setChecked(False)
        self.ui.col_grade.setChecked(False)
        self.ui.col_year.setChecked(False)
        self.ui.col_trans.setChecked(False)
        self.ui.col_mileage.setChecked(False)
        self.ui.col_fuel.setChecked(False)
        self.ui.col_cc.setChecked(False)
        self.ui.col_link.setChecked(False)

    def clear_sort(self):  # clear button of sorting panel
        self.reset_button()
        if self.datas is not None:
            self.loaddata()
            self.loadtable(self.datas, self.ui.tableWidget)

    def reset_table(self):
        self.reset_button()
        if self.datas is not None:
            self.loaddata()
            self.loadtable(self.datas, self.ui.tableWidget)
        self.ui.lbl_time_stat.setText(f'__________')
        self.ui.lbl_algo_stat.setText(f'__________')

    def sorting_data(self):
        order = None
        algo = self.ui.combo_algo_sort.currentText()
        col = []
        count = 0
        if self.ui.radio_ascend_sort.isChecked():
            order = 'ascending'
        elif self.ui.radio_descend_sort.isChecked():
            order = 'descending'
        else:
            order = None
        if self.ui.col_name.isChecked():
            col.append('title')
            count += 1
        if self.ui.col_grade.isChecked():
            col.append('answers')
            count += 1
        if self.ui.col_year.isChecked():
            col.append('views')
            count += 1
        if self.ui.col_trans.isChecked():
            col.append('votes')
            count += 1
        if self.ui.col_mileage.isChecked():
            col.append('users')
            count += 1
        if self.ui.col_fuel.isChecked():
            col.append('reputation')
            count += 1
        if self.ui.col_cc.isChecked():
            col.append('time_stamp')
            count += 1
        if self.ui.col_link.isChecked():
            col.append('summary')
            count += 1
        return count, col, algo, order

    def converted_rep(self, rep):
        for x in range(len(rep)):
            if rep[x] == 'No detail available':
                rep[x] = 0
            else:
                rep[x] = int(rep[x].replace(',', ''))
        return rep

    def revert_rep(self, rep):
        for x in range(len(rep)):
            if rep[x] == 0:
                rep[x] = 'No detail available'
            else:
                rep[x] = str(rep[x])
        return rep

    def loadTableUrlScraped(self, data, table):
        htmlTags = data.html_tags

        rows = len(next(iter(htmlTags.values())))
        cols = len(htmlTags)

        table.setRowCount(rows)
        table.setColumnCount(cols)

        headers = list(htmlTags.keys())
        table.setHorizontalHeaderLabels(headers)

        for row, (tag, content) in enumerate(htmlTags.items()):
            for col, value in enumerate(content):
                item = QTableWidgetItem(str(value))
                table.setItem(col, row, item)

    def sorting_algo(self):
        if self.datas is not None:
            T_time = 0.0000
            data_insort = copy.deepcopy(self.datas)
            data_insort.reputation = self.converted_rep(data_insort.reputation)
            count, col, algo, order = self.sorting_data()
            sorted_data = None
            if col is not None and algo is not None and order is not None and count != 0:
                for x in range(count):
                    if algo == 'Bubble Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_Bubble_Sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_Bubble_Sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Selection Sort ':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_selection_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_selection_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Insertion Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_insertion_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_insertion_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Merge Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_merge_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_merge_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Quick Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_quick_Sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_quick_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Radix Sort':
                        if order == 'ascending':
                            try:
                                sorted_data, time = sorting.asc_radix_sort(data_insort, col[x], 10)
                                T_time = T_time + time
                            except:
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Radix Sort'.")
                        elif order == 'descending':
                            try:
                                sorted_data, time = des_sorting.desc_radix_sort(data_insort, col[x], 10)
                                T_time = T_time + time
                            except:
                                sorted_data = None
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Radix Sort'.")
                    if algo == 'Bucket Sort':
                        if order == 'ascending':
                            try:
                                sorted_data, time = sorting.asc_bucket_sort_data(data_insort, col[x])
                                T_time = T_time + time
                            except:
                                sorted_data = None
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Bucket Sort'.")
                        elif order == 'descending':
                            try:
                                sorted_data, time = des_sorting.dsc_bucket_sort_data(data_insort, col[x])
                                T_time = T_time + time
                            except:
                                sorted_data = None
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Bucket Sort'.")
                    if algo == 'Counting Sort':
                        if order == 'ascending':
                            try:
                                sorted_data, time = sorting.asc_counting_sort(data_insort, col[x])
                                T_time = T_time + time
                            except:
                                sorted_data = None
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Counting Sort'.")
                        elif order == 'descending':
                            try:
                                sorted_data, time = des_sorting.dsc_counting_sort(data_insort, col[x])
                                T_time = T_time + time
                            except:
                                sorted_data = None
                                T_time = 0.00
                                QMessageBox.information(None, "Invalid algorithm",
                                                        "Please select a valid column for 'Counting Sort'.")
                    if algo == 'Heap Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_heap_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_heap_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Shell Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_shell_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_shell_sort(data_insort, col[x])
                            T_time = T_time + time
                    if algo == 'Comb Sort':
                        if order == 'ascending':
                            sorted_data, time = sorting.asc_comb_sort(data_insort, col[x])
                            T_time = T_time + time
                        elif order == 'descending':
                            sorted_data, time = des_sorting.dsc_comb_sort(data_insort, col[x])
                            T_time = T_time + time
                if sorted_data is not None:
                    sorted_data.reputation = self.revert_rep(sorted_data.reputation)
                    self.loadtable(sorted_data, self.ui.tableWidget)
                    self.ui.lbl_time_stat.setText(f'{round(T_time, 4)} sec')
                    self.ui.lbl_algo_stat.setText(f'{algo}')
                data_insort.reputation = self.revert_rep(data_insort.reputation)
            else:
                data_insort.reputation = self.revert_rep(data_insort.reputation)

    def changetextoflabel(self):
        self.ui.col_name.setText('Title')
        self.ui.col_grade.setText('answers')
        self.ui.col_year.setText('views')
        self.ui.col_trans.setText('votes')
        self.ui.col_mileage.setText('Tag')
        self.ui.col_fuel.setText('Reputation')
        self.ui.col_cc.setText('Time_stamp')
        self.ui.col_link.setText('Summary')

    def loadtable(self, loaddata, tableType):
        header_label = ['Title', 'No. of answer', 'No. of views', 'No. of votes', 'Tags', 'Reputation of User',
                        'Time Stamp', 'Summary']
        tabledata = []
        for x in range(len(loaddata.title)):
            data = [loaddata.title[x], str(loaddata.answers[x]), str(loaddata.views[x]),
                    str(loaddata.votes[x]), loaddata.users[x], loaddata.reputation[x], str(loaddata.time_stamp[x]),
                    loaddata.summary[x]]
            tabledata.append(data)
        table = tableType
        table.setRowCount(len(tabledata))
        table.setColumnCount(len(tabledata[0]))
        table.setHorizontalHeaderLabels(header_label)
        for row_index, row_data in enumerate(tabledata):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                table.setItem(row_index, col_index, item)

    def loaddata(self):
        if os.path.exists('1.csv'):
            df = pd.read_csv("1.csv")
            datas = data()
            data.title = df['Title'].values.tolist()
            data.answers = df['No. of answers'].values.tolist()
            data.views = df['No. of views'].values.tolist()
            data.votes = df['No. of votes'].values.tolist()
            data.users = df['Users'].values.tolist()
            data.reputation = df['Reputation'].values.tolist()
            data.time_stamp = df['Time_stamp'].values.tolist()
            data.summary = df['Summary'].values.tolist()
            return data
        else:
            return None

    def toggle_frame(self):
        # Check the current visibility of the frame and toggle it
        frame = self.ui.frameSort
        if frame.isHidden():
            self.ui.frameSearch.hide()
            self.ui.frameScrap.hide()
            self.ui.framemain.hide()
            self.ui.tableWidget.show()
            frame.show()
        else:
            self.ui.tableWidget.hide()
            self.ui.framemain.show()
            frame.hide()

    def toggle_frame1(self):
        # Check the current visibility of the frame and toggle it
        frame = self.ui.frameSearch
        if frame.isHidden():
            self.ui.frameSort.hide()
            self.ui.frameScrap.hide()
            self.ui.framemain.hide()
            self.ui.tableWidget.show()
            frame.show()
        else:
            self.ui.tableWidget.hide()
            self.ui.framemain.show()
            frame.hide()

    def toggle_frame2(self):
        # Check the current visibility of the frame and toggle it
        frame = self.ui.frameScrap
        if frame.isHidden():
            self.ui.frameSort.hide()
            self.ui.frameSearch.hide()
            self.ui.framemain.hide()
            self.ui.tableWidget.hide()
            frame.show()
        else:
            self.ui.tableWidget.hide()
            self.ui.framemain.show()
            frame.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
