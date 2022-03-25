import os
import random


class WordList:

    def __init__(self):

        directory = os.getcwd()
        self.words_list_file_path = directory + '\\word-list.txt'

        self.words = []

        self.read_list()

    def read_list(self):

        words_list_file = open(self.words_list_file_path, "r")
        self.words = words_list_file.readlines()

        self.clean_words()

    def clean_words(self):

        for i in range(len(self.words)):

            self.words[i] = self.words[i].strip()

    def print_words(self):

        for word in self.words:
            print(word)

    def get_random_words(self, n):

        random_words_list = []

        for i in range(n):

            random_words_list.append(self.words[self.get_random_index()])

        return random_words_list

    def get_random_index(self):

        return random.randint(0, len(self.words))
