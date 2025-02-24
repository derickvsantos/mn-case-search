import csv

def write_to_csv(data_list, filename="results.csv"):
    field_mapping = {
        "Case Number": "case_number",
        "Case Title": "case_title",
        "Case Type": "case_type",
        "Date Filed": "date_filed",
        "Case Location": "case_location",
        "Case Status": "case_status",

        "Petitioner Last Name": "applicant_last_name",
        "Petitioner First Name": "applicant_first_name",
        "Petitioner Middle Initial": "applicant_middle_initial",
        "Petitioner Street Address": "applicant_address",

        "Attorney Last Name": "attorney_last_name",
        "Attorney First Name": "attorney_first_name",
        "Attorney Middle Initial": "attorney_middle_initial",

        "Decedent Last Name": "decedent_last_name",
        "First Name": "decedent_first_name",
        "Middle Initial": "decedent_middle_initial",
        "Date of Birth": "dob",
        "Date of Death": "dod",

        "Respondent Last Name": "respondent_last_name",
        "Respondent First Name": "respondent_first_name",
        "Respondent Middle Inital": "respondent_initial_name",
        "Respondent Date of Birth": "respondent_dob",

        "Personal Representative Last Name": "pr_last_name",
        "Personal Representative First Name": "pr_first_name",
        "Personal Representative Middle Initial": "pr_middle_initial",
        "Personal Representative Street Address": "pr_address",
        
    }

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_mapping.keys(), delimiter=";")
        writer.writeheader()
        for item in data_list:
            if not item.get("applicant_last_name", ""):
                field_mapping["Petitioner Last Name"] = "petitioner_name"
                field_mapping["Petitioner First Name"] = "petitioner_name"
                field_mapping["Petitioner Middle Initial"] = "petitioner_name"
                field_mapping["Petitioner Street Address"] = "petitioner_address"
            formatted_row = {csv_key: item.get(dict_key, "NA") for csv_key, dict_key in field_mapping.items()}
            writer.writerow(formatted_row)