import wget
import os

if not os.path.exists('data'):
    os.makedirs('data')

url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_trip_data_2019-10.csv.gz'
output_file = 'data/green_trip_data_2019-10.csv.gz'

print("Downloading data...")
wget.download(url,output_file)
print("\nDownload completed!")