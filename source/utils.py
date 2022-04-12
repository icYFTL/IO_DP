def yes_no(question: str, question_formatter=print) -> bool:
    question += ' (y/n)'
    while True:
        question_formatter(question)
        result = input('> ')
        if result.lower().strip() not in ('y', 'n'):
            continue

        return result == 'y'
