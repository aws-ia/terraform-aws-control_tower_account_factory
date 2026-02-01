# To Do 

1. Option for terraform plan and terraform apply stage of the account customization pipelines for account-customizations. Option to override it somehow so it auto approves? How could we achieve this? 
4. API driven account creation alongside the account request repo. This should be an option to enable.
   1. should work on API key initially which the user can manually vend once the api is created.
5. Accounts vended with AWS Organizations API and retire the use of service catalog entirely.
6. Use buildspec in local repo (account customizations / global customizations) instead of the default one in AFT.
7. Optional steps to create in each account customization pipeline. Can provide another repo which has a local buildspec. This can support things like security scanning. It could also support third party integrations etc.
8. Allow account customizations to support separate repos instead of folders in the account-customizations repo. It should also support ref or branch tags. This will allow better versioning of the account customizations. 
9. Operational dashboard
   1.  pipelines in failed state?
   2.  pipeline stale checks?
