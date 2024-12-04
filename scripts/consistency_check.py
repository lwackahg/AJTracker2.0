import ast
import os

# Define the expected naming conventions
EXPECTED_NAMING = {
    'User': 'UserId',
    'Book': 'BookId',
    'Movie': 'movieID'
}

EXPECTED_ATTRIBUTES = {
    'WatchHistory': ['userID', 'movieID'],
    'Watchlist': ['userID', 'movieID'],
    'User': ['UserId'],
    'Book': ['BookId'],
    'Movie': ['movieID']
}

class AttributeNameChecker(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_ClassDef(self, node):
        class_name = node.name
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        attribute_name = target.id
                        # Check if attribute name matches expected naming
                        if class_name in EXPECTED_NAMING:
                            expected_name = EXPECTED_NAMING[class_name]
                            if attribute_name != expected_name:
                                self.issues.append((class_name, attribute_name, expected_name))
        self.generic_visit(node)


class QueryFilterChecker(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'filter_by':
            model_name = None
            if isinstance(node.func.value, ast.Name):
                model_name = node.func.value.id
            elif isinstance(node.func.value, ast.Attribute):
                model_name = node.func.value.attr
            if model_name:
                for keyword in node.keywords:
                    attribute_name = keyword.arg
                    if model_name in EXPECTED_ATTRIBUTES:
                        if attribute_name not in EXPECTED_ATTRIBUTES[model_name]:
                            self.issues.append((model_name, attribute_name))
        self.generic_visit(node)


def check_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=file_path)
    checker = AttributeNameChecker()
    checker.visit(tree)
    return checker.issues


def check_directory(directory_path):
    all_issues = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                issues = check_file(file_path)
                if issues:
                    all_issues.extend([(file_path, *issue) for issue in issues])
    return all_issues


def check_file_for_queries(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=file_path)
    checker = QueryFilterChecker()
    checker.visit(tree)
    return checker.issues


def check_directory_for_queries(directory_path):
    all_issues = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                issues = check_file_for_queries(file_path)
                if issues:
                    all_issues.extend([(file_path, *issue) for issue in issues])
    return all_issues


def main():
    project_dir = os.path.join(os.path.dirname(__file__), '..')
    attribute_issues = check_directory(project_dir)
    query_issues = check_directory_for_queries(project_dir)
    if attribute_issues:
        print("Inconsistencies found:")
        for issue in attribute_issues:
            print(f"File: {issue[0]}, Class: {issue[1]}, Attribute: {issue[2]}, Expected: {issue[3]}")
    else:
        print("No inconsistencies found.")
    if query_issues:
        print("Query filter inconsistencies found:")
        for issue in query_issues:
            print(f"File: {issue[0]}, Model: {issue[1]}, Attribute: {issue[2]}")
    else:
        print("No query filter inconsistencies found.")


if __name__ == "__main__":
    main()
