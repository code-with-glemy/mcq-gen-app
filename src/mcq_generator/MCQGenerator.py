#Basic imports
import os
import pandas as pd
import json
import traceback
from dotenv import load_dotenv
load_dotenv()


#MCQ Gen imports
from src.mcq_generator.logger import logging
from src.mcq_generator.utils import read_file,get_table_data

#Langchain imports
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain, SimpleSequentialChain, TransformChain
from langchain.callbacks import get_openai_callback

class MCQGen:
    def __init__(self):
        pass

    def get_full_chain(self,OpenAPIKey):
        """    Function to get the full chain for MCQ generation.
        """
        
        llm=ChatOpenAI(openai_api_key=OpenAPIKey, model_name="gpt-3.5-turbo", temperature=0.5)
        prompt1=PromptTemplate(
            input_variables=["text", "number", "subject", "tone", "response_json"],
            template="""
                Text:{text}
                You are an expert MCQ maker. Given the above text , it is your job to \
                Create a quiz of {number} mulitple choice question for {subject} students in {tone} tone.
                Make sure the questions are not repeated and check all the questions to be conforming the text as well.
                Make sure to format your response like JSON below and use it as a guide. \
                Ensure to make {number} MCQs
                ### JSON
                {response_json}
                """
            )

        Chain1=LLMChain(
            llm=llm,
            prompt=prompt1,
            output_key="quiz",  
            verbose=True
        )


        template2="""
        You are an expert english grammarian and writer.Given a Multiple Choice Quiz for {subject} students.\
        You need to evaluate the complexity of the question and give a complete analysis of the quiz.Only use at max 50 words for complexity
        if the quiz is not at par with the cognitive and analytical abilities of the students, \
        update the quiz questions which needs to be changed and change the tone such that it prefectly fits the student ability.
        Also return the review of the uiz genrated by the AI.
        Quiz_MCQs:
        {quiz}

        Check from an expert English Writer for the above quiz:
        """


        prompt2=PromptTemplate(
            input_variables=["subject", "quiz"],
            template=template2
        )

        Chain2=LLMChain(
            llm=llm,    
            prompt=prompt2,
            output_key="review",
            verbose=True
        )

        FullChain=SequentialChain(
            chains=[Chain1, Chain2],
            input_variables=["text", "number", "subject", "tone", "response_json"],
            output_variables=["quiz", "review"], 
            verbose=True
        )
        return FullChain

    def run(self):
        """
        Class to handle the MCQ generation process.
        """
        OpenAPIKey=os.getenv("OPENAI_API_KEY")

        if not OpenAPIKey:
            logging.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        Text=read_file("./book.txt")
        Response_format=read_file("./experiment/Response.json")
        Response_json=json.loads(Response_format)

        with get_openai_callback() as cb:
            try:
                Chain=self.get_full_chain(OpenAPIKey)
                Response=Chain(
                {   "text": Text,
                    "number": 2,
                    "subject": "History",
                    "tone": "simple",
                    "response_json": json.dumps(Response_json)
                }
                )
                print(Response)
            except Exception as e:
                print("Error:", e)
                traceback.print_exc()

        quiz_output=json.loads(Response.get("quiz"))
        print("Review=",Response.get("review"))
        Out=[]
        for key,value in quiz_output.items():
            Out.append({
                "question": value.get("question"),
                "options": value.get("options"),
                "answer": value.get("answer")})
        df=pd.DataFrame(Out)
        df.to_csv("quiz_output.csv", index=False)