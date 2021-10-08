terraform {
  required_providers {

    exoscale = {
      source  = "exoscale/exoscale"
      version = ">= 0.29.0"
    }
     
    hcloud = {
      source = "hetznercloud/hcloud"
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