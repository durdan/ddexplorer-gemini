import pandas as pd
import os

# Read data from the main CSV file
df = pd.read_csv("./assest/worldcities.csv")

# Group the data by 'country'
grouped_df = df.groupby('country')

# Create a folder to store country-wise CSV files if it doesn't exist
output_folder = "country_csv_files"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate over each group (country) and save its data into a separate CSV file
for country, data in grouped_df:
    # Generate the filename for the country
    filename = os.path.join(output_folder, f"{country}.csv")
    
    # Check if the file already exists
    if not os.path.exists(filename):
        # If the file doesn't exist, create it and write the data
        data.to_csv(filename, index=False)
    else:
        # If the file already exists, append the data to it
        existing_data = pd.read_csv(filename)
        updated_data = pd.concat([existing_data, data], ignore_index=True)
        updated_data.to_csv(filename, index=False)
