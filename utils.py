import pandas as pd


class Enroll:
    di = {'F2015': 0,
          'Sp2016': 1,
          'Su2016': 2,
          'F2016': 3,
          'Sp2017': 4,
          'Su2017': 5,
          'F2017': 6,
          'Sp2018': 7,
          'Su2018': 8,
          'F2018': 9,
          'Sp2019': 10,
          'Su2019': 11,
          'F2019': 12,
          'Sp2020': 13,
          'Su2020': 14,
          'F2020': 15,
          'Sp2021': 16
          }

    def import_data(self, PATH, SheetName):
        """
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        """
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def sort_rows(self, df):
        """
        Normally the data is provided in the correct timely order. However, we want to make sure the order are
        correct, since the calculation of graduation and dropout are depending on the enrollment records appear in
        the right order.
        - create the "Semester_index" column to data and use it for sorting.
        :param df: data in pandas dataframe format.
        :return: dataframe with the rows sorted by the
        terms
        """
        df["Semester_index"] = df["Semester"]
        df = df.replace({"Semester_index": self.di})
        df = df.sort_values("Semester_index").reset_index(drop=True)
        return df

    def rename_columns(self, df):
        """
        rename columns
        :param df: data in pandas dataframe format.
        :return: dataframe with formatted column names.
        """
        df.rename(columns={'attstat': 'Attendance Status',
                           'matstat': 'Matriculation Status',
                           'EthnicMultirace': "Ethnicity",
                           "DegType": "Degree Type",
                           "NJITPROG": "Program",
                           "Term": "Semester",
                           "regstat": "Registration Status",
                           "PIDM": "id",
                           "DEPARTMENT": "Department",
                           "ClassDeliver": "Delivery Mode"
                           }, inplace=True)

        return df

    def map_column_values(self, df):
        """
        map the values from numerical to characters for regstat, matstat, attstat, gender, citizen
        :param df: data in pandas dataframe format.
        :return: dataframe with column values decoded.
        """
        ###
        df['regstat'] = df['regstat'].map({1: "freshmen", 2: 'transfer', 3: 'readmit', 4: 'continue'})
        df['matstat'] = df['matstat'].map({1: "degree-seeking", 2: "non-matric"})
        df['attstat'] = df['attstat'].map({1: "full-time", 2: "part-time"})
        df['Gender'] = df['Gender'].map({1: "male", 2: "female"})
        df["Gender"].fillna("Not Provided", inplace=True)
        df['Citizen'] = df['Citizen'].map({1: "domestic", 2: "international", 3: "domestic"})
        df['ClassDeliver'].fillna("Offline", inplace = True)
        return df

    def drop_columns(self, df):
        """
        :param df: data in pandas dataframe format.
        :return: dataframe that exclude sensitive information (i.e. name and legal country)
        """
        df.drop(["URM", 'MI', "SID", 'EMAIL', 'FIRST_NAME', 'Last_name', 'Legal_Country', 'Reten'], axis=1, inplace=True)
        return df

    def clean_data(self, df):
        """
        :param df: data from the excel or csv in pandas dataframe format.
        :return: dataframe after cleaning.
        """
        df_columns_mapped = self.map_column_values(df)
        df_columns_named = self.rename_columns(df_columns_mapped)
        df_sorted = self.sort_rows(df_columns_named)
        df_cleaned = self.drop_columns(df_sorted)
        return df_cleaned

    def merge_data(self, df1, df2):
        """
        :param df1: the data in the earlier terms.
        :param df2: the data in the later terms.
        :return: merged pandas dataframe in the timely order.
        """
        df = pd.concat([df1, df2], sort=True).reset_index(drop=True)
        return df

    def add_columns(self, df):
        """
        add columns that are important for analysis after data is cleaned
        - start_semester is the first appearance of a student in a degree (id + degreeType)
            - find the first appearance of an id + degreeType combination and save the semester
            - assign the semester to start semester column when the id + degreeType combination shows again
        - first_semester_registration_status. we only interested in the first appearance of registration status (which change yearly in practice)
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
        :param df: the data that is cleaned
        :return:
        """
        start_semester_status = []
        start_semester = []
        semester_registration_status = []
        exist_start_semester = {}
        exist_start_semester_index = {}
        exist_start_semester_status = {}
        exist_graduate_row_index = {}
        exist_last_row_index = {}

        ### create the start_semester, start_semester_status, 'Semester registration status' columns
        for row_index, row in df.iterrows():
            deg_id = str(row['Degree Type']) + str(row['id'])
            if deg_id not in exist_start_semester:
                exist_start_semester[deg_id] = row['Semester']
                exist_start_semester_index[deg_id] = row['Semester_index']
                if row['Registration Status'] in ["freshmen", "transfer"]:  ## first record of regstat only take freshmen, transfer
                    semester_registration_status.append(row['Registration Status'])
                    exist_start_semester_status[deg_id] = row['Registration Status']
                else:
                    semester_registration_status.append("continue")
                    exist_start_semester_status[deg_id] = "continue"
            else:
                semester_registration_status.append("continue")

            start_semester.append(exist_start_semester[deg_id])
            start_semester_status.append(exist_start_semester_status[deg_id])

            exist_last_row_index[deg_id] = row_index

            if row["Degree Type"] == "MS":
                if row["AccumCredits"] + row["CreditEnr"] >= 30:
                    exist_graduate_row_index[deg_id] = row_index
            if row["Degree Type"] in ["BS", "BA"]:
                if row["AccumCredits"] + row["CreditEnr"] >= 120:
                    exist_graduate_row_index[deg_id] = row_index

        ### create the graduation column
        graduate = [0] * len(df)
        indexes = list(exist_graduate_row_index.values())
        replacements = ["graduate"] * len(indexes)
        for (index, replacement) in zip(indexes, replacements):
            graduate[index] = replacement

        ### create the dropout column
        exist_dropout_row_index = exist_last_row_index.copy()
        for key in exist_last_row_index.keys():
            if key in exist_graduate_row_index:
                del exist_dropout_row_index[key]
        dropout = [0] * len(df)
        indexes = list(exist_dropout_row_index.values())
        replacements = ["dropout"] * len(indexes)
        for (index, replacement) in zip(indexes, replacements):
            dropout[index] = replacement

        ### attach the columns to df
        df["Start semester"] = start_semester
        df["Start semester status"] = start_semester_status
        df["graduate"] = graduate
        df["dropout"] = dropout
        df['Semester registration status'] = semester_registration_status
        df["Start semester index"] = start_semester
        df = df.replace({"Start semester index": self.di})

        ### correct the false positive dropput labels due to undergrad students change degree between BA and BS

        real_dropout_row_index = {}
        for row_index, row in df.iterrows():
            if row["Degree Type"] in ["BS", "BA"]:
                ug_id = str(row['id'])
                if row["dropout"] == "dropout":
                    real_dropout_row_index[ug_id] = row_index  ### saved the id: rows of undergrad students
                if row["graduate"] == "graduate":
                    if ug_id in real_dropout_row_index:
                        del real_dropout_row_index[ug_id]
        dropout_real = [0] * len(df)
        indexes = list(real_dropout_row_index.values())
        replacements = ["dropout"] * len(indexes)
        for (index, replacement) in zip(indexes, replacements):
            dropout_real[index] = replacement
        df.drop("dropout", axis=1) ### delete the old dropout column and attach the real dropout column
        df["dropout"] = dropout_real

        ### create semseter end status column by combining the data from graudate and dropout columns.
        semester_end_status = []
        for i in range(0, len(graduate)):
            if graduate[i] == "graduate":
                semester_end_status.append("graduate")
            elif dropout_real[i] == "dropout":
                semester_end_status.append("dropout")
            else:
                semester_end_status.append("continue")
        df["Semester end status"] = semester_end_status

        return df

    def track(self, df):
        """
        :param df: df_enroll dataframe
        :return:
        """
        dictdf = self.dfDict("Semester_index", df)
        df_track = pd.DataFrame()
        for i in range(0, len(dictdf)):
            df = dictdf[i]
            status = df[df["Semester registration status"] != "continue"].copy()
            month = self.semester_month(status["Semester"].unique()[0])
            status["Degree months"] = month
            df_track = df_track.append(status)
            for j in range(i + 1, len(dictdf)):
                status = self.updatestatus(status, dictdf[j])
                df_track = df_track.append(status)
        return df_track

    def semester_month(self, semester):
        season = semester[:-4]
        if season == "F":
            month = 4
        elif season == "Sp":
            month = 5
        else:
            month = 3
        return month

    def dfDict(self, col, df):
        '''
        input: the df_enroll dataframe
        set the key to id
        output: the dictionary of {0: df_2015, 1: df_2016 ....}
        '''
        # create unique list of names
        UniqueSemesters = df[col].unique()
        # create a data frame dictionary to store your data frames
        dfDict = {elem: pd.DataFrame for elem in UniqueSemesters}
        for key in dfDict.keys():
            dff = df[:][df[col] == key]
            dff.set_index("id", inplace=True)
            dfDict[key] = dff
        return dfDict

    def updatestatus(self, status, d2):
        d11 = status.copy()
        d22 = d2[["Semester end status"]]

        month = self.semester_month(d2["Semester"].unique()[0])

        d11d22 = d11.join(d22, how="left", rsuffix='_new')
        semester = [d2["Semester"].unique()[0]] * len(d11d22)
        semester_index = [d2["Semester_index"].unique()[0]] * len(d11d22)
        status = []
        degree_month = []
        for index, row in d11d22.iterrows():
            if row["Semester end status"] not in ["graduate", "dropout"]:
                degree_month.append(row["Degree months"] + month)
            else:
                degree_month.append(row["Degree months"])
        for index, row in d11d22.iterrows():
            if row["Semester end status_new"] in ["graduate", "dropout"]:
                status.append(row["Semester end status_new"])
            else:
                status.append(row["Semester end status"])

        d11d22.drop(["Semester end status", "Semester end status_new", "Semester", "Semester_index", "Degree months"], axis=1, inplace=True)
        d11d22["Semester end status"] = status
        d11d22["Semester"] = semester
        d11d22["Semester_index"] = semester_index
        d11d22["Degree months"] = degree_month
        return d11d22


