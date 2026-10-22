from scripts.check_full import rule_commands, gate_status


def test_docker_validator_executes_both_syntax_and_every_rule_fixture():
    commands=rule_commands(None,True)
    assert len(commands)==2
    assert commands[0][-3:]==['check','rules','/rules/observability.yml']
    assert commands[1][-3:]==['test','rules','/tests.yml']


def test_missing_all_validators_cannot_pass_the_full_gate():
    assert rule_commands(None,False)==[]
    assert gate_status(0,['required service gate not executed'])==('INCOMPLETE',2)
