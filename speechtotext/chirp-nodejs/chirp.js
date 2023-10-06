// Import the Cloud Speech-to-Text library
const speech = require('@google-cloud/speech').v2;
const fs = require('fs');

// Instantiates a client
const client = new speech.SpeechClient({apiEndpoint: "us-central1-speech.googleapis.com"});

// Your local audio file to transcribe
const audioFilePath = "gs://<<bucket-name>>/audio-files/output.wav";
// Full recognizer resource name
const recognizerName = "projects/<<project-number>>/locations/us-central1/recognizers/<<recognizer>>";
// The output path of the transcription result.
const workspace = "gs://<<bucket-name>>/transcripts";

const recognitionConfig = {
  autoDecodingConfig: {},
  model: "chirp",
  features: {
  enableWordTimeOffsets: true,
  },
  languageCode: 'en-IN'
};

const audioFiles = [
  { uri: audioFilePath }
];
const outputPath = {
  gcsOutputConfig: {
    uri: workspace
  }
};

async function transcribeSpeech() {
  const transcriptionRequest = {
    recognizer: recognizerName,
    config: recognitionConfig,
    files: audioFiles,
    recognitionOutputConfig: outputPath,
  };

const [operation] = await client.batchRecognize(transcriptionRequest);
    const [response] = await operation.promise();
    console.log(response);
}

transcribeSpeech();
