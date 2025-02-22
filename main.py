from google.cloud import translate_v3 as translate
import os

# Cấu hình Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "testggapi.json"

def translate_document(input_uri, output_uri_prefix, target_language="en"):
    client = translate.TranslationServiceClient()

    # Thay YOUR_PROJECT_ID bằng Project ID của bạn
    parent = "projects/testggapi-451315/locations/global"

    # Cấu hình file đầu vào
    document_input_config = {
        "gcs_source": {"input_uri": input_uri},
        "mime_type": "application/pdf",  # Định dạng file đầu vào (PDF, DOCX, v.v.)
    }

    # Cấu hình file đầu ra (output_uri_prefix phải kết thúc bằng '/')
    document_output_config = {
        "gcs_destination": {"output_uri_prefix": output_uri_prefix},
    }

    # Gọi API dịch tài liệu
    response = client.translate_document(
        request={
            "parent": parent,
            "document_input_config": document_input_config,
            "document_output_config": document_output_config,
            "target_language_code": target_language,
        }
    )

    print(f"✅ Dịch thành công! File kết quả tại: {output_uri_prefix}")

# Chạy thử nghiệm
translate_document(
    "gs://testggapi/input/input2.pdf",   # File đầu vào
    "gs://testggapi/output/",                            # Folder đầu ra (kết thúc bằng '/')
    "en"                                                 # Ngôn ngữ đích (vi = tiếng Việt)
)
