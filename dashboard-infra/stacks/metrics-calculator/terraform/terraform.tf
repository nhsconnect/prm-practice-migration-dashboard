provider "aws" {
  region  = var.region

  default_tags {
    tags = {
      CreatedBy   = var.repo_name
      Environment = var.environment
      Team        = var.team
    }
  }
}

