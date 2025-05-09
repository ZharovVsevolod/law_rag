from langchain.schema import SystemMessage, AIMessage
from typing import List

# ------------
#     Main
# ------------
SYSTEM_PROMPT: SystemMessage = SystemMessage(content = """
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

START_MESSAGE: AIMessage = AIMessage(content = """Приветствую! Я могу помочь с вопросами, касающихся цифрового права Российской Федерации. 
Что Вас интересует?"""
)

ERROR_MESSAGE: str = "Упс! Кажется, что-то пошло не так... Попробуйте перезагрузить страницу."


def add_retirver_answer_to_question(
    question: str,
    retriever_answer: List[str]
) -> str:
    answer = f"Вопрос пользователя: {question}\n\n"
    answer += "#####\n"
    answer += "Дополнительный контекст (Retriever)\n"
    answer += "-----------------------------------\n\n"
    answer += transform_answer_list(retriever_answer)
    answer += "\n#####"
    return answer


def transform_answer_list(retriever_answer: List[str]) -> str:
    answer = ""
    for i, node in enumerate(retriever_answer):
        answer += f"### Документ {i + 1}\n{node}\n\n"
    answer = answer[:-2] # Remove the last \n\n
    return answer


# ------------
#    HOLMES
# ------------
HOLMES_SYSTEM_GET_TRIPLETS: SystemMessage = SystemMessage(content = """
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
