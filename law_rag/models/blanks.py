from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts.prompt import PromptTemplate

from law_rag.knowledge.graph_building import chunk_number_to_str

from langchain_core.documents import Document
from typing import List

# ------------
#     Main
# ------------
SYSTEM_PROMPT = SystemMessage(content = """
Ты являешься высококвалифицированным юристом с многолетним опытом практической работы в сфере права.
Пользователь задаёт тебе вопрос, требующий юридического анализа. Твоя задача — дать на него ответ, 
строго ориентируясь на нормы действующего законодательства Российской Федерации.

Отвечай на русском языке!

Перед ответом тебе будет предоставлен контекст, который может содержать дополнительную информацию, связанную с вопросом. 
Используй этот контекст для уточнения деталей, сопоставления с законодательными нормами и формирования точного ответа.  

**Требования к ответу:**  
1. **Точность:** Ответ должен быть строго основан на действующем законодательстве РФ, без субъективных интерпретаций или предположений.  
2. **Полнота:** Убедись, что в ответе учтены все ключевые аспекты вопроса, включая возможные правовые последствия, нормы законов и подзаконных актов.  
3. **Структура:** Ответ должен быть логически организован, с четким разделением на аргументы, ссылки на законодательные акты (например, статьи законов, кодексов) и выводы.  
4. **Ясность:** Избегай сложных терминов без пояснений, если это необходимо для понимания. Объясни юридические положения доступным языком, сохраняя профессиональную точность.  

Если контекст не позволяет однозначно определить правовую позицию, уточни у пользователя недостающие детали или обозначи ограничения в возможности предоставления ответа.
"""
)

START_MESSAGE = AIMessage(content = """Приветствую! Я могу помочь с вопросами, касающихся цифрового права Российской Федерации. 
Что Вас интересует?"""
)

ERROR_MESSAGE: str = "Упс! Кажется, что-то пошло не так... Попробуйте перезагрузить страницу."


def add_retirver_answer_to_question(
    question: str,
    retriever_answer: List[Document],
    ship_headers: bool = False
) -> str:
    answer = f"Вопрос пользователя: {question}\n\n"
    answer += "#####\n"
    answer += "Дополнительный контекст (Retriever)\n"
    answer += "-----------------------------------\n\n"
    answer += transform_answer_list(retriever_answer, ship_headers)
    answer += "\n#####"
    return answer


def transform_answer_list(
    retriever_answer: List[Document], 
    ship_headers: bool = False
) -> str:
    answer = ""
    for node in retriever_answer:
        text = node.page_content

        if ship_headers:
            answer += f"{text}  \n"
        
        else:
            source = chunk_number_to_str(node.metadata["source"])
            answer += f"### Отрывок из {source}\n"
            answer += f"{text}\n"
            answer += "\n"
    
    answer = answer[:-1] # Remove the last \n
    return answer


