#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 18:20:34 2025
create a set of wordcloud for each selected country for the questions
["Democracy is like","Europe is like","EU is like"]

@author: rbonino
"""


import pandas as pd
# import wordcloud
# import numpy as np
import os
from os import path
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')


# Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('punkt_tab')



def preprocess_text(text, deb=0):
    """

    Parameters
    ----------
    text : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    # Initialize the lemmatizer
    lemmatizer = WordNetLemmatizer()

    if deb == 0:
        print("\n" + " original \n" + text)

    # lower case string
    text = text.lower()
    if deb == 1:
        print("\n" + " lower cases \n" + text)

    # Tokenize the text into words
    words = word_tokenize(text)

    # stopwords
    filtered_words = []
    english_stopwords = stopwords.words("english")
    english_stopwords.extend(["ha", "yet", "one", "s", ",", "...", "n't"])
    for word in words:
        print("\n  - " + word)
        if word not in english_stopwords:
            filtered_words.append(word)
    if deb == 1:
        print(english_stopwords)
        print("\n" + " filtered_list \n")
        print(filtered_words)

# # stemming
#     stemmer = PorterStemmer()
#     stemmed_words = [stemmer.stem(word) for word in filtered_words]

    # Lemmatize each word
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    if deb == 1:
        print("\n" + " lemmatized words \n")

        for item1, item2 in zip(filtered_words, filtered_words):
            print(f"{item1:<15} {item2:<15} ")

    # Join the words back into a single string
    return ' '.join(lemmatized_words)


"""
retrieve the data file 
"""

# use the follwing to read a  file through its URL
# sheet_url = "https://docs.google.com/spreadsheets/d/1SQ9bMEA8_IAUQMjiNGNaHVsqjPSvL90GI2y3ZXvYrvI/edit?gid=1345744246#gid=1345744246"
# url_1 = sheet_url.replace('/edit?gid=', '/export?format=csv&amp;gid=')


current_directory = os.getcwd()
# data = pd.read_csv(url_1)

data = pd.read_csv('Data/CSVExport_2025.07.27 - translated.csv')
print(data.head())

"""
print out some summary to a file """
file = open("Most Commmon words.txt", "w")
file.write("Most common words \n")

file.write("There are {} observations and {} features in this dataset. \n"
           .format(data.shape[0], data.shape[1]))


# loop on the columns
columns = ["Democracy is like", "Europe is like", "EU is like", "Who should hear", "Question"]
# the columns to process
countries = ["all", "Austria", "Belgium", "Cyprus","France", "Germany", "Italy", "Netherlands", "Portugal", "Spain"]
# countries = ["Austria"]

for country in countries:
    for col in columns:

        df = pd.DataFrame(data)

        if country == "all":  # pass unfiltered data
            filtered_df = data
        else:    # Filter the DataFrame based on the given value of the 'country' column
            filtered_df = data[data['6.4 My experience is from...'] == country]

        # Select the 'Value' column from the filtered DataFrame
        selected_values = filtered_df[col]

        # Merge the selected elements into a single string
        merged_string = filtered_df[col].str.cat(sep=' ')


        # preprocess
       
        merged_string = preprocess_text(merged_string)
        more_stopwords = {"ha", "yet", "one", "s"}
        STOPWORDS.update(more_stopwords)
        # create wordcloud object
        wc = WordCloud(background_color="white",
                       max_words=200,
                       max_font_size=50)
#                       stopwords=STOPWORDS)
        wc.generate(merged_string)
        # Print thr first 10 key by decreasing value
        # Sort the dictionary keys by their values in decreasing order
        List = list(wc.words_.items())
        newlist = sorted(List, key=lambda x: x[1], reverse=True)

        # save wordcloud
        wc.to_file(path.join(current_directory, "Images",
                              country + "_" + col + ".png"))

        file.write("\n" + country + " " + col + "\n")
        for i in range(15):
            file.write(newlist[i][0] + "  " +
                       str(merged_string.count(newlist[i][0])) + "\n")


file.close()
print("File opened successfully!!")
print(current_directory)
