from utils import * 
from accessibilityStructuredPrompt import analyze_accessibility
from webDesignStructuredPrompt import analyze_webdesign
from ContentClarityStructuredPrompt import anaylze_content_clarity
import concurrent.futures
import time


url = "https://www.nj.gov/state/elections/vote.shtml"
# print(analyze_accessibility(url))


# # content clarity prmopt testing: 
nj_scrapped_data = chunk_html(url)

nj_content_guidlines = read_file_text("contentclarityguide.txt")

# suggestions = []

# # testing purposes
# i = 0

# for section in scrapped_data:
#     #print(f"section {i+1}: {section}")
#     i += 1

#     #print(f"here {i+1}")
#     sugesstions_list  = anaylze_content_clarity(section, content_guidlines)

#     for item in sugesstions_list:
#         suggestions.append(item)

# print(suggestions)

    #i += 1
        
def analyze_all_sections_parallel(scrapped_data, content_guidlines, max_workers=5):
    suggestions = []
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_section = {
            executor.submit(anaylze_content_clarity, section, content_guidlines): section
            for section in scrapped_data
        }

        for future in concurrent.futures.as_completed(future_to_section):
            try:
                result = future.result()
                suggestions.extend(result)

            except Exception as e:
                print(f"Error processing a section: {e}")
    end_time = time.time()
    print(f"completed tasks: {end_time - start_time:.2f} seconds")
    print(len(suggestions))
    return suggestions

print(analyze_all_sections_parallel(nj_scrapped_data, nj_content_guidlines))

# Using ThreadPoolExecutor to download pages concurrently
#start_time = time.time()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = []
#     for future in concurrent.futures.as_completed(futures):
#         print(future.result())

# end_time = time.time()
# print(f"completed tasks: {end_time - start_time:.2f} seconds")

