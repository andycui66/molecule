#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.


import pytest
from pytest_mock import MockerFixture

from molecule import config
from molecule.command import destroy


@pytest.fixture()
def _patched_ansible_destroy(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.destroy")


@pytest.fixture()
def _patched_destroy_setup(mocker):
    return mocker.patch("molecule.command.destroy.Destroy._setup")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.mark.skip(reason="destroy not running for delegated")
def test_execute(
    mocker: MockerFixture,
    caplog,
    patched_config_validate,
    _patched_ansible_destroy,
    config_instance: config.Config,
):
    d = destroy.Destroy(config_instance)
    d.execute()

    assert "destroy" in caplog.text

    assert "verify" in caplog.text

    _patched_ansible_destroy.assert_called_once_with()

    assert not config_instance.state.converged
    assert not config_instance.state.created


@pytest.mark.parametrize(
    "config_instance",
    ["command_driver_delegated_section_data"],
    indirect=True,
)
def test_execute_skips_when_destroy_strategy_is_never(
    _patched_destroy_setup,
    caplog,
    _patched_ansible_destroy,
    config_instance: config.Config,
):
    config_instance.command_args = {"destroy": "never"}

    d = destroy.Destroy(config_instance)
    d.execute()

    msg = "Skipping, '--destroy=never' requested."
    assert msg in caplog.text

    assert not _patched_ansible_destroy.called
