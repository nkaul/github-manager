import json

import pytest

from app.pretest import aws_scratch


def test_provisioning_rejects_expanded_template_scope(tmp_path, monkeypatch):
    template = json.loads(aws_scratch.TEMPLATE.read_text())
    template["Resources"]["PrivilegedRole"] = {"Type": "AWS::IAM::Role"}
    path = tmp_path / "stack.json"
    path.write_text(json.dumps(template))
    monkeypatch.setattr(aws_scratch, "TEMPLATE", path)
    with pytest.raises(ValueError, match="approved eight-resource scope"):
        aws_scratch.reviewed_template()


def test_private_ownership_file_cannot_be_overwritten(tmp_path):
    path = tmp_path / "ownership.json"
    aws_scratch.save_private(path, {"stack": "first"}, exclusive=True)
    with pytest.raises(FileExistsError):
        aws_scratch.save_private(path, {"stack": "second"}, exclusive=True)
    assert json.loads(path.read_text()) == {"stack": "first"}
    assert path.stat().st_mode & 0o777 == 0o600
