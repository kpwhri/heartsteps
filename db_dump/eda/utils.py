from config import MONGO_DB_URI_DESTINATION
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import uuid
import datetime
import subprocess
from matplotlib.patches import Patch
from pptx import Presentation

def get_database(uri:str, database_name:str):
    client = MongoClient(uri)
    return client[database_name]

def get_participant_list():
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    participants = db['participants']
    return list(participants.distinct(key='user_id'))

def get_intervention_daily_df(original):
    """
    Get the intervention daily dataframe
    
    :param original: the original dataframe
    :return: the intervention daily dataframe
    """
    new_df = original.query('day_index >= 10 and day_index <= 252').copy()
    new_df['day_index'] = new_df['day_index'].astype(int, errors='ignore')
    new_df['level_int'] = new_df['level_int'].astype(int, errors='ignore')
    return new_df


def draw_heatmap(df, index, columns, values, legend_labels, xlabel, ylabel, legend_title, figure_name, output_dir, cm_name='coolwarm') -> str:
    """
    Draw a heatmap of the given dataframe

    :param df: dataframe
    :param index: index column name
    :param columns: columns column name
    :param values: values column name
    :param legend_labels: legend labels
    :param xlabel: x label
    :param ylabel: y label
    :param legend_title: legend title
    :param figure_name: figure name
    :param output_dir: output directory
    :param cm_name: colormap name
    :return: figure path
    """
    # Create a figure
    plt.figure(figsize=(10, 5))

    # Colormap settings
    cm = plt.cm.get_cmap(cm_name)

    # Create a pivot table
    heatmap_data = df.pivot_table(index=index, columns=columns, values=values, aggfunc=np.sum)

    # Draw a heatmap with the numeric values in each cell
    if legend_labels is None:
        ax = sns.heatmap(heatmap_data, cmap=cm_name, cbar=True)
    else:
        ax = sns.heatmap(heatmap_data, cmap=cm_name, cbar=False)

    # Add title, legend and labels
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if legend_labels is not None:
        # Manually set the level labels
        legend_colors = [cm(x/(len(legend_labels)-1)) for x in range(len(legend_labels))]
        legend_patches = [Patch(color=color, label=label) for color, label in zip(legend_colors, legend_labels)]
        ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=len(legend_labels), title=legend_title)
    
    # Save heatmap to file
    figure_filepath = get_uuid4_filename(figure_name, output_dir)
    plt.savefig(figure_filepath, bbox_inches='tight', dpi=200)

    # Close the figure
    plt.close()
    return figure_filepath


def get_uuid4_filename(filename, output_dir=None):
    """
    Get a UUID4 filename
    :param filename: the original filename
    :return: the UUID4 filename
    """
    filename, ext = os.path.splitext(filename)

    if output_dir is not None:
        return os.path.join(output_dir, '{}_{}{}'.format(filename, uuid.uuid4(), ext))
    else:
        return '{}_{}{}'.format(filename, uuid.uuid4(), ext)


class JWPresentation:
    """
    JustWalk Presentation
    """
    def __init__(self):
        """
        Initialize the presentation
        """
        self.prs = Presentation()
        self.title_slide_layout = self.prs.slide_layouts[0]
        self.contents_slide_layout = self.prs.slide_layouts[1]
        self.__add_title_slide()
        self.toc = {}
        
    def __add_title_slide(self):
        """
        Add the title slide
        """
        title_text = "JustWalk JITAI Data Visualization"
        subtitle_text = "Junghwan Park\n{}".format(pd.Timestamp.today().strftime('%Y-%m-%d'))

        slide = self.prs.slides.add_slide(self.title_slide_layout)
        title = slide.placeholders[0]
        subtitle = slide.placeholders[1]

        title.text = title_text
        subtitle.text = subtitle_text

    def build(self):
        """
        Build the presentation
        """
        self.__section_slide(self.toc)

    def __section_slide(self, toc_item):
        """
        Add a section slide

        :param toc_item: the toc item
        """
        slide = self.prs.slides.add_slide(self.contents_slide_layout)
        title = slide.shapes.title
        title.text = toc_item['title']

        item_texts = [item['title'] for item in toc_item['items']]
        contents = slide.placeholders[1]
        tf = contents.text_frame
        tf.text = '\n'.join(item_texts)

        self.__add_slides(toc_item['items'])

    def __add_slides(self, toc_items):
        """
        Add slides

        :param toc_items: the toc items
        """
        for toc_item in toc_items:
            if toc_item['type'] == 'section':
                self.__section_slide(toc_item)
            elif toc_item['type'] == 'slide':
                self.__normal_slide(toc_item)
            else:
                raise ValueError(
                    'Invalid toc_item type: {}'.format(toc_item['type']))

    def __normal_slide(self, toc_item):
        """
        Add a normal slide

        :param toc_item: the toc item
        """
        contents_slide_layout = self.prs.slide_layouts[1]
        title_only_slide_layout = self.prs.slide_layouts[5]
        
        if 'figure' in toc_item:
            slide = self.prs.slides.add_slide(contents_slide_layout)
            title = slide.shapes.title
            title.text = toc_item['title']

            image_path = toc_item['figure']

            # remove the text box
            for shape in slide.shapes:
                if shape.has_text_frame and shape != title:
                    shape.text_frame.clear()

            # insert the image to the slide
            left = 0.05
            top = 0.2
            right = left
            
            width_ = 1 - (left + right)
            
            left_ = self.prs.slide_width * left
            top_ = self.prs.slide_height * top
            width_ = self.prs.slide_width * width_
            
            pic = slide.shapes.add_picture(image_path, left_, top_, width=width_)

            if 'note' in toc_item:
                # create a textbox in the slide
                left = 0.05
                top = 0.15
                width = 0.9
                height = 0.05

                left_ = self.prs.slide_width * left
                top_ = self.prs.slide_height * top
                width_ = self.prs.slide_width * width
                height_ = self.prs.slide_height * height

                txBox = slide.shapes.add_textbox(left_, top_, width_, height_)
                tf = txBox.text_frame
                tf.text = toc_item['note']
        else:
            slide = self.prs.slides.add_slide(contents_slide_layout)
            title = slide.shapes.title
            title.text = toc_item['title']

    def save(self, filepath):
        """
        Save the presentation

        :param filepath: the file path
        """
        self.filepath = filepath
        self.prs.save(filepath)
    
    def open(self):
        """
        Open the presentation
        """
        if not hasattr(self, "filepath"):
            self.save('/tmp/temp.pptx')
        subprocess.call(['open', self.filepath])