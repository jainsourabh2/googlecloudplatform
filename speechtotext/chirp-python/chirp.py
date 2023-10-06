import os

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

# Instantiates a client
#client = SpeechClient()

# Instantiates a client
client = SpeechClient(
    client_options=ClientOptions(
        api_endpoint="us-central1-speech.googleapis.com",
    )
)

# The output path of the transcription result.
workspace = "gs://<<bucket-name>>/transcripts"

# The name of the audio file to transcribe:
gcs_uri = "gs://<<bucket-name>>/audio-files/output.wav"

# Recognizer resource name:
name = "projects/<<project-number>>/locations/us-central1/recognizers/<<recognizername>>"

config = cloud_speech.RecognitionConfig(
  auto_decoding_config={},
  model="chirp",
  features=cloud_speech.RecognitionFeatures(
  enable_word_time_offsets=True,
  ),
)

output_config = cloud_speech.RecognitionOutputConfig(
  gcs_output_config=cloud_speech.GcsOutputConfig(
    uri=workspace),
)

files = [cloud_speech.BatchRecognizeFileMetadata(
    uri=gcs_uri
)]

request = cloud_speech.BatchRecognizeRequest(
    recognizer=name, config=config, files=files, recognition_output_config=output_config
)
operation = client.batch_recognize(request=request)
print(operation.result())
