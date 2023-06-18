import os
import tempfile
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
from repo_reader import clone_git_repo, load_and_index_files
from questions import QuestionContext, ask_question
from utility import format_questions
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

url="url"
question = "question"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model_name = "gpt-3.5-turbo"
def main():
    st.title("Git repo Analyser")
    repo_url=st.text_input("Github URL",placeholder="Enter the Github Url of the Repo",key = url)
    #repo_url = input("Enter the Github Url of the Repo: ")
    repo_name = repo_url.split("/")[-1]
    print("Cloning the repo.........")
    with tempfile.TemporaryDirectory() as local_path:
        if(clone_git_repo(repo_url,local_path)):
            index, document, file_type_count, file_names = load_and_index_files(local_path)
            
            if(index == None):
                print("No document were found to index.")
                exit()

            print("Repo cloned.....Indexing Files")
            llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.2)

            template = '''
            Repo: {repo_name} ({repo_url}) | Conv: {conversation_history} | Docs: {numbered_documents} | Q: {question} | FileCount: {file_type_count} | FileNames: {file_names}

            Instr:
            1. Answer based on context/docs.
            2. Focus on repo/code.
            3. Consider:
                a. Purpose/features - describe.
                b. Functions/code - provide details/samples.
                c. Setup/usage - give instructions.
            4. Unsure? Say "I am not sure".

            Answer:
            '''

            prompt = PromptTemplate(
                template= template,
                input_variables=["repo_name","repo_url","conversation_history","numbered_documents","question","file_type_count","file_names"]
            )

            llm_chain = LLMChain(prompt=prompt, llm=llm)

            conversation_history = ""
            question_context = QuestionContext(index,document,llm_chain,model_name,repo_name,repo_url,conversation_history,file_type_count,file_names)
            while True:
                try:
                    user_question = st.text_input("Ask a question about the repository:",key=question)
                    btn = st.button("Submt")
                    #user_question = input("\nAsk a question about the repository (type 'exit() to quit'): ")
                    if user_question.lower() == "exit()":
                        break
                    
                    if btn:
                        print("processing....")
                        st.text("processing....")
                        user_question = format_questions(user_question)
                        answer = ask_question(user_question, question_context)
                        print(f"\nANSWER\n{answer}\n")
                        res = st.write(answer)
                        conversation_history += f"Question: {user_question}\nAnswer: {res}\n"

                except Exception as ex:
                    print(f"An error occured: {ex}")
                    break