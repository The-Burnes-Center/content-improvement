
# �� Machine Assistant for eXperience (MAX)

This is a website content improvement and analysis tool developed for the New Jersey Division of Elections and Office of Innovation. 

---

## �� What It Does

- �� **Feature 1**: Audience  
  Help developers and designers through the user-centered design process by providing feedback on the website from the perspectiver of a 
  given user persona. Includes the ability to help generate user personas with AI.

- �� **Feature 2**: Content Clarity  
  Ensure that the content on your website is clear and accessibile for users of all reading levels. 

- �� **Feature 3**: Web Design
  Improve the visual layout of your website for increased usability.

- �� **Feature 3**: Code Best Practices
  Ensure that your HTML code is aligned with Web Content Accessibility Guidelines (WCAG) for maximum accessibility and usability. 

---

## �� Architecture

![System Architecture](./architecture.png)

- Brief overview of the architecture or workflow.
- Use diagrams to explain data flow, tools, and modular pieces.
- Example:

```
[Upload] → [OCR/Text Preprocessing] → [LLM Agent Analysis] → [Summarization + Translation] → [Frontend Display]
```

---

## �� Tech Stack

| Layer          | Tools & Frameworks                                      |
|----------------|---------------------------------------------------------|
| **Frontend**   | React, Ant.design                                       |
| **Backend**    | Python, AWS Lambda                                      |
| **AI/ML**      | OpenAI GPT-4, Claude, AWS Bedrock                       |
| **Infra/DevOps**| AWS S3, Cognito, RDS, mySQL                            |

---

## �� Setup

```bash
# Clone the repo
git clone https://github.com/The-Burnes-Center/content-improvement.git
cd content-improvement

# Install dependencies
pip install -r requirements.txt

# Run backend locally
python -m flask --app flask_backend run

# Move to the frontend
cd njvote

# Intall dependencies
npm install

# Run frontend locally
npm run dev
```

.env format: 

MYSQL_DATABASE_USER=
MYSQL_DATABASE_PASSWORD=
MYSQL_DATABASE_DB=
MYSQL_DATABASE_HOST=
OPENAI_API_KEY=

Run an instance of mysql locally. 

<!-- ---

## �� Core Modules

| Module              | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `ocr_processor.py`  | Extracts text from PDFs using AWS Textract or Mistral                       |
| `redactor.py`       | Detects and removes PII using AWS Comprehend                                |
| `agent_runner.py`   | Manages LLM agents that handle summarization, translation, and chat         |
| `api.py`            | FastAPI-based REST endpoints for frontend consumption                       |
| `db_handler.py`     | Interfaces with DynamoDB for structured read/write                          | -->

---

## �� Roadmap

- [ ] Add authentication with Cognito

---

## �� Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## �� License

MIT License – see `LICENSE.md` for details.

---

## �� Authors & Acknowledgements

- Built by Druhi Bhargava and Max Norman 
- In partnership with The Burnes Center for Social Change at Northeastern University