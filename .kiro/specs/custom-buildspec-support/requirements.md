# Requirements Document

## Introduction

This document defines the requirements for adding custom buildspec support to AFT (Account Factory for Terraform) customizations. Currently, AFT uses hardcoded buildspec files from the `modules/aft-customizations/buildspecs/` directory for all customization pipelines. This enhancement allows users to provide their own buildspec files in their account-customizations or global-customizations repositories, overriding the AFT defaults.

## Glossary

- **AFT**: Account Factory for Terraform - AWS solution for automating account provisioning
- **CodeBuild_Project**: AWS CodeBuild project resource that executes build commands
- **Buildspec**: YAML file defining build commands and phases for CodeBuild
- **Source_Artifact**: The source code artifact provided to CodeBuild from CodePipeline
- **Global_Customizations**: Terraform customizations applied to all vended accounts
- **Account_Customizations**: Terraform customizations applied to specific accounts based on customization name
- **CODEPIPELINE_Source**: CodeBuild source type that reads buildspec from the source artifact

## Requirements

### Requirement 1: Boolean Variable for Source Buildspec

**User Story:** As an AFT administrator, I want a boolean variable to enable source buildspec usage, so that I can choose between AFT default buildspecs and custom buildspecs from my repositories.

#### Acceptance Criteria

1. THE AFT_Module SHALL provide a variable named `aft_customizations_use_source_buildspec` of type boolean
2. THE Variable SHALL default to `false` for backward compatibility
3. THE Variable SHALL include a description explaining its purpose
4. THE Variable SHALL be defined in the root `variables.tf` and passed to the `aft-customizations` module

### Requirement 2: Global Customizations CodeBuild Configuration

**User Story:** As an AFT administrator, I want the global customizations CodeBuild project to use my custom buildspec when enabled, so that I can customize the build process for global customizations.

#### Acceptance Criteria

1. WHEN `aft_customizations_use_source_buildspec` is `false`, THE CodeBuild_Project `aft-global-customizations-terraform` SHALL use the buildspec content from `data.local_file.aft_global_customizations_terraform.content`
2. WHEN `aft_customizations_use_source_buildspec` is `true`, THE CodeBuild_Project `aft-global-customizations-terraform` SHALL use an empty buildspec string to read from source artifact
3. WHEN `aft_customizations_use_source_buildspec` is `true`, THE CodeBuild_Project SHALL expect a `buildspec.yml` file in the root of the global-customizations repository

### Requirement 3: Account Customizations CodeBuild Configuration

**User Story:** As an AFT administrator, I want the account customizations CodeBuild project to use my custom buildspec when enabled, so that I can customize the build process for account-specific customizations.

#### Acceptance Criteria

1. WHEN `aft_customizations_use_source_buildspec` is `false`, THE CodeBuild_Project `aft-account-customizations-terraform` SHALL use the buildspec content from `data.local_file.aft_account_customizations_terraform.content`
2. WHEN `aft_customizations_use_source_buildspec` is `true`, THE CodeBuild_Project `aft-account-customizations-terraform` SHALL use an empty buildspec string to read from source artifact
3. WHEN `aft_customizations_use_source_buildspec` is `true`, THE CodeBuild_Project SHALL expect a `buildspec.yml` file in the root of the account-customizations repository

### Requirement 4: Backward Compatibility

**User Story:** As an existing AFT user, I want my current deployment to continue working without changes, so that this enhancement does not break my existing setup.

#### Acceptance Criteria

1. WHEN the variable is not explicitly set, THE System SHALL default to using AFT-provided buildspecs
2. WHEN upgrading from a previous AFT version, THE System SHALL maintain existing behavior without requiring configuration changes
3. THE Default buildspec files SHALL remain available in `modules/aft-customizations/buildspecs/` for reference

### Requirement 5: Documentation and Examples

**User Story:** As an AFT administrator, I want documentation on how to use custom buildspecs, so that I can properly configure my customization repositories.

#### Acceptance Criteria

1. THE Customization_Repository templates SHALL include example buildspec.yml files that users can reference
2. THE Example buildspec files SHALL mirror the structure of the default AFT buildspecs
3. THE Variable description SHALL clearly explain the expected buildspec location when enabled
