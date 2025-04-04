import streamlit as st

def read_multiple_css(css_files):
    combined_css = ""
    for file_path in css_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                combined_css += f.read() + "\n"  # Append each CSS file's content
        except Exception as e:
            combined_css += f"/* Error loading {file_path}: {e} */\n"
    return combined_css

# Define the list of CSS files (Update with your actual file names)
css_files = ("bootstrap.min.css","engage.css", "njvote.css", "site-base.css", "sonj-components.css" )
css_styles = read_multiple_css(css_files)


# Extracted HTML content (from the NJ election website)
html_content = """<h3><a href="/state/">Department of State</a></h3> <h5><a href="/state/sos-about.shtml">Office of the Secretary</a></h5>"""



"""
<div class="col-12 col-sm-12 col-md-3 col-lg-3 col-xl-3 news-box sos-box ">
    <h4 class="text-center">📅 Important Dates For NJ Voters</h4>
    <div class="wrapper">
        <p><strong>March 24 - by 4:00 p.m.</strong><br>
        Candidate Petition Filing Deadline for Primary Election<br/>
        (before 4:00 p.m. 71 days before the original election date of June 3, 2025 pursuant to P.L. 2024,c.107)</p>

        <p><strong>March 27 - by 4:00 p.m.</strong><br>
        Deadline for Amendments to Defective Petitions for Primary Election Candidates</p>

        <p><strong>March 28 - by 4:00 p.m.</strong><br>
        Filing Deadline for Objections to Nominating Petitions for Primary Election Candidates</p>

        <p><strong>April 2</strong><br>
        Deadline for Determination of Petition Challenges for Primary Election Candidates</p>

        <p><strong>April 16</strong><br>
        Deadline for Change of Party Affiliation Declaration Forms for Primary Election</p>

        <p><strong>April 19</strong><br>
        Commencement of Mailing of Mail-In Ballots for Primary Election<br/>
        (45 days before the original June 3, 2025 election date pursuant to P.L. 2024,c.107)</p>
    </div>
</div>
"""

# Combine CSS with HTML
full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Important NJ Election Dates</title>
    <style>
        {css_styles}  /* Embed the Local CSS */
    </style>
</head>
<body>
    {html_content}  <!-- Insert the extracted HTML content -->
</body>
</html>
"""

# Streamlit UI
st.title("🗳️ NJ Election Dates Viewer")

# Display the extracted HTML visually in Streamlit
st.components.v1.html(full_html, height=600, scrolling=True)
