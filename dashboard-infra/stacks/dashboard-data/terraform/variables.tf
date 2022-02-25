variable "region" {
  type        = string
  description = "AWS region."
  default     = "eu-west-2"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Uniquely identities each deployment, i.e. dev, prod."
}

variable "team" {
  type        = string
  default     = "Practice Migration"
  description = "Team owning this resource"
}

variable "repo_name" {
  type        = string
  default     = "prm-practice-migration-dashboard"
  description = "Name of this repository"
}

variable "metrics_bucket_name" {
  type        = string
  description = "Name of bucket which metrics are written to"
}