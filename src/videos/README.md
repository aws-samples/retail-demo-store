# Retail Demo Store Videos Service

The Videos service streams product videos and synchronised metadata to [Amazon Interactive Video Service](https://aws.amazon.com/ivs/) and provides stream metadata (stream endpoints and products contained within the stream) via a Flask API. The [Web UI](../web-ui) makes calls to the service when a user views the 'Live' view. The endpoint provides a list of stream ingest endpoints, each with a list of their associated products, allowing the UI to present all products from the video before they appear in the stream.

When deployed to AWS, CodePipeline is used to build and deploy the Videos service as a Docker container to Amazon ECS behind an Application Load Balancer. The Videos service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Deploying Channels & Streaming Video

IVS channels are created and managed by the CloudFormation template. The default CloudFormation settings do not create any new IVS streams - instead the demo directs the UI to four externally hosted IVS streams.

To create and use IVS channels hosted in your own account, the option 'Use default IVS streams' should be set to 'No' when deploying CloudFormation. In this case, one IVS channel will be created for each '.mkv' video found in the `videos/` path of the staging S3 bucket. These videos should be uploaded by running the provided staging script - any videos in the local `videos/` directory will be uploaded.

**IMPORTANT:** Amazon IVS is currently only supported in the N. Virginia (us-east-1), Oregon (us-west-2), and Ireland (eu-west-1) regions. Therefore, to deploy the Retail Demo Store in a region that does not support IVS, be sure to select to use the Default IVS Streams CloudFormation template parameter.

## Custom Videos & Metadata
To enable full UI integration with custom videos, metadata must be embedded into the .mkv file.

Metadata must be created in the `.srt` format, with each timestamped entry containing data in the form:
`{"productId": <PRODUCT_ID>}`. The Videos service sends the metadata at the start of the timestamp. The latter section of the timestamp is not used. The file can either be edited manually or using an SRT editor (either software or online). An example metadata file can be seen [here](../../videos/sample.srt).

This metadata can then be combined with a video file to create an encoded `.mkv` file with embedded metadata by running the following command:
```
ffmpeg -i <INPUT_VIDEO_PATH> -i <INPUT_METADATA_PATH>.srt -vf scale=640x360 -c:v libx264  \
-pix_fmt yuv420p -profile:v main -tune fastdecode -x264opts “nal-hrd=cbr:no-scenecut” -minrate 3000 \
-maxrate 3000  -g 60 -c:a aac -b:a 160k -ac 2 -ar 44100 <OUTPUT_FILE_PATH>.mkv
```
An `.mkv` file created with this command is ready to be staged and should provide optimal UI integration.
The command also pre-encodes the video in a format designed to reduce the CPU & memory requirements of the Videos service.

## Local Development

The Videos service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build videos
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8007](http://localhost:8007).