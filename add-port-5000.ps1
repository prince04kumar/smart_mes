# Quick script to add port 5000 to EC2 Security Group
# You need AWS CLI configured for this to work

# First, find your security group ID
Write-Host "Finding security groups..." -ForegroundColor Cyan
aws ec2 describe-instances --instance-ids i-017b5cd25f4cb60a2 --query "Reservations[0].Instances[0].SecurityGroups[0].GroupId" --output text

# Save the output and use it below
$SecurityGroupId = "sg-XXXXXXXXX"  # Replace with your security group ID

Write-Host "Adding port 5000 rule..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress `
    --group-id $SecurityGroupId `
    --protocol tcp `
    --port 5000 `
    --cidr 0.0.0.0/0 `
    --description "Flask Backend API"

Write-Host "Done! Port 5000 is now open." -ForegroundColor Green
