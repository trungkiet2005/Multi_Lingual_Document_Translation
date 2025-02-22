import sys

from google.cloud import translate_v3, storage
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "testggapi.json"
PROJECT_ID = 'testggapi-451315'
LOCATION = "global"
BUCKET_NAME = "testggapi"

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print("Success to upload the file from local to GCS bucket.")

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print("Success to download the file from GCS bucket to local")

def translate_document( input_uri, output_uri_prefix, target_language="en"):
    translate_client = translate_v3.TranslationServiceClient()
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION}'
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

    ls = input_uri.split("/")
    ls.extend([target_language, "translations"])
    output_name = "_".join(ls[2:]).replace(".pdf", "") + ".pdf"

    storge_client = storage.Client()
    bucket = storge_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"output/{output_name}")

    if blob.exists():
        blob.delete()

    respone = translate_client.translate_document(
        request={
            "parent": parent,
            "document_input_config": document_input_config,
            "document_output_config": document_output_config,
            "target_language_code": target_language
        }
    )

    print("Success to translate the document! The result at:", document_output_config["gcs_destination"]["output_uri_prefix"])
    return f"output/{output_name}"

def find_name_in_path(input_uri):
    idx = input_uri.rfind("/")
    if(idx == -1):
        input_uri = input_uri.replace("\\", "/")
        idx = input_uri.rfind("/")
    return input_uri[idx+1:]


def translated_pdf(source_local, destination_local, target_language="en"):

    # upload file from local to google cloud storage
    destination_blob_name = 'input/' + find_name_in_path(source_local)
    upload_to_gcs(BUCKET_NAME, source_local, destination_blob_name)

    #Translate PDF
    input_uri = "gs://" + BUCKET_NAME + "/" + destination_blob_name
    output_uri_prefix = "gs://" + BUCKET_NAME + "/" + "output/"
    blob_name = translate_document(input_uri, output_uri_prefix, target_language)

    # download file from cloud to local
    download_from_gcs(BUCKET_NAME, blob_name, destination_local + "/Translated_" + find_name_in_path(source_local))

if __name__ == '__main__':

    # input_uri = "gs://testggapi/input/input2.pdf"
    # output_uri_prefix = "gs://testggapi/output/"
    # target_language = "vi"
    # translate_document(input_uri, output_uri_prefix, target_language)
    #
    # source_file_name = 'DATA/TEST/Transformers_v1.1.pdf'
    # destination_blob_name = 'input/' + find_name_in_path(source_file_name)
    # # upload_to_gcs(BUCKET_NAME, source_file_name, destination_blob_name)
    #
    # # source_blob_name = 'output/testggapi_input_Transformers_v1.1_vi_translations.pdf'
    # # destination_file_name = 'DATA/OUTPUT_TEST/Transformers_v1.1_vi_translations.pdf'
    # # download_from_gcs(BUCKET_NAME, source_blob_name, destination_file_name)


    source_local = sys.argv[1]
    destination_local = sys.argv[2]
    language = sys.argv[3]
    translated_pdf(source_local, destination_local, language)
    print("Success to translate the document! The result at:", destination_local)

