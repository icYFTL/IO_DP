import yaml


def resolve_inputs() -> dict:
    args = None

    with open("inputs.yaml", "r") as stream:
        try:
            args = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ValueError('Invalid inputs.yaml passed')

    return args

