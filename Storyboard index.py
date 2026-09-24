#!/usr/bin/env python3
import math
import os
import re
from collections import Counter
from datetime import date
from html import escape

import pandas as pd

stories = "../GitClone-stories"
file_path = stories + "/2026.06.08/CSVExport-2026.06.08_translated.csv"
original_file_path = stories + "/2026.06.08/CSVExport-2026.06.08_d1c06283-3a51-4050-ac6d-ea29ae75f32c (1).csv"
output_dir = "storyboard_output"
df = pd.read_csv(file_path)
original_df = pd.read_csv(original_file_path)

selected_categories = []
selected_countries = ['Italy']
selected_ids = []
category_prefix = '1.2 What you described relates mainly to...(pick up to three)_'
country_prefix = '6.4 My experience is from..._'

category_columns = [f'{category_prefix}{category}' for category in selected_categories if f'{category_prefix}{category}' in df.columns]
if selected_categories and category_columns:
    df = df.loc[df[category_columns].eq(1).any(axis=1)].copy()
elif selected_categories:
    raise ValueError(f'No selected categories found: {selected_categories}')
country_columns = [f'{country_prefix}{country}' for country in selected_countries if f'{country_prefix}{country}' in df.columns]
if selected_countries and country_columns:
    df = df.loc[df[country_columns].eq(1).any(axis=1)].copy()
elif selected_countries:
    raise ValueError(f'No selected countries found: {selected_countries}')
if selected_ids:
    if 'meta_ID' not in df.columns:
        raise ValueError('The selected identifier filter requires a meta_ID column')
    df = df[df['meta_ID'].isin(selected_ids)].copy()

SENTIMENT_COLUMN = '1.3 In general this experience was...'
SENTIMENT_COLORS = {'positive': '#2ca02c', 'negative': '#d62728', 'neutral': '#7f7f7f'}


def sentiment_group(value):
    value = str(value).strip().lower()
    if 'positive' in value:
        return 'positive'
    if 'negative' in value:
        return 'negative'
    return 'neutral'


def save_histogram(values, sentiments, title, output_path, labels, left_label=None, right_label=None,
                   as_percentage=False, show_counts=False, count_values=None, overlay_counts=False):
    data = pd.DataFrame({'value': values, 'sentiment': sentiments}).dropna(subset=['value'])
    if data.empty or not labels:
        return False
    width, height = 1000, 760
    left, right, axis_y, top = 90, 910, 560, 180
    bar_width = (right - left) / len(labels)
    counts = [{group: 0 for group in SENTIMENT_COLORS} for _ in labels]
    for _, row in data.iterrows():
        index = min(int(float(row['value']) * len(labels)), len(labels) - 1)
        counts[index][sentiment_group(row['sentiment'])] += 1
    max_count = max(sum(item.values()) for item in counts) or 1
    if as_percentage:
        tick_svg = ''.join(f'<text x="{left - 14}" y="{axis_y - (axis_y - top) * tick / 100 + 5:.2f}" text-anchor="end">{tick}%</text>' for tick in range(0, 101, 20))
    else:
        step = max(1, math.ceil(max_count / 5))
        tick_svg = ''.join(f'<text x="{left - 14}" y="{axis_y - (axis_y - top) * tick / max_count + 5:.2f}" text-anchor="end">{tick}</text>' for tick in range(0, max_count + 1, step))
    bars, count_labels = [], []
    for index, count in enumerate(counts):
        x = left + index * bar_width + 2
        y = axis_y
        total = sum(count.values())
        for group, color in SENTIMENT_COLORS.items():
            amount = 100 * count[group] / total if as_percentage and total else count[group]
            scale = 100 if as_percentage else max_count
            bar_height = (axis_y - top) * amount / scale
            y -= bar_height
            bars.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width - 4:.2f}" height="{bar_height:.2f}" fill="{color}" />')
        if show_counts and count_values is not None:
            count_labels.append(f'<text x="{left + (index + .5) * bar_width:.2f}" y="{top - 8}" text-anchor="middle" font-size="12">{count_values[index]}</text>')
    overlay, right_axis = '', ''
    if overlay_counts:
        line_values = [sum(item.values()) for item in counts]
        line_max = max(line_values) or 1
        coords = []
        for index, value in enumerate(line_values):
            x1 = left + index * bar_width + 2
            x2 = x1 + bar_width - 4
            y = axis_y - (axis_y - top) * value / line_max
            if index:
                coords.extend([(x1, coords[-1][1]), (x1, y)])
            else:
                coords.append((x1, y))
            coords.append((x2, y))
        points = ' '.join(f'{x:.2f},{y:.2f}' for x, y in coords)
        overlay = f'<polyline points="{points}" fill="none" stroke="#111827" stroke-width="6" />'
        step = max(1, math.ceil(line_max / 5))
        ticks = list(range(0, line_max + 1, step))
        if ticks[-1] != line_max:
            ticks.append(line_max)
        right_axis = ''.join(f'<text x="{right + 14}" y="{axis_y - (axis_y - top) * tick / line_max + 5:.2f}" fill="#111827">{tick}</text>' for tick in ticks)
        right_axis = f'<path d="M {right} {top} L {right} {axis_y}" stroke="#111827" />{right_axis}<text x="{right + 42}" y="{top - 18}" text-anchor="middle" fill="#111827">Absolute count</text>'
    labels_svg = ''.join(f'<text x="{left + (index + .5) * bar_width:.2f}" y="{axis_y + 28}" text-anchor="middle" transform="rotate(35 {left + (index + .5) * bar_width:.2f} {axis_y + 28})">{escape(str(label))} ({count_values[index] if show_counts and count_values is not None else ""})</text>' for index, label in enumerate(labels))
    legend = ''.join(f'<text x="{760 + index * 75}" y="{axis_y + 115}" fill="{color}">{group.title()}</text>' for index, (group, color) in enumerate(SENTIMENT_COLORS.items()))
    limit_svg = ''
    if left_label and right_label:
        limit_svg = f'<text x="{left}" y="{axis_y + 85}">{escape(left_label)}</text><text x="{right}" y="{axis_y + 85}" text-anchor="end">{escape(right_label)}</text>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white" />
