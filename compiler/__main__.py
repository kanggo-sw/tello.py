import compiler


def main(file: str):
    program_loader = compiler.Loader.from_file(file)

    for command in program_loader.query():
        print(command)

        # TODO: Implement backend
