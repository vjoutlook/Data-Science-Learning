import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """
    Loads the messages and categories datasets from the specified filepaths
    Inputs:
        messages_filepath: Filepath to the messages dataset
        categories_filepath: Filepath to the categories dataset
    Output:
        df: Merged Pandas dataframe
    """
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    
    # load categories dataset
    categories  = pd.read_csv(categories_filepath)       
    
    # merge datasets
    df = messages.merge(categories, how = "inner", on =['id'])
    
    return df

def clean_data(df):
    """
    Cleans the merged dataset
    Input:
        df: Merged pandas dataframe
    Output:
        df: Cleaned dataframe
    """
    # create a dataframe of the 36 individual category columns    
    # select the first row of the categories dataframe
    #categories = df['categories'].str.split(pat =";",expand = True)
    categories = df['categories'].str.split(';',expand=True)
    #row = categories.iloc[0]
    row = categories[:1]
    category_colnames = row.apply(lambda x: x.str.split('-')[0][0], axis=0)
    categories.columns = category_colnames
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1:]
    
        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
    
    # drop the original categories column from `df`
    df.drop('categories', inplace = True, axis =1)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories], axis =1)
    # drop duplicates
    df = df.drop_duplicates()
    
    return df

def save_data(df, database_filename):
    """
    Saves clean dataset into an sqlite database
    Input:
        df:  Cleaned dataframe
        database_filename: Name of the database file
    """
    
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('disaster_response', engine, index=False)  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()