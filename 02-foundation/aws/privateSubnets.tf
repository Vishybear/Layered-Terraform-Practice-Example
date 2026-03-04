# Private Subnets (for application servers, databases)
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  depends_on = [ aws_vpc.main ]
  
  tags = {
    Name        = "${var.environment}-private-${var.availability_zones[count.index]}"
    Environment = var.environment
    Type        = "private"
  }
}