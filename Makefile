init:
	cd infra/terraform && terraform init

plan:
	cd infra/terraform && terraform plan

apply:
	cd infra/terraform && terraform apply

destroy:
	cd infra/terraform && terraform destroy