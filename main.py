from source.input_handler import resolve_inputs
from source.task import Task

if __name__ == '__main__':
    inputs = resolve_inputs()
    cp = None
    if isinstance(inputs['r'], str):
        l, r = tuple(map(int, inputs['r'].split('-')))
        cp = range(l, r + 1)
    elif isinstance(inputs['r'], int):
        cp = range(inputs['r'], inputs['r'] + 1)
    else:
        raise ValueError('Invalid "r" passed')

    days = inputs['calculate_days']
    del inputs['calculate_days']

    for r in cp:
        print(f'Resolving with R={r}')
        inputs['r'] = r

        t = Task(**inputs)
        t.calculate(days)
        del t
