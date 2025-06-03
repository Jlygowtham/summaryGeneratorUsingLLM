from db_connection import postgresDb
import fitz
from io import BytesIO
from docx import Document
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.chat_models import ChatOllama
from markdown_it import MarkdownIt
# from weasyprint import HTML
import pypandoc

def newUserService(userData: dict):
    try:
        name=userData.name
        email=userData.email
        password= userData.password

        pg= postgresDb()
        
        query="select email from userbio where email=%s"
        existUser= pg.showData(query,(email,))

        print(f"exist user status: {existUser}")

        if existUser.get('data'):
            return "user already exist"

        query="""
                Insert into UserBio(name,email,password)
                values(%s,%s,%s)
            """
        values=(name,email,password)

        insertNewUser = pg.insertData(query,values)
        
        print("New user status",insertNewUser['data'])
        return insertNewUser['data']
    
    except Exception as e:
        print(f"Error in newUserService function: {e}")
        return {"error":e,"status code":400}
    
    finally:
        pg.disconnect()

def loginService(userData:dict):
    try:
        email= userData.email
        password = userData.password

        pg= postgresDb()
        
        query="""
               Select * from userBio
               where email=%s and password=%s
         """
        values=(email,password)

        loginUser=pg.showData(query,values)
        
        pg.disconnect()

        print("login user status: ",loginUser)

        if not loginUser.get('data'):
            return "Invalid credentials"

        return loginUser

    except Exception as e:
        print(f"Error in loginService function: {e}")
        return {"error":e,"status code":400}
    


def summaryService(file,file_type,user_id):
    try:
        if file_type=='pdf':
            data = pdfService(user_id,file,file_type)
            print("pdf summary:",data)
            return data
        
        elif file_type=='docx':
            data = docService(user_id,file,file_type)
            print("Document summary: ",data)
            return data
        
        elif file_type=='csv':
            csv_read= pd.read_csv(BytesIO(file.read()))
            content = csv_read.to_string()
            response = llmService(user_id,content,'csv')
            print("csv summary",response)
            insertLLMSummary(user_id,content,response,file_type)
            return response
        
        elif file_type=='xlsx':
            data = pd.read_excel(BytesIO(file.read()))
            content = data.to_string()
            response = llmService(user_id,content,'csv')
            print("xlsx summary",response)
            insertLLMSummary(user_id,content,response,file_type)
            return response

        else:
            data= file.read().decode('utf-8')
            response = llmService(user_id,data,'txt')
            print("text summary",response)
            insertLLMSummary(user_id,data,response,file_type)
            return response
        
    except Exception as e:
        print("Exception:",e)
        return {"error",e}
    

def pdfService(user_id,file,file_type):
    try:
       print("Enter pdf service")
       content=file.read()
       pdf=fitz.open(stream=content,filetype='pdf')
       txt=''
       for page in pdf:
           txt+=page.get_text()
       print("pdf content: ",txt)

       response = llmService(user_id,txt,'pdf')
       insertLLMSummary(user_id,txt,response,file_type)
       return response

    except Exception as e:
        print("Exception",e)
        return {'error': e}
    

def docService(userid,file,file_type):
    try:
        print("Enter document service")
        docRead=Document(BytesIO(file.read()))
        content = ''.join([para.text for para in docRead.paragraphs])
        response = llmService(userid,content,'docx')
        insertLLMSummary(userid,content,response,file_type)
        return response
    except Exception as e:
        print("Exception: ",e)
        return {"error":e}


def llmService(userid,content,file_type):
    try:
        model = ChatOllama(model='llama3.2:latest',temperature=0.3)

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
Role:             
-You are a professional English teacher with over 10 years of experience and strong summarization skills.

Objective:
-Your job is to clearly and concisely summarize content based on its file type.

File Type: 
-{file_type if file_type else 'pdf or docx or csv or xlsx or txt file'}

Instructions:
- You must always produce a clear and meaningful summary based on the input — even if the content is informal, unstructured, or minimal.
- Do not generate SQL queries, programming code, shell commands, or advice.
- Do not include anything that wasn’t directly found or implied in the original content.
- Avoid hallucinating facts or adding hypothetical content.

Formatting:
- Use professional tone.
- For PDFs, Word, or TXT: Extract key insights using concise headings and bullet points.
- For CSV/XLSX: Provide a business-level narrative summary of trends or key data patterns.
- Focus on clarity and brevity.
- Give Markdown formatting output with headings (#, ##) and bullet points (-) as appropriate and Emphasize important points with bold text.

"""),
            ("user", "{content}")
        ])

        chain = prompt | model
        response = chain.invoke({"content": content})
        
        convertSummaryToDocx(str(userid),response.content)
        convertSummaryToPdf(str(userid),response.content)
        print("LLm response:",response)
        return response.content

    except Exception as e:
        print("Exception: ",e)
        return {"error":e}
    

def insertLLMSummary(userid,content,llmresponse,file_type):
    try:
        query="""Insert into summaryHistory(fileType,content,llmSummary,user_id)
                 values(%s,%s,%s,%s)"""
        values=(file_type,content,llmresponse,str(userid))
        pg=postgresDb()
        result=pg.insertData(query,values)
        print("Result: ",result)

    except Exception as e:
        print("Exception",e)


def convertSummaryToPdf(userId,response):
    try:
        output_file = f"{userId}_summary.pdf"
        pypandoc.convert_text(response, 'pdf', format='md', outputfile=output_file)
        print("✅ Summary converted to PDF successfully.")
    except Exception as e:
        print("Exception:",e)

def convertSummaryToDocx(userId,response):
    try:
        doc = Document()

        doc.add_paragraph(response)
        output_path = f"{userId}_summary.docx"
        doc.save(output_path)
        print("✅ Summary converted to .docx successfully.")

    except Exception as e:
        print("Exception: ",e)

# pdf, docx -> read, convert bytesIO
# txt, csv -> read, decode, convert StringIO    