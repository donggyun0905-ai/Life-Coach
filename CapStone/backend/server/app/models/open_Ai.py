from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv
from models.open_ai_model import text_imbeding as ti
import os


def run_open_ai(ver=1):
    global cashed_docs
    load_dotenv(dotenv_path='smith.env')

    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("🔑 Google API Key:", google_api_key)
    ####ai 입출력 설정하는 코드
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
    You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.

    Answer in Korean.

    #Context:
    {context}
    """,
            ),
            ("human", "{question}"),
        ]
    )
    ###
    ### 사용할 open ai config
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        disable_streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    ###
    def format_docs(docs):
        return "\n\n".join(document.page_content for document in docs)

    chain = {
                "context": RunnableLambda(lambda _: ti.t_imbeding()) | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            } | prompt | llm | StrOutputParser()
    if (ver == 1):
        question = (
            "Summarize the title and main content of the following text both concisely and in detail. Make sure not to miss any important points and keep the summary clear and well-organized.")
        # 다음 글의 제목과 주요 내용을 핵심적으로 요약하고 자세하게도 요약해줘. 중요한 점은 놓치지 말고, 간결하게 정리해줘.
    elif (ver == 2):
        question = "Without an introductory sentence, refer to both summaries and create a final summary that is cleanly organized into distinct paragraphs, easy to read, and structured with clear headings. Eliminate redundancy and focus on delivering the core content in a well-formatted outline. At the end, include a brief and concise summary of the key message in Korean."
        # "맨 앞에서 서론 없이 두 요약본을 참고해서 중복 없이 깔끔하게 문단별, 읽기 쉽고 정리 잘된 목차에 내용있는 양식으로 핵심적으로 최종 요약해줘. 마지막에는 최종 핵심만 간결하게 적어줘 한글로"
    elif (ver == 3):
        question = "Summarize the content in Korean, starting directly with the main points—no introduction—keeping it concise, well-organized, and easy to read."
        # 핵심만 간결하고 정리해서 보기 쉽게 요약해줘
    response = chain.invoke(question)

    return response