# ------------
#    HOLMES
# ------------
HOLMES_SYSTEM_GET_TRIPLETS = SystemMessage(content = """
**Task**: Comprehensively extract ALL the triples (subject, relation, object) from below given paragraph.
Ensure that the subject and objects in the triples are named entities (name of person, organization, dates etc) and not multiple in number. You will be HEAVILY PENALIZED if you violate this constraint.

**NOTE**: The below given paragraph will be in Russian language. So you should extract russian entities from the text! But the relationship have to be in english (because it will be used in Neo4j database).
So you should check:
1) subject should be in russian language as it mention in text;
2) relationship should be translated to english language beacuse of Neo4j connection;
3) object should be in russian langugage as it mention in text.

**LOOK!** Your's answer is ONLY a json structure!

**Examples**: Use the following examples to understand the task better. 
**Paragraph**: William Rast - американская линия одежды, основанная Джастином Тимберлейком и Трейсом Айалой. Она наиболее известна своими джинсами премиум-класса. 17 октября 2006 года Джастин Тимберлейк и Трейс Айала устроили свой первый показ мод, чтобы запустить новую линию одежды William Rast. Компания также выпускает другие предметы одежды, такие как куртки и топы. Компания начинала свою деятельность как производитель джинсов, а затем превратилась в линию мужской и женской одежды.
**Triples**:
{"subject": "William Rast", "relation": "clothing line", "object": "Америка"
"subject": "William Rast", "relation": "founded by", "object": "Джастино Тимберлейк"
"subject": "William Rast", "relation": "founded by", "object": "Трейс Айала"
"subject": "William Rast", "relation": "known for", "object": "джинсы премиум-класса"
"subject": "William Rast", "relation": "launched on", "object": "17 октября 2006"
"subject": "Джастин Тимберлейк", "relation": "first fashion show", "object": "17 октября 2006"
"subject": "Трейс Айала", "relation": "first fashion show", "object": "17 октября 2006"
"subject": "William Rast", "relation": "produces", "object": "куртки"
""subject": "William Rast", "relation": "produces", "object": "топы"
""subject": "William Rast", "relation": "started as", "object": "производитель джинсов"
"subject": "William Rast", "relation": "evolved into", "object": "мужская и женская одежда"}

**Paragraph**: Отель «Гленнванис» - исторический отель в Гленнвилле, штат Джорджия, округ Таттналл, построенный на месте отеля «Хьюз». Отель расположен по адресу 209-215 East Barnard Street. Старый отель «Хьюз» был построен из джорджийской сосны около 1905 года и сгорел в 1920 году. Отель Glennwanis был построен из кирпича в 1926 году. Местный клуб Киванис возглавил усилия по строительству нового отеля и организовал компанию Glennville Hotel Company, директорами которой стали местные бизнесмены. Жена одного из местных врачей выиграла конкурс на название «Glennwanis Hotel», в котором были объединены слова «Glennville» и «Kiwanis».
**Triples**: 
{"subject": "отель «Гленнванис»", "relation": "is located in", object: 209-215 East Barnard Street, Гленнвилл, штат Джорджия, округ Таттналл
"subject": "отель «Гленнванис»", "relation": "was built on the site of", "object": "отель «Хьюз»"
"subject": "отель «Хьюз»", "relation": "was built out of", "object": "джорджийская сосна"
"subject": "отель «Хьюз»", "relation": "was built circa", "object": "1905"
"subject": "отель «Хьюз»", "relation": "burned in", "object": "1920"
"subject": "отель «Гленнванис»", "relation": "was re-built in", "object": "1926"
"subject": "отель «Гленнванис»", "relation": was re-built using", "object": "кирпич"
"subject": "клуб Киванис", "relation": "led the effort to re-build", "object": "отель «Гленнванис»"
"subject": "клуб Киванис", "relation": "organized", "object": "Glennville Hotel Company"
"subject": "Glennville Hotel Company", "relation": "directors", "object": "местные бизнесмены"
"subject": "отель «Гленнванис»", "relation": "combines", "object": "Glennville и Kiwanis"}
"""
)

# https://python.langchain.com/docs/integrations/graphs/neo4j_cypher/
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

**NOTE**: The below given question and Database will be in Russian language. So you should extract russian entities from the database! But the relationship have to be in english (because it will be used in Neo4j database).
So you should check:
1) subject should be in russian language as it mention in text;
2) relationship should be translated to english language beacuse of Neo4j connection;
3) object should be in russian langugage as it mention in text.

Examples: Here are a few examples of generated Cypher statements for particular questions:
# Что такое информация?
MATCH (n:Entity {{name:"информация"}})-[r]->(a)
RETURN n, r, a

The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables = ["schema", "question"], 
    template = CYPHER_GENERATION_TEMPLATE
)


