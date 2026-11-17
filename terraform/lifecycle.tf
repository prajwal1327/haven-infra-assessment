# Sold listing photos move to S3 Intelligent-Tiering after 30 days.
# This storage class has no minimum storage duration, supporting the
# application-level seller deletion SLA without Glacier early-delete fees.

resource "aws_s3_bucket" "listing_media" {
  bucket = "haven-listing-media"
}

resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
  bucket = aws_s3_bucket.listing_media.id

  rule {
    id     = "tier-sold-listing-photos"
    status = "Enabled"

    filter {
      tag {
        key   = "listing_status"
        value = "sold"
      }
    }

    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}
