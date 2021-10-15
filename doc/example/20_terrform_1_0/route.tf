resource "aws_route53_record" "v4" {
  zone_id = "my-zone-id-${var.stage}"
  name    = "test"
  type    = "A"
  ttl     = "300"
  records = ["8.8.8.8"]
}
