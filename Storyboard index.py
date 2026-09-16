#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 18:06:30 2026

@author: rbonino
Create a storyboard with an index of stories

"""
import pandas as pd

# Load the CSV file into a pandas DataFrame
stories = "../GitClone-stories"  # where is the stories repo cloned to */
file_path = stories + "/2026.06.08/CSVExport-2026.06.08_chargediandDigicomEURAI.csv"
# file_path = "./cca+climate/cca+climate.csv"
df = pd.read_csv(file_path)


# Display the first few rows to verify
print(df.head())


# After loading the DataFrame and defining category_prefix
category_prefix = '1.2 What you described relates mainly to...(pick up to three)_'

# Get all category columns
category_columns = [col for col in df.columns if col.startswith(category_prefix)]

# Create a dictionary to hold stories by cat
cat_stories = {}



# Populate the dictionary
for category_col in category_columns:
    cat_name = category_col.split('_', 1)[1]
    # Get all rows where this cat is assigned (value is 1)
    stories_in_cat = df[df[category_col] == 1][["Title", "Content"]].to_dict('records')
    cat_stories[cat_name] = stories_in_cat
# Count stories per category
cat_counts = {cat: len(stories) for cat, stories in cat_stories.items()}

# Sort categories by story count in descending order
sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)

# Build a unique story id mapping for all stories (title + content pairs)
all_story_records = df[["Title", "Content","EU is like"]].drop_duplicates().to_dict("records")
story_ids = {}
for idx, story in enumerate(all_story_records, 1):
    key = (story["Title"], story["Content"])
    story_ids[key] = idx

# Build reverse lookup for output ordering
story_indexed = [{
    "id": story_ids[(story["Title"], story["Content"])],
    "Title": story["Title"],
    "Content": story["Content"],
} for story in all_story_records]
story_indexed.sort(key=lambda x: x["id"])

# Print sorted categories and their story counts
print("\nCategories sorted by story count:")
for cat, count in sorted_cats:
    print(f"{cat}: {count} stories")

# Print the total number of stories
total_cat_assignments = sum(cat_counts.values())
print(f"Unique stories found: {len(story_ids)}")
print(f"\nTotal number of category assignments: {total_cat_assignments}")

# Save  stories to a file
with open("stories.md", "w", encoding="utf-8") as f:
    f.write("Storyboard \n\n")
    f.write(f"Unique stories found: {len(story_ids)}\n\n")
    f.write(f"Total number of category assignments: {total_cat_assignments}\n\n")

    # Save sorted categories 
    f.write("# Categories sorted by story count:\n\n")
    for cat, count in sorted_cats:
        f.write(f"{cat}: {count} stories\n\n")

    # Print stories for each category with a unique global ID per title/content
    for cat, stories in cat_stories.items():
        print(f"\nCategory: {cat}")
        print(f"Number of stories: {len(stories)}")
        print("Stories:")
        for story in stories:
           story_id = story_ids[(story["Title"], story["Content"])]
           print(f"--{story_id}. {story['Title']}")


    # Save stories by category with unique IDs and final story list 
    f.write("# Categories sorted by story count:\n\n")
    for cat, stories in cat_stories.items():
        f.write(f"\n ## Category: {cat}\n\n")
        f.write(f"Number of stories: {len(stories)}\n\n")
        f.write(" Stories id:\n\n")
        for story in stories:
            story_id = story_ids[(story["Title"], story["Content"])]
            f.write(f" -{story_id}. {story['Title']}\n")
            f.write("\n")

    # Save the story index to a file
    f.write("# All unique stories with their number and full text:\n")
    for story in story_indexed:
        f.write(f"## {story['id']}. {story['Title']}\n\n")
        f.write(f"{story['Content']}\n\n")

    # Print the story index
    print("\nAll unique stories with their number and full text:")
    for story in story_indexed:
        print(f"{story['id']}. {story['Title']}")
        print(f"{story['Content']}\n")

