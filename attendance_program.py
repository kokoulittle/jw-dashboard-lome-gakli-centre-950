import numpy as np
import pandas as pd


# Generate all Wednesdays and Sundays between January 1st and December 31, 2026
date_range = pd.date_range(start="2026-02-01", end="2026-12-31", freq='D')
# 2 = Wednesday, 6 = Sunday
target_days = date_range[date_range.weekday.isin([2, 6])]

# Attendants and responsibilities
attendants = ["Jérémie WEMEGAN", "Emile ATALAMBOUDE", "Opportun OTTO",
              "Frédéric NAGBANGOU", "Essobiziou AMANA",
              "Amen DZAH", "Mario PELAGIE", "Laël DJESSOU",
              "Adiel DJESSOU", "Moïse TSOWOU", "Axel AMEVOR",
              "Roland LARE", "Amour KLOUSSE", "Joël AGBOGAN"]

responsibilities = ["Entrée", "Porte", "Intérieur", "Comptage"]


# Create the schedule
schedule = []

for date in target_days:
    # Randomly assign attendants to responsibilities
    shuffled_attendants = np.random.permutation(attendants).tolist()
    day_schedule = {
        "Date": date.strftime("%Y-%m-%d"),
        "Entrée": shuffled_attendants[0],
        "Porte": shuffled_attendants[1],
        "Intérieur": shuffled_attendants[2],
        "Comptage": shuffled_attendants[3]
    }
    schedule.append(day_schedule)

# Convert to DataFrame
df_random_schedule = pd.DataFrame(schedule)

print(df_random_schedule)

doc_path = "Random_Attendant_Crew_Schedule.csv"

df_random_schedule.to_csv(doc_path, index=False)
