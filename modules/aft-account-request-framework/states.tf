# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

######## aft_organizations_account_provisioning ########
# Creates and updates accounts for the Organizations vending method
# (CreateAccount / MoveAccount, then waits for auto-enrollment).
# Input is the account request SQS message; it branches on "operation".
# Both branches: create/lookup -> move -> poll the baseline and then the parent
# OU's controls on the account -> validate governance against the OU ->
# publish the CreateManagedAccount / UpdateManagedAccount lifecycle event.
# The CreateAccount branch also deletes the new account's default VPCs (when
# enabled in config) right after the move, before the baseline poll.
# The poll loop goes on to the validation when the baseline is complete and the
# OU's controls are on the account, or when the poll's control wait has
# expired: GOVERNANCE_RESERVE_SECONDS before TimeoutSeconds once a poll has seen the
# baseline complete (aft_common/organizations_provisioning.py). The poll reads
# TimeoutSeconds from $.poll_window.timeout_seconds.
# A failure of any step, a failed CreateAccount request, a failed baseline or
# a failed control goes to NotifyFailure, which sends the execution's one
# failure notification and fails it with the real error and cause. A timed-out
# execution is reported by the EventBridge rule in eventbridge.tf.
resource "aws_iam_role" "aft_organizations_account_provisioning_sfn" {
  count              = local.service_catalog_backend ? 0 : 1
  name               = "aft-organizations-account-provisioning-sfn"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/states.tpl", { none = "none" })
}

