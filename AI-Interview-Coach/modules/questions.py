import random
from pathlib import Path
from typing import Dict, List

import pandas as pd


DEFAULT_QUESTIONS: Dict[str, List[Dict[str, str]]] = {
    "HR Interview": [
        {
            "question": "Tell me about yourself.",
            "ideal_answer": "Share a concise summary of your background, strengths, and recent achievements relevant to the role.",
        },
        {
            "question": "Why should we hire you?",
            "ideal_answer": "Connect your skills and impact to the company's needs with specific examples and results.",
        },
        {
            "question": "Describe a challenging project and how you handled it.",
            "ideal_answer": "Explain the challenge, your approach, collaboration, and measurable outcome.",
        },
    ],
    "Software Engineer": [
        {
            "question": "Explain a challenging software project you built.",
            "ideal_answer": "Describe architecture choices, trade-offs, implementation details, testing strategy, and impact.",
        },
        {
            "question": "How do you ensure code quality in a team?",
            "ideal_answer": "Mention code reviews, testing, CI/CD, linting, and clear coding standards.",
        },
        {
            "question": "How would you optimize a slow API endpoint?",
            "ideal_answer": "Discuss profiling, database/query optimization, caching, async processing, and monitoring.",
        },
    ],
    "Data Analyst": [
        {
            "question": "How do you approach analyzing a new dataset?",
            "ideal_answer": "Talk through business context, data cleaning, EDA, hypothesis testing, and communication of insights.",
        },
        {
            "question": "Describe a time your analysis changed a decision.",
            "ideal_answer": "Highlight your methodology, stakeholder communication, and business impact.",
        },
        {
            "question": "What metrics would you track for product growth?",
            "ideal_answer": "Cover activation, retention, conversion, engagement, and segmentation by cohort.",
        },
    ],
    "Custom Role": [
        {
            "question": "Tell me about your relevant experience for this role.",
            "ideal_answer": "Align your skills, accomplishments, and problem-solving experience with the role requirements.",
        }
    ],
}


def _questions_csv_path() -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir / "data" / "questions.csv"


def _normalize_role(role_name: str) -> str:
    role_name = (role_name or "").strip()
    if role_name in DEFAULT_QUESTIONS:
        return role_name
    return "Custom Role"


def load_question_bank() -> pd.DataFrame:
    csv_path = _questions_csv_path()
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            required = {"role", "question", "ideal_answer"}
            if required.issubset(df.columns):
                return df
        except Exception:
            pass

    rows = []
    for role, items in DEFAULT_QUESTIONS.items():
        for item in items:
            rows.append({"role": role, "question": item["question"], "ideal_answer": item["ideal_answer"]})
    return pd.DataFrame(rows)


def get_roles() -> List[str]:
    base_roles = ["HR Interview", "Software Engineer", "Data Analyst", "Custom Role"]
    return base_roles


def get_random_question(role_name: str) -> str:
    df = load_question_bank()
    role_key = _normalize_role(role_name)
    role_df = df[df["role"].fillna("").eq(role_key)]
    if role_df.empty:
        role_df = df
    return random.choice(role_df["question"].tolist())


def get_ideal_answer(question: str) -> str:
    df = load_question_bank()
    match = df[df["question"].fillna("").str.strip().eq((question or "").strip())]
    if match.empty:
        return "Provide a structured answer with relevant examples, clear outcomes, and confidence."
    return str(match.iloc[0]["ideal_answer"])


def generate_followup_question(user_answer: str, role_name: str, language: str = "English") -> str:
    answer = (user_answer or "").lower()
    if len(answer.strip()) < 20:
        return "Could you expand on your answer with a concrete example?"
    if "team" in answer or "collabor" in answer:
        return "How did you resolve disagreements within the team?"
    if "challenge" in answer or "problem" in answer:
        return "What would you do differently if you faced the same challenge again?"
    if role_name == "Software Engineer":
        return "How did you measure the performance or reliability impact of your solution?"
    if role_name == "Data Analyst":
        return "How did you validate that your analysis was statistically sound?"
    return "Can you share one measurable outcome from this experience?"
