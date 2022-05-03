resource "aws_vpc" "metrics_calculator_vpc" {
  cidr_block = "10.0.0.0/26"

  tags = {
    Name = "VPC for the metrics calculator lambdas"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id               = aws_vpc.metrics_calculator_vpc.id
  cidr_block           = "10.0.0.0/28"
  availability_zone_id = data.aws_availability_zones.available.zone_ids[0]

  depends_on = [aws_internet_gateway.gw]

  tags = {
    Name = "Metrics calculator VPC public subnet"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id               = aws_vpc.metrics_calculator_vpc.id
  cidr_block           = "10.0.0.16/28"
  availability_zone_id = data.aws_availability_zones.available.zone_ids[0]

  tags = {
    Name = "Metrics calculator VPC private subnet"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.metrics_calculator_vpc.id
}

resource "aws_nat_gateway" "ngw" {
  allocation_id = aws_eip.ngw_public_ip.id
  subnet_id     = aws_subnet.public_subnet.id

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.gw]
}

resource "aws_eip" "ngw_public_ip" {
  vpc = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_route_table" "public_subnet_route_table" {
  vpc_id = aws_vpc.metrics_calculator_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table" "private_subnet_route_table" {
  vpc_id = aws_vpc.metrics_calculator_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.ngw.id
  }
}

resource "aws_route_table_association" "public_route_table" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_subnet_route_table.id
}

resource "aws_route_table_association" "private_route_table" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_subnet_route_table.id
}

data "aws_availability_zones" "available" {
  state = "available"

  filter { # Only fetch Availability Zones (no Local Zones)
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}