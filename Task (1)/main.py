from os import listdir
from os.path import basename, abspath, join, isfile
from dataclasses import dataclass
from enum import Enum
import re
from math import log

class Mark(Enum):
    SPAM = 'spam'
    NOSPAM = 'ham'
    EMPTY = ''

@dataclass
class EmailSummary:
    path: str
    words: set[str]

@dataclass
class WordStats:
    word: str
    spam: int
    no_spam: int

class File_extensions(Enum):
    TXT = '.txt'
    CSV = '.csv'

class Eparser:

    def __init__(self):
        self.total_spam_words = 0
        self.total_no_spam_words = 0
        self.total_spam_mails = 0
        self.total_no_spam_mails = 0
        self.words_database = dict()

    @property
    def total_mails(self):
        return self.total_no_spam_mails + self.total_spam_mails
    @property 
    def total_words(self):
        return self.total_no_spam_words + self.total_spam_words

    def export_db(self, name):
        with open(name, 'w') as f:
            f.write(f"{self.total_spam_mails} {self.total_no_spam_mails} {self.total_spam_words} {self.total_no_spam_words}\n")
            for stats in self.words_database.values(): f.write(f"{stats.word},{stats.spam},{stats.no_spam}\n")

    def import_db(self, name):
        with open(name, 'r') as f:
            self.total_spam_mails, self.total_no_spam_mails, self.total_spam_words, self.total_no_spam_words = [int(x) for x in f.readline().split(' ')]
            while True:
                line = f.readline()
                if(line == ""): break
                word, spam, no_spam = line.split(',')
                try:
                    word_stats = self.words_database[word]
                    word_stats.spam += int(spam)
                    word_stats.no_spam += int(no_spam)
                except KeyError:
                    self.words_database.update({word: WordStats(word, int(spam), int(no_spam))})
               
    def __repr__(self):
        return f"Всего писем: {self.total_mails} из них {self.total_spam_mails} спама и {self.total_no_spam_mails} не спама.\nВсего слов {self.total_words} из них {self.total_spam_words} спама и {self.total_no_spam_words} не спама."

    def get_current_folder(self): #Возвращает путь к папке со скриптом
        current_folder_path = abspath(__file__).replace(basename(__file__), '')
        return current_folder_path
    
    def correct_path(self, path): #Если путь не является абсолютным, делает его относительно текущей директории
        if path[1:2] != ':':
            return(self.get_current_folder() + path)
        return path

    def parse(self, line : str): #Работает для строк
        file_summary = EmailSummary('string', set())
        line = re.sub(r'\W+',' ', line)
        for word in line.split(' '):
            if word != '':
                file_summary.words.add(word.lower())
        return file_summary
    
    def parse_files_in_folder(self, path, extension): #Парсит все файлы с необходимым расширением по пути
        folder_path = self.correct_path(path)
        try:
            files = [join(folder_path,f) for f in listdir(folder_path) if isfile(join(folder_path, f)) and f[f.rfind('.'):] == extension.value]
        except FileNotFoundError:
            print(f"No files found on the current path [{folder_path}]")
            return []
        return files

    def learn(self, fileStats : EmailSummary, mark, words_old = 0, words_new = 0): #learn on EmailSummary
        for word in fileStats.words:
            try:
                self.words_database[word]
                words_old += 1
            except KeyError:
                self.words_database.update({word : WordStats(word, 0, 0)})
                words_new += 1
            wordStats = self.words_database[word]
            if mark == Mark.SPAM:
                self.total_spam_words += 1
                wordStats.spam += 1
            elif mark == Mark.NOSPAM:
                self.total_no_spam_words += 1
                wordStats.no_spam += 1
        if mark == Mark.SPAM:
            self.total_spam_mails += 1
        elif mark == Mark.NOSPAM:
            self.total_no_spam_mails += 1
        return words_old, words_new

    def check(self, fileStats : EmailSummary) -> Mark: #check on EmailSummary
        isSpam = 0
        isNSpam = 0
        for word in fileStats.words:
            try:
                word_stats = self.words_database[word]
                spam, no_spam = word_stats.spam, word_stats.no_spam
            except KeyError:
                spam, no_spam = 0, 0
            isSpam += log((spam+1)/(self.total_spam_words+self.total_words+2))
            isNSpam += log((no_spam+1)/(self.total_no_spam_words+self.total_words+2))
        result = Mark.SPAM
        if isNSpam > isSpam: result = Mark.NOSPAM
        return result

class EparserTXT(Eparser):
    def parse(self, path : str):
        path = self.correct_path(path)
        file_summary = EmailSummary(path, set())
        with open(file_summary.path, "r") as file:
            lines = file.readlines()
            for line in lines:
                file_summary.words |= super().parse(line).words
        return file_summary
    
    def learn(self, path : str, mark, words_old = 0, words_new = 0):
        fileStats = self.parse(path)
        words_old, words_new = super().learn(fileStats, mark, words_old, words_new)
        return words_old, words_new
    
    def learn_on_folder(self, path : str, mark : Mark):
        path = self.correct_path(path)
        files = self.parse_files_in_folder(path, extension=File_extensions.TXT)
        words_old, words_new = 0,0
        for file in files:
            words_old, words_new = self.learn(file, mark, words_old, words_new)
        print(f"Successfully processed {len(files)} files. {words_new} new words added to the database. {words_old} words updated in the database.")

    def check(self, path : str) -> Mark:
        fileStats = self.parse(path)
        return super().check(fileStats)

class EparseCSV(Eparser):
    def parse(self, path):
        path = self.correct_path(path)
        csv_stats = []
        with open(path, 'r') as csv:
            while True:
                line = csv.readline()
                if line == '': break
                mark, text = line.split(',')[:2]
                try:
                    mark = Mark(mark)
                except ValueError:
                    continue
                line_summary = super().parse(text)
                csv_stats.append((mark, line_summary))
        return csv_stats

    def learn(self, path : str, mark = Mark.EMPTY, words_old = 0, words_new = 0):
        if mark != Mark.EMPTY:
            print(f"Метки из csv файла не будут учитываться, выставленна метка для всех строк: {mark}")
        words_old, words_new = 0,0
        csv_stats = self.parse(path)
        for line_mark, stats in csv_stats:
            if mark != Mark.EMPTY:
                line_mark = mark
            words_old, words_new = super().learn(stats, line_mark, words_old, words_new)
        print(f"Successfully processed {len(csv_stats)} lines. {words_new} new words added to the database. {words_old} words updated in the database.")
        return words_old, words_new
                
    def check(self, path, logging=False):
        csv_stats = self.parse(path)
        correct_cnt, wrong_cnt, total_cnt = 0, 0, 0
        for line_mark, stats in csv_stats:
            result = super().check(stats)
            if logging: print(f"{stats.words} [{line_mark.value}] - > [{result.value}] ", end = '')
            if line_mark == result:
                if logging: print(f"CORRECT")
                correct_cnt += 1
            else:
                if logging: print(f"WRONG")
                wrong_cnt += 1
            total_cnt += 1
        return (total_cnt, wrong_cnt, correct_cnt)


if __name__ == '__main__':
    t = EparseCSV()
    t.learn("check.csv")
    t.export_db('res.csv')
    #t.import_db('res.csv')
    check_result = t.check("check.csv", logging=False)
    print(f"Проверено сообщений: {check_result[0]}. Из них неправильно определенно: {check_result[1]}, правильно: {check_result[2]}")
    print(f"Точность: {round(check_result[2]/check_result[0], 3)}")