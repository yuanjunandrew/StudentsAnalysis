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
    print_hi('Start students analysis')
    ### input file paths
    PATH_enrollment_2015to2021 = "data/CC_Enrollments_4_Dr_Borcea.xlsx"
    PATH_admission_2015to2021 = "data/CC_Admissions_4_Dr_Borcea.xlsx"
    PATH_application_2015to2021 = "data/CC_Applications_4_Dr_Borcea.xlsx"

    ### output file paths
    PATH_enrollment_output = "output/enrollment_JY.csv"
    PATH_enrollment_track_output = "output/enrollment_track_JY.csv"
    PATH_yield_output = "output/yield_JY.csv"
    PATH_convert_output = "output/convert_JY.csv"

    enroll = Enroll() ## initiate a class with the functions for the enrollment data analysis
    apply = Apply() ## initiate a class with the functions for the conversion (applied to admitted) analysis
    admit = Admit() ## initiate a class with the functions for the yeild (admitted to enrolled) analysis


    enroll_df_raw = enroll.import_data(PATH_enrollment_2015to2021, "Sheet1")
    enroll_df_cleaned = enroll.clean_data(enroll_df_raw)
    enroll_df = enroll.add_columns(enroll_df_cleaned)
    enroll_df.to_csv(PATH_enrollment_output)  ## output the total enrollment data with added columns

    enroll_track_df = enroll.track(enroll_df)
    enroll_track_df.to_csv(PATH_enrollment_track_output) ## output the term by term tracking data of enrollment

    apply_df_raw = apply.import_data(PATH_application_2015to2021, "Sheet1")
    apply_df = apply.clean_data(apply_df_raw)
    admit_df_raw = admit.import_data(PATH_admission_2015to2021, "Sheet1")
    admit_df = admit.clean_data(admit_df_raw)

    yield_df = admit.yields(admit_df, enroll_df)
    yield_df.to_csv(PATH_yield_output)  ## output the yield data

    convert_df = apply.converts(apply_df, yield_df)
    convert_df.to_csv(PATH_convert_output) ## output the convert data

