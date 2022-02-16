## Prerequisites

### Create terraform state bucket

#### Create bucket
`aws s3api create-bucket --bucket prm-pracmig-terraform-state-dev --acl private --create-bucket-configuration '{ "LocationConstraint": "eu-west-2" }'`

#### Configure public access
`aws s3api put-public-access-block --bucket prm-pracmig-terraform-state-dev --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true`

#### Toggle on versioning
`aws s3api put-bucket-versioning --bucket prm-pracmig-terraform-state-dev --versioning-configuration Status=Enabled`

#### Create lock table
NOTE: terraform will throw a lock exception if this table doesn't exist before running
`aws dynamodb create-table --table-name prm-pracmig-terraform-table --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType="HASH" --billing-mode PAY_PER_REQUEST`

