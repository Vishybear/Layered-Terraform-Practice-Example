# Internet Gateway (for public internet access)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  depends_on = [ aws_vpc.main ]
  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}