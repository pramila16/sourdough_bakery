import json
import yaml
from pathlib import Path
from typing import Dict, Any
from patchwork.patchflows.AutoFix.AutoFix import AutoFix as PatchworkAutoFix
from patchwork.logger import init_cli_logger
from autoremediate.steps.PR.PR import PR as BitBucketPR
from patchwork.patchflows.AutoFix.AutoFix import Compatibility
from patchwork.steps.ExtractCode.ExtractCode import ExtractCode
from patchwork.steps.LLM.LLM import LLM
from patchwork.steps.ModifyCode.ModifyCode import ModifyCode
from patchwork.steps.ScanSemgrep.ScanSemgrep import ScanSemgrep


class AutoFix(PatchworkAutoFix):
    def __init__(self, inputs: Dict[str, Any]):
        self.inputs = inputs
        logger = init_cli_logger(log_level="TRACE", plain=False)
        config = self._load_config()
        final_inputs = {**config, **(self.inputs or {})}
        final_inputs["logger"] = logger
        super().__init__(inputs=final_inputs)
        print("initialised")

    def _load_config(self) -> Dict[str, Any]:
        config_path = Path(__file__).parent / 'defaults.yml'
        try:
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Invalid YAML in defaults.yml: {str(e)}")

    def run(self) -> dict:
        if not self.inputs.get("bitbucket_key"):
            return super().run()
        outputs = ScanSemgrep(self.inputs).run()
        self.inputs.update(outputs)
        outputs = ExtractCode(self.inputs).run()
        self.inputs.update(outputs)

        for i in range(self.n):
            self.inputs["prompt_values"] = outputs.get("files_to_patch", [])
            outputs = LLM(self.inputs).run()
            self.inputs.update(outputs)

            for extracted_response in self.inputs["extracted_responses"]:
                response_compatibility = Compatibility.from_str(
                    extracted_response.get("compatibility", "UNKNOWN").strip()
                )
                if response_compatibility < self.compatibility_threshold:
                    extracted_response.pop("patch", None)

            outputs = ModifyCode(self.inputs).run()
            self.inputs.update(outputs)

            if i == self.n - 1:
                break

            # validation
            self.inputs.pop("sarif_file_path", None)
            outputs = ScanSemgrep(self.inputs).run()
            self.inputs.update(outputs)
            outputs = ExtractCode(self.inputs).run()
            self.inputs.update(outputs)
            if self.inputs.get("prompt_value_file") is not None:
                with open(self.inputs["prompt_value_file"], "r") as fp:
                    vulns = json.load(fp)
                if len(vulns) < 1:
                    break
        outputs = BitBucketPR(self.inputs).run()
        self.inputs.update(outputs)

        return self.inputs


