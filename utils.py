import pandas as pd

class Enroll:

    def import_data(self, PATH, SheetName):
        '''
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        '''
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def sort_rows(self, df):
        '''
        :param df: data in pandas dataframe format.
        :return: dataframe with the rows sorted by the terms
        '''
        return df


    def format_column_names(self, df):
        '''
        :param df: data in pandas dataframe format.
        :return: dataframe with formatted column names.
        '''
        return df


    def decode_column_values(self, df):
        '''
        :param df: data in pandas dataframe format.
        :return: dataframe with column values decoded.
        '''
        return df

    def drop_columns(self, df):
        '''
        :param df: data in pandas dataframe format.
        :return: dataframe that exclude sensitive information (i.e. name and legal country)
        '''
        return df

    def clean_data(self, df):
        '''
        :param df: data from the excel or csv in pandas dataframe format.
        :return: dataframe after cleaning.
        '''
        df_sorted = sort_rows(df)
        df_columns_named = format_column_names(df_sorted)
        df_columns_decoded = decode_column_values(df_columns_named)
        df_cleaned = drop_columns(df_columns_decoded)
        return df_cleaned

    def merge_data(self, df1, df2):
        '''
        :param df1: the data in the earlier terms.
        :param df2: the data in the later terms.
        :return: merged pandas dataframe in the timely order.
        '''
        return df

    def add_columns(self, df):
        '''
        add columns that are important for analysis after data is cleaned
        - start_semester is the first appearance of a student in a degree (id + degreeType)
            - find the first appearance of an id + degreeType combination and save the semester
            - assign the semester to start semester column when the id + degreeType combination shows again
        - regstat(registration status) changes yearly, but we only interested in the first appearance of regstat
            - convert to freshmen, transfer, continue for undergrad
            - convert to freshmen for all graduate students (very few students are transfer, and they are not specifically labeled in data)
        - semester_end_status, this information does not exist, but we track the record of students by their ids
            - if an enrollment record satisfies the graduation credit requirement, save the row index as the value to the key = id + degreeType as the graduate tracker
            - some students might take another semester even if the credit is fulfilled. Hence, update the  row index value to the key
            - initiate a dictionary with keys = id + DegreeType for the students that appeared, value = row index as the dropout tracker.
            - update the row index if the student show up again in the enrollment record
            - if id + degreeType existed in the graduation tracker, remove the entry in the dropout tracker.
            - generate graduate column using the row indexes that are tracked.
            - generate dropout column using the row indexes that are tracked.
                - generate the dropout_by_degree using the row indexes that are tracked, however, some students may change from BA to BS or vise visa.
                - so we initiate a new dictionary to track the undergrad students in dropout column
                - if we find a student is undergrad (BS or BA), track if the student id also exists as graduate, if so, remove the dropout entry
            - merge graduate, dropout columns, and fill the blanks with "continue" for undergrad and masters
        :param df: the data that is used for
        :return:
        '''
        return df

    def track(self, enroll_df):
        pass

class Apply:
    def import_data(self, PATH, SheetName):
        '''
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        '''
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def yields(self, apply_df, admit_df):
        pass

class Admit:
    def import_data(self, PATH, SheetName):
        '''
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        '''
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def converts(self, admit_df, enroll_df):
        '''
        :return:
        '''