resource "aws_sfn_state_machine" "aft_organizations_account_provisioning" {
  count    = local.service_catalog_backend ? 0 : 1
  name     = var.aft_organizations_account_provisioning_sfn_name
  role_arn = aws_iam_role.aft_organizations_account_provisioning_sfn[0].arn
  definition = jsonencode({
    Comment        = "AFT account create/update for the Organizations vending method"
    StartAt        = "Operation"
    TimeoutSeconds = var.aft_organizations_provisioning_timeout_seconds
    States = {
      Operation = {
        Type = "Choice"
        Choices = [
          {
            Variable     = "$.operation"
            StringEquals = "ADD"
            Next         = "StartCreate"
          },
          {
            Variable     = "$.operation"
            StringEquals = "UPDATE"
            Next         = "UpdateAccount"
          }
        ]
        Default = "UnsupportedOperation"
      }
      StartCreate = {
        Comment    = "Record the execution start time; CreateAccount uses it to find a request this execution already submitted."
        Type       = "Pass"
        Parameters = { "execution_start_time.$" = "$$.Execution.StartTime" }
        ResultPath = "$.create_window"
        Next       = "CreateAccount"
      }
      CreateAccount = {
        Comment    = "Check the managed OU, then submit Organizations CreateAccount (async)."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["create_account"].arn
        ResultPath = "$.create"
        Retry = [
          {
            ErrorEquals = ["InvalidAccountRequestError"]
            MaxAttempts = 0
          },
          {
            ErrorEquals     = ["States.ALL"]
            IntervalSeconds = 5
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "PollCreateStatus"
      }
      PollCreateStatus = {
        Comment    = "Poll DescribeCreateAccountStatus until terminal."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["poll_create_status"].arn
        ResultPath = "$.create_status"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "CreateStatusChoice"
      }
      CreateStatusChoice = {
        Type = "Choice"
        Choices = [
          {
            Variable     = "$.create_status.State"
            StringEquals = "SUCCEEDED"
            Next         = "MoveAccount"
          },
          {
            Variable     = "$.create_status.State"
            StringEquals = "FAILED"
            Next         = "NotifyFailure"
          }
        ]
        Default = "WaitCreate"
      }
      WaitCreate = {
        Type    = "Wait"
        Seconds = 15
        Next    = "PollCreateStatus"
      }
      MoveAccount = {
        Comment    = "Move the new account from the org root into its managed OU."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["move_account"].arn
        ResultPath = "$.move"
        Retry = [
          {
            # An OU that can't be vended into fails the request as it is.
            ErrorEquals = ["InvalidAccountRequestError"]
            MaxAttempts = 0
          },
          {
            ErrorEquals     = ["States.ALL"]
            IntervalSeconds = 5
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "DeleteDefaultVpcs"
      }
      StartBaselinePoll = {
        Comment = "Record the execution start time and timeout; the baseline poll ends its control wait before the execution times out."
        Type    = "Pass"
        Parameters = {
          "execution_start_time.$" = "$$.Execution.StartTime"
          timeout_seconds          = var.aft_organizations_provisioning_timeout_seconds
        }
        ResultPath = "$.poll_window"
        Next       = "PollBaseline"
      }
      # No Parameters or InputPath: the Lambda reads the previous poll's result
      # ($.baseline) and $.poll_window from the full state input.
      PollBaseline = {
        Comment    = "Poll Control Tower baseline status, then the OU's controls on the account, until auto-enroll completes."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["baseline_status"].arn
        ResultPath = "$.baseline"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "BaselineChoice"
      }
      BaselineChoice = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.baseline.is_failed"
            BooleanEquals = true
            Next          = "NotifyFailure"
          },
          {
            Or = [
              {
                And = [
                  {
                    Variable      = "$.baseline.is_complete"
                    BooleanEquals = true
                  },
                  {
                    Variable      = "$.baseline.controls_settled"
                    BooleanEquals = true
                  }
                ]
              },
              {
                Variable      = "$.baseline.controls_wait_expired"
                BooleanEquals = true
              }
            ]
            Next = "ValidateGovernance"
          }
        ]
        Default = "WaitBaseline"
      }
      # The poll backs off from 30 s to 300 s between polls (POLL_WAIT_* in
      # aft_common/organizations_provisioning.py).
      WaitBaseline = {
        Type        = "Wait"
        SecondsPath = "$.baseline.next_wait_seconds"
        Next        = "PollBaseline"
      }
      ValidateGovernance = {
        Comment    = "Compare the account's baselines and controls with its OU's."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["validate_governance"].arn
        ResultPath = "$.governance"
        Retry = [{
          ErrorEquals = ["GovernanceValidationError"]
          MaxAttempts = 0
          }, {
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "CreateSucceeded"
      }
      DeleteDefaultVpcs = {
        Comment    = "Delete the new account's default VPCs in the governed Regions enabled for it; skipped unless enabled in config."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["delete_default_vpcs"].arn
        ResultPath = "$.default_vpcs"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        # If the step still fails after its retries, the account is provisioned
        # anyway: the error is kept in the state and reported once.
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.default_vpcs_error"
          Next        = "ReportDefaultVpcsError"
        }]
        Next = "DefaultVpcsPending"
      }
      # The Lambda returns "pending" on every path, because a Choice on a
      # missing path fails the execution outside every Catch.
      DefaultVpcsPending = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.default_vpcs.pending"
            BooleanEquals = true
            Next          = "WaitDefaultVpcs"
          }
        ]
        Default = "StartBaselinePoll"
      }
      WaitDefaultVpcs = {
        Type    = "Wait"
        Seconds = 60
        Next    = "DeleteDefaultVpcs"
      }
      ReportDefaultVpcsError = {
        Comment  = "Publish one warning that the default VPCs were not deleted, then go on."
        Type     = "Task"
        Resource = aws_lambda_function.aft_organizations_account_provisioning["delete_default_vpcs"].arn
        Parameters = {
          "move.$"               = "$.move"
          "default_vpcs_error.$" = "$.default_vpcs_error"
        }
        ResultPath = null
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.default_vpcs_report_error"
          Next        = "StartBaselinePoll"
        }]
        Next = "StartBaselinePoll"
      }
      CreateSucceeded = {
        Comment    = "Publish the CreateManagedAccount lifecycle event."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["publish_event"].arn
        ResultPath = null
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        End = true
      }
      UpdateAccount = {
        Comment    = "Look up the existing account by email."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["lookup_account"].arn
        ResultPath = "$.lookup"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "UpdateMoveAccount"
      }
      UpdateMoveAccount = {
        Comment    = "Move the account into its (possibly new) managed OU; idempotent if unchanged."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["move_account"].arn
        ResultPath = "$.move"
        Retry = [
          {
            # An OU that can't be vended into fails the request as it is.
            ErrorEquals = ["InvalidAccountRequestError"]
            MaxAttempts = 0
          },
          {
            ErrorEquals     = ["States.ALL"]
            IntervalSeconds = 5
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "UpdateStartBaselinePoll"
      }
      UpdateStartBaselinePoll = {
        Comment = "Record the execution start time and timeout; the baseline poll ends its control wait before the execution times out."
        Type    = "Pass"
        Parameters = {
          "execution_start_time.$" = "$$.Execution.StartTime"
          timeout_seconds          = var.aft_organizations_provisioning_timeout_seconds
        }
        ResultPath = "$.poll_window"
        Next       = "UpdatePollBaseline"
      }
      # No Parameters or InputPath: the Lambda reads the previous poll's result
      # ($.baseline) and $.poll_window from the full state input.
      UpdatePollBaseline = {
        Comment    = "Wait for the baseline, then the OU's controls, to settle (re-enroll after an OU move)."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["baseline_status"].arn
        ResultPath = "$.baseline"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "UpdateBaselineChoice"
      }
      UpdateBaselineChoice = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.baseline.is_failed"
            BooleanEquals = true
            Next          = "NotifyFailure"
          },
          {
            Or = [
              {
                And = [
                  {
                    Variable      = "$.baseline.is_complete"
                    BooleanEquals = true
                  },
                  {
                    Variable      = "$.baseline.controls_settled"
                    BooleanEquals = true
                  }
                ]
              },
              {
                Variable      = "$.baseline.controls_wait_expired"
                BooleanEquals = true
              }
            ]
            Next = "UpdateValidateGovernance"
          }
        ]
        Default = "UpdateWaitBaseline"
      }
      # The poll backs off from 30 s to 300 s between polls (POLL_WAIT_* in
      # aft_common/organizations_provisioning.py).
      UpdateWaitBaseline = {
        Type        = "Wait"
        SecondsPath = "$.baseline.next_wait_seconds"
        Next        = "UpdatePollBaseline"
      }
      UpdateValidateGovernance = {
        Comment    = "Compare the account's baselines and controls with its OU's."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["validate_governance"].arn
        ResultPath = "$.governance"
        Retry = [{
          ErrorEquals = ["GovernanceValidationError"]
          MaxAttempts = 0
          }, {
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        Next = "UpdateSucceeded"
      }
      UpdateSucceeded = {
        Comment    = "Publish the UpdateManagedAccount lifecycle event."
        Type       = "Task"
        Resource   = aws_lambda_function.aft_organizations_account_provisioning["publish_event"].arn
        ResultPath = null
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyFailure"
        }]
        End = true
      }
      # Every failure of both branches comes here: a step's Catch (the error is
      # in $.error), a failed CreateAccount request or a failed baseline. The step sends the one notification of
      # the execution; the step Lambdas send none, so a retried attempt is
      # never reported.
      NotifyFailure = {
        Comment  = "Send one failure notification with the error, then fail the execution with it."
        Type     = "Task"
        Resource = aws_lambda_function.aft_organizations_account_provisioning["notify_failure"].arn
        Parameters = {
          "execution_arn.$" = "$$.Execution.Id"
          "state.$"         = "$"
        }
        ResultPath = "$.failure"
        Retry = [{
          ErrorEquals     = ["States.ALL"]
          IntervalSeconds = 5
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.notify_error"
          Next        = "FailNotNotified"
        }]
        Next = "FailProvisioning"
      }
      FailProvisioning = {
        Type      = "Fail"
        ErrorPath = "$.failure.error"
        CausePath = "$.failure.cause"
      }
      FailNotNotified = {
        Type  = "Fail"
        Error = "AccountProvisioningFailed"
        Cause = "Organizations account provisioning failed, and the failure notification Lambda failed; see $.error in the execution history"
      }
      UnsupportedOperation = {
        Type  = "Fail"
        Error = "UnsupportedOperation"
        Cause = "operation must be ADD or UPDATE"
      }
    }
  })
}
