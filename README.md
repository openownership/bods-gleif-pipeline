# BODS-GLEIF Pipeline

Pipeline for producing beneficial ownership statements (BODS) data from data in the [Global Legal Entity Identifier Foundation (GLEIF)](https://www.gleif.org/) database.

## Data

The pipeline ultimately performs the following data transformations:

* Level 1 Data: LEI-CDF Format -> BODS Entity Statements
* Level 2 Data: Relationship Record (RR) CDF -> BODS Ownership or Control Statements
* Level 2 Data: Reporting Exceptions -> BODS Entity, Person and Ownership or Control Statements

## Architecture

The pipeline is built to run on Amazon Web Services (AWS), using AWS Kinesis data streams to connect
the stages together and an AWS EC2 instance to run the pipeline stages. AWS Firehose delivery 
streams can optionally be connected to Kinesis data streams to save intermediate or final data, for instance
to an S3 bucket.

Storage between pipeline runs is achieved using Elasticsearch, which runs in the same EC2 instance
as the pipeline code. 

The bulk of the pipeline code is contained within the [openownership/bodspipelines](https://github.com/openownership/bodspipelines) 
repository, which is a shared library intended to house all BODS pipelines in future. This repository contains the scripts and Docker
container configuration neceassry to run the pipeline on an EC2 instance.

## Ingest Stage

The Ingest pipeline stage downloads the [GLEIF Concatenated Files](https://www.gleif.org/en/lei-data/gleif-concatenated-file/download-the-concatenated-file)
and parses XML data to JSON which written to a Kinesis data stream. The uncompressed GLEIF data takes
up over 8GB of storage.

## Transform Stage

The Transform pipeline stage reads data from the Kinesis stream which is output by the Ingest stage.
The stage transforms the JSON representation of GLEIF data into beneficial ownership data (BODS)
statements.

# Usage

## Requirements

The pipeline is designed to be run on Amazon Web Services (AWS) infrastruture and has the following requirements:

* t2.medium EC2 instance with at least 20GB of storage
* 2 Kinesis streams to connect pipeline stages
* Optionally Firehose delivery streams connecting data streams to S3 buckets

## Setup

Create an EC2 instance (see requirements above), setup Kinesis data streams for each 
pipeline stage to output to, and optionally create Kinesis delivery streams to connected
to output data to S3 buckets.	

### Configuration

Create a .env file with the environment variable below (also see .env.example file).
 
```
BODS_AWS_REGION=
BODS_AWS_ACCESS_KEY_ID=
BODS_AWS_SECRET_ACCESS_KEY=
ELASTICSEARCH_HOST=bods_ingester_gleif_es
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_PROTOCOL=http
LOCAL_DATA_DIRECTORY=gleif
```

### One-time Setup

Run on EC2 instance:

```
bin/build
bin/setup_indexes
```

### Ingest Pipeline Stage

Run on EC2 instance:

```
bin/ingest
```

or

```
bin/transform
```

### Testing

Note it is possible to run the pipeline on a local machine for testing purposes
but this will degrade performance, possibly very significantly depending on the
the bandwidth of the network connection between the machine and the data center
where the Kinesis streams are hosted.
