# bods-gleif-pipeline

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
repositoty, which is a shared library intended to . This repository contains the scripts and Docker
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

* t2.medium EC2 instance with at least 16GB of storage
* 2 Kinesis streams to connect pipeline stages
* Optionally Firehose delivery streams connecting data streams to S3 buckets

## Setup
