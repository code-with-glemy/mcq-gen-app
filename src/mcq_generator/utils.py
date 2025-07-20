import json
import traceback

def read_file(File): 
    if File.name.endswith(".pdf"):
        import PyPDF2
        try:
            pdf_reader = PyPDF2.PdfReader(File)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {e}")
    elif File.name.endswith(".txt"):
        return File.read().decode("utf-8")
    elif File.endswith(".json"):
        with open(File, "r") as file:
            return file.read()
    else:
        raise ValueError("Unsupported file format. Only .pdf and .txt files are supported.")
    # Function to read a file

def get_table_data(quiz_str):
    try:
        # convert the quiz from a str to dict
        quiz_dict=json.loads(quiz_str)
        quiz_table_data=[]
        
        # iterate over the quiz dictionary and extract the required information
        for key,value in quiz_dict.items():
            mcq=value["question"]
            options=" || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                 
                 ]
            )
            
            correct=value["answer"]
            explanation=value['explanation']
            quiz_table_data.append({"Question": mcq,"Choices": options, "Correct": correct, "Explanation": explanation})
        
        return quiz_table_data
        
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
    
