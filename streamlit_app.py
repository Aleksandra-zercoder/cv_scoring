import os

import openai
import streamlit as st

from parse_hh import get_candidate_info, get_job_description

client = openai.Client(
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу
Потом представь результат в виде оценки от 1 до 10.
""".strip()

# Функция для запроса к GPT
def request_gpt(system_prompt, user_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # используем правильное имя модели
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Ошибка при обращении к API: {e}")
        return None

# Основная функция для оценки кандидата
def evaluate_candidate(job_description_url, cv_url):
    # Получение описания вакансии и резюме
    if job_description_url.startswith("http"):
        job_description = get_job_description(job_description_url)
    else:
        job_description = job_description_url  # Если введен текст, используем его напрямую

    if cv_url.startswith("http"):
        cv_info = get_candidate_info(cv_url)
    else:
        cv_info = cv_url  # Если введен текст, используем его напрямую

    if job_description and cv_info:
        # Отправка данных в GPT для получения результата
        combined_input = f"Оценка кандидата по вакансии:\n\n{job_description}\n\nРезюме кандидата:\n\n{cv_info}"
        evaluation = request_gpt(SYSTEM_PROMPT, combined_input)
        return evaluation
    else:
        return "Ошибка при получении данных."

# Интерфейс Streamlit
st.title("Оценка кандидата")

job_description_url = st.text_input("Введите ссылку на описание вакансии")
cv_url = st.text_input("Введите ссылку на резюме кандидата или текст резюме")

if st.button("Оценить"):
    evaluation_result = evaluate_candidate(job_description_url, cv_url)
    st.write("Результат оценки:", evaluation_result)
