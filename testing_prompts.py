from utils import * 

from web_design_structured_prompt import analyze_webdesign
from content_clarity_structured_prompt import anaylze_content_clarity
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


persona = generate_user_persona
print(f"user persona: {persona}")
# output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {generate_user_persona}.""")

# print(f"auditing website: {output} ")

#persona = " Victor a student at Rutgers university looking to register for the first time . confused if he should vote in his home county or at his college county"

#change this to be a single suggestion, then add to a list and impliment threading? 

positives_output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit and provide postives for the website using the  {persona}. 
                             
                             Examples of  the postives include: 

                            1. Clear navigation menu with important voter information categories like "Voter Information Portal", "3 Ways To Vote", "Register to Vote!", etc.
                            2. Prominent display of important dates and deadlines for upcoming elections.
                            3. Easy access to key voter resources like voter registration, polling location lookup, and ballot tracking.
                            4. Multiple language options available, including Spanish translations for some content.
                            5. Information on accessibility options for voters with disabilities.
                            6. Links to social media accounts for additional updates and information.
                            7. Contact information for county election officials and a voter information hotline.
                             
                             """)

challenges_output = get_pred(get_pure_source(url), f"""Based off of the provided URL, please audit the website for the following user persona: {persona} and provide challenges.
                             Examples of challenges include:

                            1. The homepage is quite text-heavy and may be overwhelming for some users. Consider streamlining content or using more visual elements.
                            2. The font size is relatively small, which may be difficult for some older voters to read comfortably. Consider offering an easy way to increase text size.
                            3. While there are some visual elements, more infographics or icons could help break up text and make information more digestible.
                            4. The mobile responsiveness of the site could be improved for easier viewing on smartphones.
                            5. Consider adding a prominent search function to help users quickly find specific information.
                            6. A FAQ section addressing common questions for older voters might be helpful.
                            7. The site could benefit from more white space and a cleaner layout to improve readability.
                            8. Add more information specifically tailored for older voters, such as details on absentee voting or assistance at polling places.
                            9. Ensure all PDFs and downloadable forms are accessible and easy to fill out electronically.
                            10. Consider adding video tutorials for key processes like registering to vote or using voting machines.
                             """)

# print(f"auditing  postives website based on victor: {positives_output} ")
# print(f"auditing  challenges based on victor: {challenges_output} ")

print(f"auditing  postives website based on generated persona : {positives_output} ")
print(f"auditing  challenges based on generated persona: {challenges_output} ")








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

