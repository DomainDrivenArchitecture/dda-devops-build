terraform {
  required_providers {
     
    hcloud = {
      source = "hetznercloud/hcloud" # this whole block is important
      version = ">= 1.23.0"
    }

    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }

    hetznerdns = {
      source = "timohirt/hetznerdns"
      version = ">= 1.1.0"
    }
  }
}