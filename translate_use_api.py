from google.cloud import translate_v3 
from google.cloud import storage
import streamlit as st
import os
import json


def upload_to_gcs(file_name, file_data):
    storage_client = storage.Client()
    bucket = storage_client.bucket('testggapi')
    file_name = 'input/' + file_name
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_data, content_type="application/pdf")
    #st.success("File uploaded to GCS successfully.")

def translate_document(file_name, source_language = "en",
                       target_language = "en"):
    translate_client = translate_v3.TranslationServiceClient()
    PROJECT_ID, LOCATION = 'testggapi-451315', 'global'
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION}'
    
    input_uri = f'gs://testggapi/input/{file_name}'
    output_uri_prefix = f'gs://testggapi/output/'
    
    storage_client = storage.Client()
    bucket = storage_client.bucket('testggapi')
    
    ls = ["testggapi", "input", file_name.replace(".pdf", ""), target_language, "translations"]
    file_name = 'output/' + '_'.join(ls) + ".pdf"
    blob = bucket.blob(file_name)
    
    if blob.exists():
        blob.delete()
    
    document_input_config = {   
        "gcs_source": {
            "input_uri": input_uri
        },
        "mime_type": "application/pdf"
    }
    
    document_output_config = {
        "gcs_destination": {
            "output_uri_prefix": output_uri_prefix
        }
    }
    
    respone = translate_client.translate_document(
        request={
            "parent": parent,
            "document_input_config": document_input_config,
            "document_output_config": document_output_config,
            "source_language_code": source_language,
            "target_language_code": target_language
        }
    )
    #st.write("File translated successfully.")

def download_from_gcs(file_name, target_language):
    
    storage_client = storage.Client()
    bucket = storage_client.bucket('testggapi')
    
    ls = ["testggapi", "input", file_name.replace(".pdf", ""), target_language, "translations"]
    file_name = 'output/' + '_'.join(ls) + ".pdf"
    
    blob = bucket.blob(file_name)
    file_data = blob.download_as_bytes()
    #st.write("File downloaded from GCS successfully.")
    return file_data


def translated_pdf(file_name, file_data, source_language, target_language):
    
    if "GOOGLE_CLOUD_KEY_JSON" in st.secrets:
        key_json = st.secrets["GOOGLE_CLOUD_KEY_JSON"]
        
        try:
            # Chuyển `\\n` thành `\n` đúng định dạng JSON
            key_json_fixed = key_json.replace("\\n", "\n")

            # Kiểm tra xem có phải JSON hợp lệ không
            key_dict = json.loads(key_json_fixed)  # Nếu lỗi thì key bị sai
            
            # Ghi key ra file tạm
            with open("temp_key.json", "w") as f:
                json.dump(key_dict, f)  # Đảm bảo ghi đúng JSON

            # Thiết lập biến môi trường
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_key.json"
            print("✅ GOOGLE_APPLICATION_CREDENTIALS đã được thiết lập!")

        except json.JSONDecodeError as e:
            print("❌ Lỗi JSONDecodeError:", e)
            print("🔍 Nội dung key_json bị lỗi:", key_json)


    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text(f"⏳ Running... {0}%")
    upload_to_gcs(file_name, file_data)
    progress_bar.progress(25)
    status_text.text(f"⏳ Running... {25}%")
    translate_document(file_name, source_language, target_language)
    progress_bar.progress(70)
    status_text.text(f"⏳ Running... {70}%")
    file_data = download_from_gcs(file_name, target_language)
    progress_bar.progress(100)
    status_text.text(f"⏳ Running... {100}%")
    return file_data