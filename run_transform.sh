pyspark --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    --conf spark.hadoop.fs.s3a.access.key=$(aws configure get aws_access_key_id) \
    --conf spark.hadoop.fs.s3a.secret.key=$(aws configure get aws_secret_access_key) \
    --conf spark.hadoop.fs.s3a.endpoint=s3.ap-south-1.amazonaws.com