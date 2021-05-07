# Configure the Hetzner Cloud Provider
terraform {
  required_providers {
     hcloud = {
      source = "hetznercloud/hcloud" # this whole block is important
      version = "1.23.0"
    }
  }
  required_version = ">= 0.13"
}

provider "hcloud" {
  token = var.hetzner_api_key
}
