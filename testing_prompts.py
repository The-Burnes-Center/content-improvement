from utils import * 
from accessibilityStructuredPrompt import analyze_accessibility
from webDesignStructuredPrompt import analyze_webdesign
from ContentClarityStructuredPrompt import anaylze_content_clarity
import concurrent.futures
import time


url = "https://www.nj.gov/state/elections/vote.shtml"
#print(analyze_accessibility(url))


generate_user_persona = get_pred(url,
                    f"""Based on the url provided, please create one user persona of someone who would navigate the website. 
                        Include their age, gender, occupation, income level, education level, tech savviness, needs or end goals from the website, 
                        challenges they may have using the website.
                    

                        An example of a user persona and formatting is: 

                        Name: '  '
                        Age: ' '
                        Gender: '  '
                        Occupation:  ''
                        Income Level:  XX per year
                        Education Level: '   '
                        Tech Savviness: Beginner/ Moderate / Intermediate / Advance 

                        Example Goals and Needs: 

                        Goals and Needs: 
                        1. Register to vote in New Jersey
                        2. Check voter registration status
                        3. Find the polling place
                        4. Understand early voting options
                        5. Request and submit a mail-in ballot

                        Example Challenges Using the Website:

                        Challenges Using the Website: 
                        1. Navigating through multiple pages to find specific information
                        2. Understanding legal or technical terminology related to voting procedures
                        3. Locating and downloading necessary forms for voter registration or mail-in ballots
                        4. Identifying the most up-to-date information, especially if there are changes to voting procedures
                        5. Finding clear instructions on how to complete and submit various forms
                        6. Accessing mobile-friendly versions of the website while using her smartphone

                        Example Summary: 
                        X  wants to ensure they are properly registered and informed about the voting process in New Jersey. 
                        They are civic-minded and wants to participate in elections but may struggle with finding time to thoroughly research voting procedures. 
                        They would benefit from clear, concise information and easy-to-follow instructions on the website.

                                
                                 
                        """ )

# print(f"user persona: {generate_user_persona}")
# output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {generate_user_persona}.""")

# print(f"auditing website: {output} ")

persona = " Victor a student at Rutgers university looking to register for the first time . confused if he should vote in his home county or at his college county"

challenges_output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona}. """)

print(f"auditing website based on victor: {challenges_output} ")







# # content clarity prmopt testing: 
# nj_scrapped_data = chunk_html(url)

# nj_content_guidlines = read_file_text("contentclarityguide.txt")

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
        
# def analyze_all_sections_parallel(scrapped_data, content_guidlines, max_workers=5):
#     suggestions = []
#     start_time = time.time()
#     print(f"number of sections {len(scrapped_data)}")

#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         future_to_section = {
#             executor.submit(anaylze_content_clarity, section, content_guidlines): section
#             for section in scrapped_data
#         }

#         for future in concurrent.futures.as_completed(future_to_section):
#             try:
#                 result = future.result()
#                 suggestions.extend(result)

#             except Exception as e:
#                 print(f"Error processing a section: {e}")
#     end_time = time.time()
#     print(f"completed tasks: {end_time - start_time:.2f} seconds")
#     print(len(suggestions))
#     return suggestions

#print(analyze_all_sections_parallel(nj_scrapped_data, nj_content_guidlines))

# Using ThreadPoolExecutor to download pages concurrently
#start_time = time.time()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = []
#     for future in concurrent.futures.as_completed(futures):
#         print(future.result())

# end_time = time.time()
# print(f"completed tasks: {end_time - start_time:.2f} seconds")

