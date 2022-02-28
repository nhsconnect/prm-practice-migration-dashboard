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

variable "telemetry_bucket_name" {
  type        = string
  description = "Name of bucket which telemetry data is retrieved from"
}

variable "metrics_bucket_name" {
  type        = string
  description = "Name of bucket which metrics data is written"
}

variable "metrics_calculator_function_name" {
  type    = string
  default = "metric_calculator"
}

variable "metrics_calculator_deployment_bucket_name" {
  type    = string
  description = "Name of bucket where the metrics calculator package is deployed"
}

variable "metrics_calculator_code_key" {
  type    = string
  description = "Object key for metrics calculator deployed code"
}

variable "metrics_calculator_handler_name" {
  type    = string
  description = "Handler function name for the metrics calculator"
}