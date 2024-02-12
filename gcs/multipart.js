/**
 * TODO(developer): Uncomment the following lines before running the sample.
 */
// The ID of your GCS bucket
const bucketName = 'multipart-upload-bucket';

// The path of file to upload
const filePath = '/Users/path/Downloads/SP_Chauhan_Trailer_HD_Clean.mpg';

// The size of each chunk to be uploaded
const chunkSize = 32 * 1024 * 1024;

// Imports the Google Cloud client library
const {Storage, TransferManager} = require('@google-cloud/storage');

// Creates a client
const storage = new Storage({
    keyFilename: './sa-key.json',
  });

// Creates a transfer manager client
const transferManager = new TransferManager(storage.bucket(bucketName));

async function uploadFileInChunksWithTransferManager() {
  // Uploads the files
  await transferManager.uploadFileInChunks(filePath, {
    chunkSizeBytes: chunkSize,
  });

  console.log(`${filePath} uploaded to ${bucketName}.`);
  console.log(new Date())
}

console.log(new Date())
uploadFileInChunksWithTransferManager().catch(console.error);
