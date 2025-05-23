from patchwork.common.utils.utils import exclude_none_dict
from patchwork.step import Step
from patchwork.steps.CommitChanges.CommitChanges import CommitChanges
from patchwork.steps.CreatePR.CreatePR import CreatePR
from patchwork.steps.PR.typed import PRInputs, PROutputs
from patchwork.steps.PreparePR.PreparePR import PreparePR
from autoremediate.steps.CreatePR.CreatePR import CreatePR as BitbucketCreatePR


class PR(Step, input_class=PRInputs, output_class=PROutputs):
    def __init__(self, inputs):
        super().__init__(inputs)
        self.inputs = inputs

    def run(self):
        if not self.inputs.get("bitbucket_key"):
            return super().run()
        commit_changes = CommitChanges(self.inputs)
        commit_changes_output = commit_changes.run()
        self.set_status(commit_changes.status, commit_changes.status_message)

        prepare_pr = PreparePR(self.inputs)
        prepare_pr_output = prepare_pr.run()
        self.set_status(prepare_pr.status, prepare_pr.status_message)
        create_pr = BitbucketCreatePR(
            dict(
                base_branch=commit_changes_output.get("base_branch"),
                target_branch=commit_changes_output.get("target_branch"),
                pr_body=prepare_pr_output.get("pr_body"),
                **self.inputs,
            )
        )
        create_pr_outputs = create_pr.run()
        self.set_status(create_pr.status, create_pr.status_message)

        return exclude_none_dict(
            dict(
                base_branch=commit_changes_output.get("base_branch"),
                target_branch=commit_changes_output.get("target_branch"),
                pr_url=create_pr_outputs.get("pr_url"),
                pr_number=create_pr_outputs.get("pr_number"),
                pr_title=prepare_pr_output.get("pr_title"),
                pr_body=prepare_pr_output.get("pr_body"),
            )
        )