class Admit:
    def import_data(self, PATH, SheetName):
        """
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        """
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def yields(self, admit_df, enroll_df):
        """
        :param admit_df: imported admission file in dataframe format
        :param enroll_df: the enroll_df is one of the output dataframe from the enrollment analysis
        :return: data in pandas dataframe format.
        """
        id_start_semester_status = {}
        for row_index, row in enroll_df.iterrows():
            student_id = str(row['id'])
            if student_id not in id_start_semester_status:
                id_start_semester_status[student_id] = row["Start semester status"]

        yields = []
        start_semester_status = []
        for index, row in admit_df.iterrows():
            student_id = str(row["PIDM"]) ### use the PIDM column in admmission data to match with ids from Enrollment data
            if student_id in id_start_semester_status:
                yields.append("yield")
                start_semester_status.append(id_start_semester_status[student_id])
            else:
                yields.append("not yield")
                start_semester_status.append("")
        yield_df = admit_df.copy()
        yield_df["Yield"] = yields
        yield_df["Start semester status"] = start_semester_status
        return yield_df

class Apply:
    def import_data(self, PATH, SheetName):
        """
        :param PATH: the file path to the excel file.
        :param SheetName: the name of the sheet we want to import the data from excel.
        :return: data in pandas dataframe format.
        """
        x = pd.ExcelFile(PATH)
        df = x.parse(SheetName)
        return df

    def converts(self, apply_df, yield_df):
        """
        :param apply_df: imported application file in dataframe format
        :param yield_df: the yield_df is the output dataframe from the admission analysis
        :return: data in pandas datafrme format.
        """
        id_start_semester_status = {}
        for row_index, row in yield_df.iterrows():
            student_id = str(row['PIDM']) ### use the PIDM column in yeild data
            if student_id not in id_start_semester_status:
                id_start_semester_status[student_id] = row["Start semester status"]

        converts = []
        start_semester_status = []
        for index, row in apply_df.iterrows():
            student_id = str(row["PIDM"]) ### use the PIDM column in application data to match with PIDM from yield data
            if student_id in id_start_semester_status:
                converts.append("converted")
                start_semester_status.append(id_start_semester_status[student_id])
            else:
                converts.append("not converted")
                start_semester_status.append("")
        converted_df = apply_df.copy()
        converted_df["Converted"] = converts
        converted_df["Start semester status"] = start_semester_status
        return converted_df

