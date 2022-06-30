## Prerequisites

### AWS authentication

Before running any operations against AWS ensure that you have [configured the command line interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

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

### Install Docker

The `tasks` script controls the actual execution of the terraform code. It is recommended that the `dojo-` version of the tasks are executed—this ensures that the expected version of terraform is used, and in an environment that will match how it runs in CI.

To run the `dojo-` version of the tasks, you must ensure you have a docker-compatible API installed locally, for example, using [Colima](https://github.com/abiosoft/colima).

## Running terraform

The `tasks` script can be used to execute the terraform code.

To apply a terraform stack, first execute a "plan":

```
./tasks dojo-plan <stack-name> <stack-environment>
```

- `stack-name`: the name of the stack to apply (matching one of the directories under the `stacks/`)
- `stack-environment`: the name of the environment to apply the changes to.

Review the expected changes that it outputs. Once satisfied with them, apply the changes:

```
./tasks dojo-apply <stack-name> <stack-environment>
```

- `stack-name`: the name of the stack to apply (matching one of the directories under the `stacks/`)
- `stack-environment`: the name of the environment to apply the changes to.

## Troubleshooting

### Problem

```shell
Error: Failed to validate installed provider

Validating provider hashicorp/aws v4.9.0 failed: selected package for
registry.terraform.io/hashicorp/aws is no longer present in the target
directory; this is a bug in Terraform
```

### Solution

delete the .terraform directory

