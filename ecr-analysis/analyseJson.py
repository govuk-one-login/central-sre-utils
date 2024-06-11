# A Python script to format the ECR JSON data in a text file

import json
from collections import defaultdict
import os

def process_ecr_data(json_data):
    # Dictionaries to store the results
    ecr_image_counts = defaultdict(int)
    image_versions = defaultdict(lambda: defaultdict(int))
    image_dates = defaultdict(lambda: defaultdict(list))

    for account_data in json_data:
        for account, details in account_data.items():
            image_details = details.get("imageDetails", [])
            ecr_image_counts[account] += len(image_details)

            for image in image_details:
                repo_name = image["repositoryName"]
                image_digest = image["imageDigest"]
                image_pushed_at = image["imagePushedAt"]
                last_recorded_pull_time = image.get("lastRecordedPullTime")

                image_versions[account][repo_name] += 1
                image_dates[account][repo_name].append({
                    "imageDigest": image_digest,
                    "imagePushedAt": image_pushed_at,
                    "lastRecordedPullTime": last_recorded_pull_time
                })

    return ecr_image_counts, image_versions, image_dates

def append_results_to_file(output_filename, ecr_image_counts, image_versions, image_dates):
    with open(output_filename, 'a') as outfile:
        for account, count in ecr_image_counts.items():
            outfile.write(f"Account: {account}\n")
            outfile.write(f"  Total ECR Images: {count}\n")

            if account in image_versions:
                for repo, repo_count in image_versions[account].items():
                    outfile.write(f"  Repository: {repo}\n")
                    outfile.write(f"    Image Versions: {repo_count}\n")

                    if repo in image_dates[account]:
                        for date_info in image_dates[account][repo]:
                            outfile.write(f"      Image Digest: {date_info['imageDigest']}\n")
                            outfile.write(f"      Image Pushed At: {date_info['imagePushedAt']}\n")
                            last_recorded_pull_time = date_info.get('lastRecordedPullTime')
                            if last_recorded_pull_time:
                                outfile.write(f"      Last Recorded Pull Time: {last_recorded_pull_time}\n")
            outfile.write("\n")

def main(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"File {input_filename} does not exist.")
        return
    
    # Read the JSON file
    with open(input_filename, 'r') as file:
        try:
            json_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
    
    # Process the JSON data
    ecr_image_counts, image_versions, image_dates = process_ecr_data(json_data)

    # Append the results to the output file
    append_results_to_file(output_filename, ecr_image_counts, image_versions, image_dates)

# The name of the file which you want to analyse
input_filename = 'describeImagesFinal.json'
# The name of the text file you want to write results to
output_filename = 'results.txt'

main(input_filename, output_filename)
