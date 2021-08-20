from boto.s3.connection import S3Connection

AWS_STORAGE_BUCKET_NAME = 'suporteassist'
AWS_ACCESS_KEY_ID = 'AKIA46H6AGELQM3ROUM4'
AWS_SECRET_ACCESS_KEY = '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'

conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)

for key in bucket.list(prefix="clientes/cli-03654469000132/", delimiter="/"):
    print(key)
    #print(key.name+"\n")
