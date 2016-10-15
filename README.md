An online archive of historical issues of the Daily Californian.

This repository contains tools to process raw microfilm images, generate PDFs and host them using Amazon S3. It also contains the Daily Cal's archival website, also hosted in a separate S3 bucket.

This project is under heavy development. While we continue to add more images, we're working on refining our image processing pipeline and web interface. Specifically, we want to

* Perform automatic image correction on the raw TIF files
* Perform OCR using PyTesseract
* Automatically tag pages using a list of Daily Cal and Berkeley keywords
* Create a full-text search for the entire archive
* Detect articles and advertisements
* Crowd-source corrections to our OCR text

If you're interested in contributing to this project -- perhaps if you're another student newspaper interested in digitizing your archives without spending the hundreds of thousands of dollars required for a private service -- please drop us a line at archives@dailycal.org.

# Get started

This project interacts with S3 to host the processed files *and* to host the "baked" website using django-bakery. You'll need to set the following environment variables:

* ``ARCHIVE_BUCKET_NAME``: The name of the Amazon S3 bucket where the processed files will go
* ``RAW_BUCKET_NAME``: The name of the bucket where raw scans will be pulled for processing
* ``AWS_BUCKET_NAME``: The name of the bucket where the *baked website* will go
* ``AWS_S3_REGION_NAME``: For example, `us-west-2`
* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESS_KEY``

# Process images

You can move images through the processing and archival pipeline with a series of management commands.

# Publish the website