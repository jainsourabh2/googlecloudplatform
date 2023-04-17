//import { S3Client, ListObjectsCommand } from "@aws-sdk/client-s3"; // ES Modules import
const fs = require('fs');
const cfsign = require('aws-cloudfront-sign');
const { S3Client, ListObjectsCommand } = require("@aws-sdk/client-s3"); // CommonJS import
const bucket = "bucket"
const distribution = "https://distribution.cloudfront.net"
const expireTime = 1712812480000
const keypairId = 'keypairId'
const region = "us-east-1"
const accessKeyId = 'accessKeyId'
const secretAccessKey = 'secretAccessKey'
const outputfileName = 'output.tsv'
const outputfileNameHeader = 'TsvHttpData-1.0'

let signingParams = {
  keypairId: keypairId,
  privateKeyString: process.env.PRIVATE_KEY,
  // Optional - this can be used as an alternative to privateKeyString
  privateKeyPath: './private_key.pem',
  expireTime: expireTime
}

const client = new S3Client(
  { 
    region: region,
    credentials:{
      accessKeyId:accessKeyId,
      secretAccessKey:secretAccessKey
    } 
  });
const input = {
  Bucket: bucket
};

try {
  fs.writeFileSync(outputfileName, outputfileNameHeader + '\n');
  // file written successfully
} catch (err) {
  console.error(err);
}

const command = new ListObjectsCommand(input);
async function func(){
  const response = await client.send(command);
  //console.log(response.Contents)
  let objectList = response.Contents 
  for(let i=0;i<objectList.length;i++){
    if(objectList[i].Size > 0)
      {
        let baseURL = distribution + '/' + objectList[i].Key;
        // Generating a signed URL
        let signedUrl = cfsign.getSignedUrl(
          baseURL, 
          signingParams
        );
        let output = signedUrl + '\t' + objectList[i].Size + '\n'
        fs.appendFile(outputfileName, output, err => {
          if (err) {
            console.error(err);
          }
        });
        //console.log(signedUrl + '  ' + objectList[i].Size)
      }
  }

}

func()