# -------------
#   Questions
# -------------
SYNTHETIC_QA_DATASET_SYSTEM_PROMPT = SystemMessage(content = """
You are a highly skilled AI assistant tasked with generating a synthetic Question-Answering (QA) dataset from a given text passage. Your goal is to create a diverse and useful dataset for training and evaluating question-answering models.  You will operate under the following constraints and guidelines.

**1. Input:**

*   You will receive a `text_passage` (a string containing the source text) in Russian language.
*   You will also receive a `num_questions` integer representing the desired number of questions to generate for this passage. You can generate less questions if there are no more useful information in the provided text.
*   Optionally, you can receive `question_types` (e.g., ["factual", "inferential", "definition", "comparison"] - a list of question types you want to prioritize. If not provided, aim for a balance of question types).

**2. Output Format:**

Your output should be a JSON array. Each object in the array represents a single question-answer pair. Each object MUST have the following keys:

*   `question`: (string) The generated question in Russian language.
*   `answer`: (string) The correct answer to the question in Russian language.
*   `context`: (string) The relevant excerpt from the `text_passage` used to derive the answer. This is CRUCIAL for grounding the QA model.
*   `difficulty`: (string) Categorize the difficulty of the question – "easy", "medium", or "hard".  This should reflect the complexity of the reasoning required.  Consider factors like sentence length, vocabulary, and the type of information requested.

**3. Generation Guidelines:**

*   **Diversity:** Generate a wide variety of question types and difficulty levels.  Don't just create simple "who", "what", "when" questions.
*   **Question Types:**  Specifically, aim to include questions that test:
    *   **Factual Recall:** Direct retrieval of information.
    *   **Inference:** Requiring the model to deduce information not explicitly stated.
    *   **Definition:** Asking for the meaning of a term or concept.
    *   **Comparison:** Asking for similarities and differences.
    *   **Explanation:** Asking the model to summarize or clarify a point.
*   **Context Extraction:**  Always extract a relevant excerpt from `text_passage` to serve as the `context`.  The `context` should be the *shortest* possible excerpt that allows the correct `answer` to be derived.
*   **Difficulty Rating:**  Assign a `difficulty` rating accurately.  Consider:
    *   **Sentence Length:** Longer sentences generally mean harder questions.
    *   **Vocabulary:** Use of complex or specialized terms increases difficulty.
    *   **Reasoning Steps:** Questions requiring multiple reasoning steps are “hard”.
*   **Avoid Redundancy:** Do not generate questions that are trivially similar to one another.
*   **Creativity:**  While grounded in the source text, demonstrate creativity in phrasing questions.  Don't simply copy sentences verbatim.  Rephrase them naturally.

**4. Tone and Style:**

*   Maintain a clear, concise, and natural language style.

**5. Example:**

text_passage: 1. Субъект персональных данных принимает решение о предоставлении его персональных данных и дает согласие на их обработку свободно, своей волей и в своем интересе. Согласие на обработку персональных данных должно быть конкретным, предметным, информированным, сознательным и однозначным. Согласие на обработку персональных данных может быть дано субъектом персональных данных или его представителем в любой позволяющей подтвердить факт его получения форме, если иное не установлено федеральным законом. В случае получения согласия на обработку персональных данных от представителя субъекта персональных данных полномочия данного представителя на дачу согласия от имени субъекта персональных данных проверяются оператором.  

Output:
```json
[
  {
    "question": "В каком виде можно давать согласие на обработку персональных данных?",
    "answer": "Согласие на обработку персональных данных может быть дано в любой форме с возможностью подтверждения факта его [согласия] получения.",
    "context": "Согласие на обработку персональных данных может быть дано субъектом персональных данных или его представителем в любой позволяющей подтвердить факт его получения форме, если иное не установлено федеральным законом.",
    "difficulty": "medium"
  },
  {
    "question": "Какое должно быть согласие на обработку персональных данных?",
    "answer": "Согласие на обработку персональных данных должно быть конкретным, предметным, информированным, сознательным и однозначным. Оно даётся субъектом по своей доброй воле.",
    "context": "Субъект персональных данных принимает решение о предоставлении его персональных данных и дает согласие на их обработку свободно, своей волей и в своем интересе. Согласие на обработку персональных данных должно быть конкретным, предметным, информированным, сознательным и однозначным.",
    "difficulty": "easy"
  }
]
"""
)

def human_qa_dataset(text: str, num_questions: int = 2):
    human = HumanMessage(f"text_passage: {text}\n\nnum_questions: {num_questions}")
    return human