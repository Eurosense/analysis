#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 18:06:30 2026

@author: rbonino
"""
import pandas as pd
import matplotlib.pyplot as plt
import textwrap

# Terminal underline helper
UNDERLINE = '\033[4m'
RESET = '\033[0m'

def underline(text: str) -> str:
    return f"{UNDERLINE}{text}{RESET}"

# Load the CSV file

file_path = "../R Eurosense Data/2026.04.13/CSVExport_2026.04.13_translated.csv"

df = pd.read_csv(file_path)

# Plot distribution of experience sentiment by country for Housing and Living Conditions
experience_col = '1.3 In general this experience was...'
housing_col = '1.2 What you described relates mainly to...(pick up to three)_Housing and Living Conditions'
country_prefix = '6.4 My experience is from..._'

housing_df = df[df[housing_col] == 1].copy()

country_cols = [col for col in housing_df.columns if col.startswith(country_prefix)]

content_col = 'Content'
title_col = 'Title'
original_title_col = '1.1 What title would you give your experience?'
origin_col = 'Origin' if 'Origin' in housing_df.columns else None
language_col = 'language'
eu_col = 'EU is like'
europe_col = 'Europe is like'
democracy_col = 'Democracy is like'
who_should_hear_col = 'Who should hear'
question_col = 'Question'
experience_was_col = '6.3 The experience you described was...'
meta_id_col = 'meta_ID'

meta_cols = [original_title_col, language_col, eu_col, europe_col, democracy_col, who_should_hear_col, question_col, experience_was_col, meta_id_col]
if origin_col:
    meta_cols.insert(1, origin_col)

country_df = housing_df[[experience_col, title_col, content_col] + meta_cols + country_cols].melt(
    id_vars=[experience_col, title_col, content_col] + meta_cols,
    value_vars=country_cols,
    var_name='country_col',
    value_name='has_experience'
)
country_df = country_df[country_df['has_experience'] == 1].copy()
country_df['country'] = country_df['country_col'].str.replace(country_prefix, '', regex=False)

sentiment_order = [
    'Very positive',
    'Positive',
    'Neutral',
    'I don’t know / Not sure',
    'Negative',
    'Very negative'
]
colors = [
    '#006400',  # dark green
    '#a6d96a',  # light green
    '#f5f5dc',  # beige
    '#808080',  # gray
    '#ff7f7f',  # light red
    '#a50026'   # dark red
]

experience_counts = country_df.groupby(['country', experience_col]).size().unstack(fill_value=0)
experience_counts = experience_counts.reindex(columns=sentiment_order, fill_value=0)
experience_counts['Total'] = experience_counts.sum(axis=1)
experience_counts = experience_counts[experience_counts['Total'] > 0]
experience_counts = experience_counts.sort_values(by='Total', ascending=False)
experience_counts_pct = experience_counts.drop(columns='Total').div(experience_counts['Total'], axis=0) * 100

print('\nHousing and Living Conditions sentiment distribution by country (percent):')
print(experience_counts_pct.round(1))
print('\nNumber of entries per country:')
print(experience_counts['Total'])

story_groups = []
meta_cols_for_story = [title_col, original_title_col, content_col]
if origin_col:
    meta_cols_for_story.append(origin_col)
meta_cols_for_story += [language_col, eu_col, europe_col, democracy_col, who_should_hear_col, question_col, experience_was_col, meta_id_col]

for country in experience_counts.index:
    country_group = country_df[country_df['country'] == country]
    for sentiment in sentiment_order:
        sentiment_group = country_group[country_group[experience_col] == sentiment]
        if sentiment_group.empty:
            continue
        # Group by content/title and get first non-null meta_ID
        stories_list = []
        for (title, content), group in sentiment_group.groupby([title_col, content_col]):
            story_dict = {}
            for col in meta_cols_for_story:
                # Get first non-null value, else get first value
                non_null_vals = group[col].dropna()
                if len(non_null_vals) > 0:
                    story_dict[col] = non_null_vals.iloc[0]
                else:
                    story_dict[col] = group[col].iloc[0]
            stories_list.append(story_dict)
        story_groups.append({
            'country': country,
            'sentiment': sentiment,
            'stories': stories_list,
        })

story_counter = 1
for group in story_groups:
    for story in group['stories']:
        story['index'] = story_counter
        story_counter += 1

print('\nStory contents grouped by country and sentiment:')
for group in story_groups:
    print(f"\n=== Country: {group['country']} ===")
    print(f"\n-- Sentiment: {group['sentiment']} --")
    for story in group['stories']:
        origin_val = story.get(origin_col, 'NA') if origin_col else 'NA'
        print(f"{story['index']}. {story[content_col]}")
        print(f"{underline('Original title')}: {story.get(original_title_col, story.get(title_col, 'NA'))}")
        print(f"{underline('Origin and language')}: {origin_val} ; {story.get(language_col, 'NA')}")
        print(f"{underline('Unique identifier')}: {story.get(meta_id_col, 'NA')}")
        print(f"{underline('EU is like')}: {story.get(eu_col, 'NA')}")
        print(f"{underline('Europe is like')}: {story.get(europe_col, 'NA')}")
        print(f"{underline('Democracy is like')}: {story.get(democracy_col, 'NA')}")
        print(f"{underline('Who should hear')}: {story.get(who_should_hear_col, 'NA')}")
        print(f"{underline('Question')}: {story.get(question_col, 'NA')}")
        print(f"{underline('The experience was')}: {story.get(experience_was_col, 'NA')}")
        print(underline('This story also appears in'))

# Build chart figure
ax = experience_counts_pct.plot(
    kind='bar',
    stacked=True,
    figsize=(14, 8),
    color=colors
)
ax.set_title('Sentiment distribution (100% normalized) for Housing and Living Conditions by Country')
ax.set_xlabel('Country')
ax.set_ylabel('Percent of stories')
ax.legend(title='Experience sentiment', bbox_to_anchor=(1.04, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')

for idx, total in enumerate(experience_counts['Total']):
    ax.text(idx, 101, str(total), ha='center', va='bottom', fontsize=8)

plt.ylim(0, 110)
plt.tight_layout()
plt.savefig('housing_sentiment_by_country_pct.png', dpi=200)

# Create a Markdown report with TOC, plot link, and story content
md_lines = []
md_lines.append('# Housing Sentiment Report')
md_lines.append('')
md_lines.append('## Summary')
md_lines.append('')
md_lines.append('### Number of entries per country')
md_lines.append('')
md_lines.append('| Country | Total |')
md_lines.append('|---|---:|')
for country, total in experience_counts['Total'].items():
    md_lines.append(f'| {country} | {total} |')
md_lines.append('')
md_lines.append('### Sentiment distribution by country (percent)')
md_lines.append('')
header = ['Country'] + sentiment_order
md_lines.append('|' + '|'.join(header) + '|')
md_lines.append('|' + '|'.join(['---'] * len(header)) + '|')
for country, row in experience_counts_pct.round(1).iterrows():
    values = [country] + [f'{row[sentiment]:.1f}' for sentiment in sentiment_order]
    md_lines.append('|' + '|'.join(values) + '|')
md_lines.append('')

# Story content by country and sentiment
md_lines.append('## Story contents grouped by country and sentiment')
md_lines.append('')
current_country = None
for group in story_groups:
    if group['country'] != current_country:
        current_country = group['country']
        md_lines.append(f'## Country: {current_country}')
        md_lines.append('')
    md_lines.append(f'### {group["sentiment"]}')
    md_lines.append('')
    for story in group['stories']:
        origin_val = story.get(origin_col, 'NA') if origin_col else 'NA'
        md_lines.append(f'**{story["index"]}. {story[title_col]}**')
        md_lines.append('')
        wrapped_content = textwrap.wrap(story[content_col], width=100)
        for line in wrapped_content:
            md_lines.append(line)
        md_lines.append('')
        md_lines.append(f'<u>Original title</u>: {story.get(original_title_col, story.get(title_col, "NA"))}')
        md_lines.append(f'<br><u>Origin and language</u>: {origin_val} ; {story.get(language_col, "NA")}')
        md_lines.append(f'<br><u>Unique identifier</u>: {story.get(meta_id_col, "NA")}')
        md_lines.append(f'<br><u>EU is like</u>: {story.get(eu_col, "NA")}')
        md_lines.append(f'<br><u>Europe is like</u>: {story.get(europe_col, "NA")}')
        md_lines.append(f'<br><u>Democracy is like</u>: {story.get(democracy_col, "NA")}')
        md_lines.append(f'<br><u>Who should hear</u>: {story.get(who_should_hear_col, "NA")}')
        md_lines.append(f'<br><u>Question</u>: {story.get(question_col, "NA")}')
        md_lines.append(f'<br><u>The experience was</u>: {story.get(experience_was_col, "NA")}')
        md_lines.append(f'<br><u>This story also appears in</u>')
        md_lines.append('')

with open('housing_sentiment_by_country_pct.md', 'w', encoding='utf-8') as md_file:
    md_file.write('\n'.join(md_lines))