<text x="500" y="48" text-anchor="middle" font-size="22">{escape(title)}</text>
<path d="M {left} {top} L {left} {axis_y} L {right} {axis_y}" fill="none" stroke="#39424e" stroke-width="3" />
<g font-size="14">{tick_svg}</g>{''.join(bars)}{''.join(count_labels)}{overlay}<g font-size="14">{labels_svg}</g>{limit_svg}<g font-size="14">{right_axis}</g><g>{legend}</g>
</svg>'''
    with open(output_path, 'w', encoding='utf-8') as plot_file:
        plot_file.write(svg)
    return True


def save_numeric_histogram(dataframe, prefix, title, output_path, labels=None, left_label=None, right_label=None, as_percentage=False, overlay_counts=False):
    column = prefix + '_percentX'
    if column not in dataframe.columns or SENTIMENT_COLUMN not in dataframe.columns:
        return False
    values = pd.to_numeric(dataframe[column], errors='coerce').clip(0, 1)
    return save_histogram(values, dataframe[SENTIMENT_COLUMN], title, output_path, labels or [str(index / 10) for index in range(11)], left_label, right_label, as_percentage=as_percentage, overlay_counts=overlay_counts)


def save_categorical_histogram(dataframe, column, title, output_path, ordered_labels=None, as_percentage=False, show_counts=False, overlay_counts=False):
    if column not in dataframe.columns or SENTIMENT_COLUMN not in dataframe.columns:
        return False
    values = dataframe[column].fillna('Unknown').astype(str)
    labels = [label for label in (ordered_labels or list(dict.fromkeys(values))) if label in set(values)]
    labels.extend(label for label in dict.fromkeys(values) if label not in labels)
    positions = {label: index / max(len(labels) - 1, 1) for index, label in enumerate(labels)}
    counts = [int((values == label).sum()) for label in labels]
    return save_histogram(values.map(positions), dataframe[SENTIMENT_COLUMN], title, output_path, labels, as_percentage=as_percentage, show_counts=show_counts, count_values=counts, overlay_counts=overlay_counts)


def save_one_hot_histogram(dataframe, prefix, title, output_path, as_percentage=False, show_counts=False, overlay_counts=False):
    columns = [column for column in dataframe.columns if column.startswith(prefix)]
    if not columns:
        return False
    labels = [column[len(prefix):].strip() for column in columns]
    values = [next((label for column, label in zip(columns, labels) if row[column] == 1), 'Unknown') for _, row in dataframe[columns].iterrows()]
    temp = dataframe.copy()
    temp['__plot_value'] = values
    return save_categorical_histogram(temp, '__plot_value', title, output_path, ordered_labels=labels, as_percentage=as_percentage, show_counts=show_counts, overlay_counts=overlay_counts)


def save_wordcloud(dataframe, column, title, output_path):
    if column not in dataframe.columns:
        return False
    stop_words = {'about', 'after', 'again', 'also', 'and', 'are', 'been', 'being', 'but', 'can', 'could', 'did', 'for', 'from', 'have', 'how', 'into', 'just', 'more', 'most', 'not', 'our', 'out', 'that', 'the', 'their', 'there', 'they', 'this', 'was', 'were', 'what', 'when', 'where', 'which', 'who', 'will', 'with', 'would', 'you', 'your', 'a', 'an', 'as', 'at', 'be', 'in', 'is', 'it', 'of', 'on', 'or', 'to', 'we', 'i', 'my', 'me', 'ha', 'yet', 'one', 's', 'nt'}
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", ' '.join(dataframe[column].dropna().astype(str)).lower())
    frequencies = Counter(word for word in words if word not in stop_words and len(word) > 1)
    top_words = frequencies.most_common(50)
    if not top_words:
        return False
    colors = ['#0f766e', '#2563eb', '#c2410c', '#7c3aed', '#be123c', '#4d7c0f']
    maximum = top_words[0][1]
    positions = [(120 + index * 137 % 760, 130 + index * 83 % 430) for index in range(len(top_words))]
    word_svg = ''.join(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{10 + int(40 * count / maximum)}" fill="{colors[index % len(colors)]}" opacity="0.82">{escape(word)}</text>' for index, ((word, count), (x, y)) in enumerate(zip(top_words, positions)))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650"><rect width="100%" height="100%" fill="white" /><text x="450" y="48" text-anchor="middle" font-size="22">{escape(title)}</text>{word_svg}</svg>'
    with open(output_path, 'w', encoding='utf-8') as plot_file:
        plot_file.write(svg)
    return True


def markdown_line_breaks(value):
    return re.sub(r'\r?\n', '  \n', str(value))


def story_value(row, column):
    value = row.get(column, '') if row is not None else ''
    return '' if pd.isna(value) else value


os.makedirs(output_dir, exist_ok=True)
plot_specs = []


def add_plot(filename, title, writer):
    if writer(os.path.join(output_dir, filename)):
        plot_specs.append((title, filename))


add_plot('histogram_1_3.svg', '1.3 Experience sentiment histogram', lambda path: save_categorical_histogram(df, SENTIMENT_COLUMN, SENTIMENT_COLUMN, path, ['Very positive', 'Positive', 'Neutral', 'Negative', 'Very negative']))
numeric_questions = [
    ('2.1 In the experience you shared, what matters most are...', 'histogram_2_1.svg', 'Values and traditions', 'Change and innovation'),
    ('2.2 In the experience you shared, others behave...', 'histogram_2_2.svg', 'As expected', 'Unusually'),
    ('2.3 In the experience you shared, everybody is treated ...', 'histogram_2_3.svg', "The same but it's not ok", "Differently but it's not ok"),
    ('2.4 In the experience you shared, you feel the government...', 'histogram_2_4.svg', 'Interferes too much', "Doesn't care at all"),
]
for prefix, filename, left_label, right_label in numeric_questions:
    add_plot(filename, f'{prefix} histogram', lambda path, prefix=prefix, left_label=left_label, right_label=right_label: save_numeric_histogram(df, prefix, prefix, path, left_label=left_label, right_label=right_label, as_percentage=True, overlay_counts=True))

age_order = ['16 - 24', '25 - 34', '34 - 54', '55 - 65', 'over 65']
add_plot('histogram_6_3.svg', '6.3 Experience frequency histogram', lambda path: save_categorical_histogram(df, '6.3 The experience you described was...', '6.3 The experience you described was...', path, ['not sure', 'a one time occurrence', 'rare but it happens from time to time', 'somewhat common', 'very common'], as_percentage=True, show_counts=True, overlay_counts=True))
add_plot('histogram_6_4.svg', '6.4 Experience origin histogram', lambda path: save_one_hot_histogram(df, country_prefix, country_prefix, path, as_percentage=True, show_counts=True, overlay_counts=True))
add_plot('histogram_6_6.svg', '6.6 Age histogram', lambda path: save_categorical_histogram(df, '6.6 I am ...', '6.6 I am ...', path, age_order, as_percentage=True, show_counts=True, overlay_counts=True))
add_plot('histogram_6_5.svg', '6.5 Identity histogram', lambda path: save_categorical_histogram(df, '6.5 I identify as...', '6.5 I identify as...', path, as_percentage=True, show_counts=True, overlay_counts=True))
for column, title, filename in [('EU is like', '5.1 For me, the EU is like...', 'wordcloud_5_1.svg'), ('Europe is like', '5.2 For me, Europe is like...', 'wordcloud_5_2.svg'), ('Democracy is like', '5.3 For me, democracy is like...', 'wordcloud_5_3.svg'), ('Who should hear', '6.1 Who should hear your story?', 'wordcloud_6_1.svg'), ('Question', '6.2 If you could ask one question to people in power, what would it be?', 'wordcloud_6_2.svg')]:
    add_plot(filename, f'{title} word cloud', lambda path, column=column, title=title: save_wordcloud(df, column, title, path))

category_columns = [column for column in df.columns if column.startswith(category_prefix)]
cat_stories = {column.split('_', 1)[1]: df[df[column] == 1][['Title', 'Content']].to_dict('records') for column in category_columns}
cat_counts = {cat: len(records) for cat, records in cat_stories.items()}
sorted_cats = sorted(cat_counts.items(), key=lambda item: item[1], reverse=True)
all_story_records = df[['Title', 'Content']].drop_duplicates().to_dict('records')
story_ids = {(story['Title'], story['Content']): index for index, story in enumerate(all_story_records, 1)}
story_categories = {}
for category, records in cat_stories.items():
    for story in records:
        story_categories.setdefault((story['Title'], story['Content']), []).append(category)
story_indexed = []
for story in all_story_records:
    mask = (df['Title'] == story['Title']) & (df['Content'] == story['Content'])
    story_indexed.append({'id': story_ids[(story['Title'], story['Content'])], 'Title': story['Title'], 'Content': story['Content'], 'row': df[mask].iloc[0]})

original_content_column = '1. Please describe a recent experience of you in our society: Something that is important to you and you would tell a good friend. Share your experience here in a couple of sentences. The experience can be positive or negative. There are no right or wrong answers.'
original_title_column = '1.1 What title would you give your experience?'
original_stories = original_df.set_index('id').to_dict('index') if 'id' in original_df.columns else {}
generated_date = date.today().isoformat()
with open(os.path.join(output_dir, 'stories.md'), 'w', encoding='utf-8') as report:
    report.write(f'Storyboard\n\nGenerated on: {generated_date}\n\n')
    report.write(f"Selected categories: {', '.join(selected_categories) if selected_categories else 'All'}  \n")
    report.write(f"Selected countries: {', '.join(selected_countries) if selected_countries else 'All'}  \n")
    report.write(f"Selected story IDs: {', '.join(selected_ids) if selected_ids else 'All'}\n\n")
    report.write('# Story summary\n\n')
    report.write(f'Unique stories found: {len(story_ids)}\n\n')
    report.write(f'Total number of category assignments: {sum(cat_counts.values())}\n\n')
    report.write('# Categories sorted by story count:\n\n')
    for category, count in sorted_cats:
        report.write(f'{category}: {count} stories\n\n')
    report.write('# Plots\n\n')
    for title, filename in plot_specs:
        report.write(f'## {title}\n\n![{title}]({filename})\n\n')
        if filename == 'histogram_6_4.svg':
            for column in df.columns:
                if column.startswith(country_prefix):
                    count = int(df[column].fillna(0).sum())
                    if count:
                        report.write(f'- {column[len(country_prefix):]}: {count} stories\n')
            report.write('\n')
    report.write('# All unique stories with their number and full text:\n\n')
    for story in sorted(story_indexed, key=lambda item: item['id']):
        report.write(f"## {story['id']}. {story['Title']}\n\n{markdown_line_breaks(story['Content'])}\n\n")
        row = story['row']
        original = original_stories.get(story_value(row, 'id'))
        language = story_value(original, 'meta_selected_language') if original else ''
        if original and str(language).lower() not in ('', 'en', 'english'):
            report.write(f'<u>Original title ({language})</u> : {story_value(original, original_title_column)}\n\n')
            report.write(f'<u>Original content ({language})</u> :\n\n{markdown_line_breaks(story_value(original, original_content_column))}\n\n')
        metadata = [
            ('Origin', ', '.join(column[len(country_prefix):] for column in df.columns if column.startswith(country_prefix) and row.get(column) == 1)),
            ('Language', story_value(row, 'meta_selected_language')),
            ('Unique identifier', story_value(row, 'meta_ID')),
            ('EU is like', story_value(row, 'EU is like')),
            ('Europe is like', story_value(row, 'Europe is like')),
            ('Democracy is like', story_value(row, 'Democracy is like')),
            ('Who should hear this', story_value(row, 'Who should hear')),
            ('Question', story_value(row, 'Question')),
            ('The experience was', story_value(row, SENTIMENT_COLUMN)),
        ]
        for label, value in metadata:
            report.write(f'<u>{label}</u> : {markdown_line_breaks(value)}\n\n')
        key = (story['Title'], story['Content'])
        report.write(f'<u>This story also appears in</u> : {", ".join(story_categories.get(key, []))}\n\n')

print(f'Generated on: {generated_date}')
print(f'Unique stories found: {len(story_ids)}')
