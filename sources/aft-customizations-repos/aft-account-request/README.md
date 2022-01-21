# Introduction
This repo stores the Account Requests for Control Tower Account Factory for Terraform. This is where you place requests for accounts that you would like provisioned and managed by the AFT solution.

### Request a new Account

AFT follows a GitOps model for creating and updating AWS Control Tower managed accounts. Account Request Terraform file should be created to provide necessary inputs to trigger AFT pipeline workflow for account vending. You can reference example Account Request you should have pushed to your chosen git repository for storing AFT Account Requests (link to instructions in deployment).

When account provisioning or updating is complete, the AFT pipeline workflow continues and runs AFT Account Provisioning Framework and Customizations steps.

Git push action will trigger ct-aft-account-request AWS CodePipeline in AFT management account to process your account request.

- **module name** must be unique per AWS account request.

- **module source** is path to Account Request terraform module provided by AFT - this should always be ```source = "./modules/aft-account-request"```

- **control_tower_parameters** captures mandatory inputs listed below to create AWS Control Tower managed account.
    - AccountEmail
    - AccountName
    - ManagedOrganizationalUnit
    - SSOUserEmail
    - SSOUserFirstName
    - SSOUserLastName
  

   Refer to https://docs.aws.amazon.com/controltower/latest/userguide/account-factory.html for more information.

- **account_tags** captures user defined keys and values to tag AWS accounts by required business criteria. Refer to https://docs.aws.amazon.com/organizations/latest/userguide/orgs_tagging.html for more information on Account Tags.

- **change_management_parameters** captures inputs listed below. As a customer you may want to capture reason for account request and who initiated the request.
    - change_requested_by
    - change_reason

- **custom_fields** captures custom keys and values. As a customer you may want to collect additional metadata which can be logged with the Account Request and also leveraged to trigger additional processing when vending or updating an account. This metadata can be referenced during account customizations which can determine the proper guardrails which should be deployed. For example, an account that is subject to regulatory compliance could deploy an additional config rule.

- **account_customizations_name** (Optional) Name of a customer-provided Account Customization to be applied when the account is provisioned.

### Update Existing Account

You may update AFT provisioned accounts by updating previously submitted Account Requests. Git push action triggers the same Account Provisioning workflow to process account update request.

AFT supports updating of all non control_tower_parameters inputs and ManagedOrganizationalUnit of control_tower_parameters input. Remaining control_tower_parameters inputs cannot be changed.

### Submit Multiple Account Requests

Although AWS Control Tower Account Factory can process single request at any given time, AFT pipeline allows you to submit multiple Account Requests and queues all the requests to be processed by AWS Control Tower Account Factory in FIFO order.

You can create Account Request Terraform file per account or cascade multiple requests in a single Terraform file.
