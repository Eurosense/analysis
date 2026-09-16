#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 17:47:37 2025

@author: roberto bonino
Build a storyboard from a .csv corpus of Eurosense stories.
Group the stories by categories chosen
"""

import pandas as pd
import os

# Load your CSV file that cntains the stories to process
# Before processing, remeber to delete the frst two lines wich contain metadata
# file_path = "AI stories/AI stories - stories.csv"

IDselect = 1  #set to 1 if you want to select specific metaID
metaID = "MVE"

print ( os.listdir("Data"))
file_path = "./Data/2026.06.08/CSVExport-2026.06.08_translated.csv"
##file_path = "./cca+climate/cca+climate.csv"

# choose how many row for testing
#df = pd.read_csv(file_path,nrows=50)
df = pd.read_csv(file_path)

# Safely convert meta_started to datetime if present.
# Handle numeric epoch in ms or s, and fallback to parsing strings.
if 'meta_started' in df.columns:
    num = pd.to_numeric(df['meta_started'], errors='coerce')
    if num.notna().any():
        maxv = num.max()
        if maxv > 1e12:
            df['meta_started_dt'] = pd.to_datetime(num, unit='ms', errors='coerce')
        elif maxv > 1e9:
            df['meta_started_dt'] = pd.to_datetime(num, unit='s', errors='coerce')
        else:
            df['meta_started_dt'] = pd.to_datetime(df['meta_started'], errors='coerce')
    else:
        df['meta_started_dt'] = pd.to_datetime(df['meta_started'], errors='coerce')

print(df.head())



print(df.head())

md_path = "StoryboardTest.md"  #The output file

# Each category is recorded as a separate column with a name that starts with category_prefix
# if the category is assigned to a row, the related column is set to 1, otherwise 0
category_prefix = '1.2 What you described relates mainly to...(pick up to three)_'
# capture all the categories in the category
category_columns = [col for col in df.columns if col.startswith(category_prefix)]

# Each country is recorded as a separate column with a name that starts with country_prefix
# if the country is assigned to a row, the related column is set to 1, otherwise 0
country_prefix = '6.4 My experience is from..._'


iprint =1
storyCount=0

if  iprint :  print (category_columns)
with open(md_path, "w", encoding="utf-8") as md_file:
 
    # Loop over the categories  listed in category_col
    for category_col in category_columns:
       
        # Extract the category name after the prefix
        category_name = category_col.split('_', 1)[1]
        if  iprint :  print(f"\n--- Rows belonging to category: {category_name}")
        md_file.write(f"# \n## {category_name}\n\n")

        # Find rows where the category column is 1
        rows_in_category = df[df[category_col] == 1]


       
        # Loop over these rows
        for index, row in rows_in_category.iterrows():
             
            #print ( row["6.4 My experience is from..."])
            if IDselect:  #skip if condition NOT met
               if  row["meta_ID"] != metaID:
               # if  row["6.4 My experience is from..."] != "Germany":
               #     continue
               # ageGroup = row["6.6 I am ..."]
               # if (ageGroup != "55 - 65" and ageGroup != "over 65"):
                   continue
            start = row['meta_started']   
            # if start < 1779468458960:
            #     print(f" -----select  {row['meta_started']} {row['meta_started_dt']} ")
            #     continue

            storyCount = storyCount +1
            print(f" --------------------------storyCount {storyCount}   index :{index }")
            categories = ""
            
            # Collect all categories for this row
            for col in category_columns:
                if row[col] == 1:
                    cat_name = col.split('_', 1)[1]
                    categories += cat_name + " ; "
            # Add 'Other' text if present
            other_col = '1.2 What you described relates mainly to...(pick up to three)_Other, please specify'
            other_col = 'Other'
            if other_col in df.columns and pd.notna(row[other_col]) and row[other_col].strip() != '':
               # categories.append(row[other_col])
                categories += row[other_col] + " ; "
                
            #retrieve the countries
            countries =''
            for col in df.columns: 
                if col.startswith(country_prefix):
                    if row[col] == 1:
                        country_name = col.split('_', 1)[1]
                        countries += country_name + " ; "
                
            title = row["Title"]
            content = row["Content"]

            print(f" TITLE {storyCount}  {title} index: {index}")  
            md_file.write(f"\n###  {title}   \n {content} <br>")

            md_file.write(f"  \n <u>Original title:</u> {row['1.1 What title would you give your experience?']} <br>")
            md_file.write(f" <u>    Origin and language  </u>:   {countries}  {row['meta_selected_language']}  <br>")
           
                 
            print(f" -----started  {row['meta_started']} {row['meta_started_dt']} ")
           
           
            md_file.write(f"<u>Time stamp</u>:  {row['meta_started']}   {row['meta_started_dt']}<br>")
            md_file.write(f"<u>Unique identifier</u>: {row['meta_ID']}<br>")
            md_file.write(f"<u>EU is like </u>: {row['EU is like']}<br>")
            md_file.write(f"<u>Europe is like</u>: {row['Europe is like']}<br>")
            md_file.write(f"<u>Democracy is like</u>: {row['Democracy is like']}<br>")
            md_file.write(f"<u>Who should hear</u>: {row['Who should hear']}<br>")
            md_file.write(f"<u>Question</u>: {row['Question']}<br>")
            md_file.write(f"<u>The experience was</u>: {row['1.3 In general this experience was...']}")
            md_file.write(f"<u> and</u>: {row['6.3 The experience you described was...']}<br>")
        
            md_file.write(f"\n\nThis story also appears in {categories} <br>") 
            md_file.write(f"<u>Original text</u>:{row['1. Please describe a recent experience of you in our society: Something that is important to you and you would tell a good friend. Share your experience here in a couple of sentences. The experience can be positive or negative. There are no right or wrong answers.']}<br>")

            # print(f"  Row {index}: {categories} {title}  ")  
        
print(f"Markdown file saved to {md_path}")