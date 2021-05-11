import pandas as pd
from utils import Enroll, Apply, Admit

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.


if __name__ == '__main__':
    print_hi('Start student analysis')
    ### input file paths
    PATH_enrollment_2015to2020 = "data/CC_Enrollments_4_Dr_Borcea_09302020.xlsx"
    PATH_enrollment_2020to2021 = "data/CC_Enrollment_4_Dr_Bocea_F2020_S2021_02222021.xlsx"
    PATH_admission_2015to2021 = "data/CC_Admissions_4_Dr_Borcea_09242020.xlsx"
    PATH_application_2015to2021 = "data/CC_Applications_4_Dr_Borcea_09302020.xlsx"

    ### output file paths
    PATH_enrollment_output = "output/enrollment_JY.csv"
    PATH_enrollment_track_output = "output/enrollment_track_JY.csv"
    PATH_yield_output = "output/enrollment_track_JY.csv"
    PATH_convert_output = "output/enrollment_track_JY.csv"

    enroll = Enroll() ## initiate a class with the functions for the enrollment data analysis
    apply = Apply() ## initiate a class with the functions for the yield (applied to admitted) analysis
    admit = Admit() ## initiate a class with the functions for the Conversion (admitted to enrolled) analysis

    enroll_df_15to20 = enroll.import_data(PATH_enrollment_2015to2020, "Sheet1" )
    enroll_df_20to21 = enroll.import_data(PATH_enrollment_2020to2021, "Sheet1")
    enroll_df_15to20_clean = enroll.clean_data(enroll_df_15to20)
    enroll_df_20to21_clean = enroll.clean_data(enroll_df_20to21)
    enroll_df_merge = enroll.merge_data(enroll_df_15to20_clean, enroll_df_20to21_clean)
    enroll_df = enroll.add_columns(enroll_df_merge)
    enroll_df.to_csv(PATH_enrollment_output)  ## output the total enrollment data with added columns

    enroll_track_df = enroll.track(enroll_df)
    enroll_track_df.to_csv(PATH_enrollment_track_output) ## output the term by term tracking data of enrollment

    apply_df = apply.import_data(PATH_application_2015to2021, "Sheet1")
    admit_df = admit.import_data(PATH_admission_2015to2021, "Sheet1")

    yield_df = apply.yields(apply_df, admit_df)
    yield_df.to_csv(PATH_yield_output) ## output the yield data

    convert_df = admit.converts(admit_df, enroll_df)
    convert_df.to_csv(PATH_convert_output) ## output the convert data
