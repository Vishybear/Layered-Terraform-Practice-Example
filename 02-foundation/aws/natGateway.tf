# NAT Gateways (allow private subnets to access internet)
resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  depends_on = [ aws_subnet.private ]
  tags = {
    Name        = "${var.environment}-nat-${count.index + 1}"
    Environment = var.environment
  }
}