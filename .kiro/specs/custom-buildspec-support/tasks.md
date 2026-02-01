# Implementation Plan: Custom Buildspec Support for AFT Customizations

## Overview

This implementation adds a boolean variable to control whether AFT customization CodeBuild projects use embedded buildspecs or read from source repositories. The changes span the root module, aft-customizations submodule, and example template files.

## Tasks

- [x] 1. Add variable to root module
  - [x] 1.1 Add `aft_customizations_use_source_buildspec` variable to `variables.tf`
    - Define as boolean type with default `false`
    - Include validation block
    - Add descriptive documentation
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Pass variable to aft-customizations module
  - [x] 2.1 Add variable definition to `modules/aft-customizations/variables.tf`
    - Define matching boolean variable
    - _Requirements: 1.4_
  
  - [x] 2.2 Update module call in `main.tf` to pass the variable
    - Add variable passthrough to aft_customizations module block
    - _Requirements: 1.4_

- [x] 3. Modify CodeBuild project configurations
  - [x] 3.1 Update `aft-global-customizations-terraform` source block in `modules/aft-customizations/codebuild.tf`
    - Add conditional expression for buildspec attribute
    - Use empty string when variable is true, file content when false
    - _Requirements: 2.1, 2.2_
  
  - [x] 3.2 Update `aft-account-customizations-terraform` source block in `modules/aft-customizations/codebuild.tf`
    - Add conditional expression for buildspec attribute
    - Use empty string when variable is true, file content when false
    - _Requirements: 3.1, 3.2_

- [x] 4. Checkpoint - Validate Terraform configuration
  - Run `terraform validate` to ensure configuration is syntactically correct
  - Run `terraform fmt -check` to verify formatting
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Add example buildspec files to customization templates
  - [x] 5.1 Create `buildspec.yml.example` in `sources/aft-customizations-repos/aft-global-customizations/`
    - Copy content from default buildspec
    - Add header comment explaining usage
    - _Requirements: 5.1, 5.2_
  
  - [x] 5.2 Create `buildspec.yml.example` in `sources/aft-customizations-repos/aft-account-customizations/`
    - Copy content from default buildspec
    - Add header comment explaining usage
    - _Requirements: 5.1, 5.2_

- [x] 6. Final checkpoint - Verify implementation
  - Run `terraform validate` on complete configuration
  - Verify variable defaults work correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- This is a Terraform/HCL implementation - no separate programming language selection needed
- The implementation uses Terraform's ternary conditional expression: `condition ? true_value : false_value`
- Property tests can be implemented using Terratest or manual terraform plan verification
- All changes maintain backward compatibility through the `false` default value
