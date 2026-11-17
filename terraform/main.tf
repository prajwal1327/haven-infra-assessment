resource "aws_s3_bucket" "landlord_media" {
  for_each = toset(var.landlord_accounts)

  bucket = "haven-media-${each.key}"

  tags = {
    landlord_account_id = each.key
  }
}

# Preserve existing resources when migrating from count indexes to for_each keys.
moved {
  from = aws_s3_bucket.landlord_media[0]
  to   = aws_s3_bucket.landlord_media["la-001"]
}

moved {
  from = aws_s3_bucket.landlord_media[1]
  to   = aws_s3_bucket.landlord_media["la-002"]
}

moved {
  from = aws_s3_bucket.landlord_media[2]
  to   = aws_s3_bucket.landlord_media["la-003"]
}

moved {
  from = aws_s3_bucket.landlord_media[3]
  to   = aws_s3_bucket.landlord_media["la-004"]
}
