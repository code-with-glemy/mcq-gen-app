import os
import json
import traceback
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

from src.mcq_generator.logger import logging
from src.mcq_generator.utils import read_file, get_table_data
from src.mcq_generator.MCQGenerator import MCQGen

import streamlit as st
from langchain.callbacks import get_openai_callback

mcq_gen= MCQGen()

with open('experiment/Response.json', 'r') as file:
    response_json = json.load(file)
    
# Streamlit app setup
st.title("MCQ Generator App")

#Create a form using st.form
with st.form(key='mcq_form'):
    #File upload
    uploaded_file = st.file_uploader("Upload a file (PDF, TXT, JSON)", type=['pdf', 'txt', 'json'])
    
    #Input fields for MCQ generation
    mcq_count= st.number_input("Number of MCQs to generate", min_value=1, max_value=20, value=5)
    #Subject
    subject = st.text_input("Subject for MCQs", value="History", max_chars=50)
    #Tone
    tone=st.text_input("Complexity level of the questions", value="easy", max_chars=50)
    
    button_generate = st.form_submit_button("Generate MCQs")
    
    if button_generate and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Generating MCQs..."):
            try:
                # Read the file content
                print(uploaded_file)
                file_content = read_file(uploaded_file)
                
                
                # Generate MCQs
                with get_openai_callback() as cb:
                    OpenAPIKey=os.getenv("OPENAI_API_KEY")
                    FullChain= mcq_gen.get_full_chain(OpenAPIKey)
                    result = FullChain({
                        "text": file_content,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(response_json)
                    })
                    
                st.success("MCQs generated successfully!")
                
            except Exception as e:
                logging.error(f"Error during MCQ generation: {e}")
                st.error(f"An error occurred: {e}")
                traceback.print_exc()
            else:
                print("Total tokens used:", cb.total_tokens)
                print("Prompt tokens used:", cb.prompt_tokens)
                print("Completion tokens used:", cb.completion_tokens)
                print("Total cost in USD:", cb.total_cost)
                
                if isinstance(result,dict):
                    quiz = result.get("quiz")
                    st.write("Review:", result.get("review"))
                    print("Quiz:", quiz)
                    if quiz is not None:
                        st.write("Generated MCQs:")
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index=df.index + 1
                            st.table(df)
                            st.text_area(label="Review", value=result["review"])
                        else:
                            st.error("No MCQs generated. Please check the input file and parameters.")
                else:
                    st.write(result)
