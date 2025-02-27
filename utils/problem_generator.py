import json

class BaseParser:
    def __init__(self, metadata: dict):
        """
        metadata: {
            "task_name": str,
            "difficulty": str,
            "description": str,
            "function_name": str,
            "inputs": [ {"name": str, "type": str}, ... ],
            "outputs": [ {"name": str, "type": str}, ... ]
        }
        """
        self.problemName = metadata.get("task_name", "")
        self.functionName = metadata.get("function_name", "")
        self.inputFields = metadata.get("inputs", [])
        self.outputFields = metadata.get("outputs", [])
        self.difficulty = metadata.get("difficulty", "")
        self.description = metadata.get("description", "")

    def map_type_to_cpp(self, type_str: str) -> str:
        mapping = {
            "int": "int",
            "float": "float",
            "string": "std::string",
            "bool": "bool",
            "list<int>": "std::vector<int>",
            "list<float>": "std::vector<float>",
            "list<string>": "std::vector<std::string>",
            "list<bool>": "std::vector<bool>",
            "list<list<int>>": "std::vector<std::vector<int>>",
            "list<list<float>>": "std::vector<std::vector<float>>",
            "list<list<string>>": "std::vector<std::vector<std::string>>",
            "list<list<bool>>": "std::vector<std::vector<bool>>",
        }
        return mapping.get(type_str, "unknown")

    def map_type_to_rust(self, type_str: str) -> str:
        mapping = {
            "int": "i32",
            "float": "f64",
            "string": "String",
            "bool": "bool",
            "list<int>": "Vec<i32>",
            "list<float>": "Vec<f64>",
            "list<string>": "Vec<String>",
            "list<bool>": "Vec<bool>",
        }
        return mapping.get(type_str, "unknown")

    def map_type_to_java(self, type_str: str) -> str:
        mapping = {
            "int": "int",
            "float": "float",
            "string": "String",
            "bool": "boolean",
            "list<int>": "List<Integer>",
            "list<float>": "List<Float>",
            "list<string>": "List<String>",
            "list<bool>": "List<Boolean>",
        }
        return mapping.get(type_str, "unknown")


class ProblemDefinitionParser(BaseParser):
    """
    Генерирует шаблон функции для решения задачи на различных языках.
    """

    def generate_cpp(self) -> str:
        inputs = ", ".join(
            [f"{self.map_type_to_cpp(field['type'])} {field['name']}" for field in self.inputFields]
        )
        return f"""{self.map_type_to_cpp(self.outputFields[0]['type'])} {self.functionName}({inputs}) {{
    // Здесь будет реализована логика
    return result;
}}"""

    def generate_js(self) -> str:
        inputs = ", ".join([field["name"] for field in self.inputFields])
        return f"""function {self.functionName}({inputs}) {{
    // Здесь будет реализована логика
    return result;
}}"""

    def generate_rust(self) -> str:
        inputs = ", ".join(
            [f"{field['name']}: {self.map_type_to_rust(field['type'])}" for field in self.inputFields]
        )
        output_type = self.map_type_to_rust(self.outputFields[0]['type'])
        return f"""fn {self.functionName}({inputs}) -> {output_type} {{
    // Здесь будет реализована логика
    result
}}"""

    def generate_java(self) -> str:
        inputs = ", ".join(
            [f"{self.map_type_to_java(field['type'])} {field['name']}" for field in self.inputFields]
        )
        return f"""public static {self.map_type_to_java(self.outputFields[0]['type'])} {self.functionName}({inputs}) {{
    // Здесь будет реализована логика
    return result;
}}"""


class FullProblemDefinitionParser(BaseParser):
    """
    Генерирует полный шаблон программы (с функцией main, чтением входных данных из потока ввода и выводом результата)
    для различных языков.

    Дополнительно принимает список тестовых примеров в параметре metadata (опционально):
      "testCases": [ {"input": ..., "output": ...}, ... ]
    """

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        self.testCases = metadata.get("testCases", [])

    def generate_cpp(self) -> str:
        input_reads_list = []
        for i, field in enumerate(self.inputFields):
            if field["type"].startswith("list<list<"):
                code = (
                    f"std::string line_{i};\n"
                    f"std::getline(std::cin, line_{i});\n"
                    f"std::istringstream iss_{i}(line_{i});\n"
                    f"int outer_size_{field['name']}; iss_{i} >> outer_size_{field['name']};\n"
                    f"{self.map_type_to_cpp(field['type'])} {field['name']}(outer_size_{field['name']});\n"
                    f"for (int k_{i} = 0; k_{i} < outer_size_{field['name']}; k_{i}++) {{\n"
                    f"    std::string inner_line_{i};\n"
                    f"    std::getline(std::cin, inner_line_{i});\n"
                    f"    std::istringstream inner_iss_{i}(inner_line_{i});\n"
                    f"    int inner_size_{field['name']}; inner_iss_{i} >> inner_size_{field['name']};\n"
                    f"    {field['name']}[k_{i}].resize(inner_size_{field['name']});\n"
                    f"    std::string elems_line_{i};\n"
                    f"    std::getline(std::cin, elems_line_{i});\n"
                    f"    std::istringstream elems_{i}(elems_line_{i});\n"
                    f"    for (int j_{i} = 0; j_{i} < inner_size_{field['name']}; j_{i}++) elems_{i} >> {field['name']}[k_{i}][j_{i}];\n"
                    f"}}"
                )
            elif field["type"].startswith("list<"):
                code = (
                    f"std::string line_{i};\n"
                    f"std::getline(std::cin, line_{i});\n"
                    f"std::istringstream iss_{i}(line_{i});\n"
                    f"int size_{field['name']}; iss_{i} >> size_{field['name']};\n"
                    f"{self.map_type_to_cpp(field['type'])} {field['name']}(size_{field['name']});\n"
                    f"std::string elems_line_{i};\n"
                    f"std::getline(std::cin, elems_line_{i});\n"
                    f"std::istringstream elems_{i}(elems_line_{i});\n"
                    f"for (int j_{i} = 0; j_{i} < size_{field['name']}; j_{i}++) elems_{i} >> {field['name']}[j_{i}];"
                )
            else:
                code = (
                    f"std::string line_{i};\n"
                    f"std::getline(std::cin, line_{i});\n"
                    f"std::istringstream iss_{i}(line_{i});\n"
                    f"{self.map_type_to_cpp(field['type'])} {field['name']};\n"
                    f"iss_{i} >> {field['name']};"
                )
            input_reads_list.append(code)
        input_reads_code = "\n  ".join(input_reads_list)

        output_type = self.map_type_to_cpp(self.outputFields[0]['type'])
        func_call = f"{output_type} result = {self.functionName}(" + ", ".join(
            [field["name"] for field in self.inputFields]
        ) + ");"

        has_matrix_output = output_type.startswith("std::vector<std::vector<")
        matrix_to_string_func = ""
        if has_matrix_output:
            matrix_to_string_func = """
        std::string matrixToString(const std::vector<std::vector<int>>& matrix) {
            std::ostringstream oss;
            for (const auto& row : matrix) {
                for (const auto& elem : row) {
                    oss << elem << " ";
                }
                oss << "\\n";
            }
            return oss.str();
        }
        """
        return f"""#include <iostream>
    #include <sstream>
    #include <vector>
    #include <string>
    #include <algorithm>
    {matrix_to_string_func}
    ##USER_CODE_HERE##

    int main() {{
      {input_reads_code}
      {func_call}
      {"std::cout << matrixToString(result) << std::endl;" if has_matrix_output else "std::cout << result << std::endl;"}
      return 0;
    }}
    """

    def generate_js(self) -> str:
        # Чтение из стандартного ввода с помощью Node.js (синхронное чтение из '/dev/stdin')
        input_reads_list = []
        for field in self.inputFields:
            if field["type"].startswith("list<"):
                code = (
                    f"const {field['name']} = (function() {{\n"
                    f"    const line = inputLines.shift();\n"
                    f"    const size = parseInt(line.trim());\n"
                    f"    const elems = inputLines.shift().trim().split(/\\s+/).map(Number);\n"
                    f"    return elems.slice(0, size);\n"
                    f"}})();"
                )
            else:
                code = f"const {field['name']} = parseInt(inputLines.shift().trim());"
            input_reads_list.append(code)
        input_reads_code = "\n  ".join(input_reads_list)
        func_call = f"const result = {self.functionName}(" + ", ".join(
            [field["name"] for field in self.inputFields]
        ) + ");"
        return f"""##USER_CODE_HERE##

const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf8');
const inputLines = input.trim().split('\\n');
{input_reads_code}
{func_call}
console.log(result);
"""

    def generate_rust(self) -> str:
        # Чтение из стандартного ввода в Rust
        input_reads_list = []
        for field in self.inputFields:
            if field["type"].startswith("list<"):
                code = (
                    f"let mut input_line = String::new();\n"
                    f"std::io::stdin().read_line(&mut input_line).expect(\"Failed to read line\");\n"
                    f"let size_{field['name']}: usize = input_line.trim().parse().unwrap();\n"
                    f"input_line.clear();\n"
                    f"std::io::stdin().read_line(&mut input_line).expect(\"Failed to read line\");\n"
                    f"let {field['name']}: {self.map_type_to_rust(field['type'])} = input_line.trim()\n"
                    f"    .split_whitespace()\n"
                    f"    .take(size_{field['name']})\n"
                    f"    .map(|s| s.parse().unwrap())\n"
                    f"    .collect();"
                )
            else:
                code = (
                    f"let mut input_line = String::new();\n"
                    f"std::io::stdin().read_line(&mut input_line).expect(\"Failed to read line\");\n"
                    f"let {field['name']}: {self.map_type_to_rust(field['type'])} = input_line.trim().parse().unwrap();"
                )
            input_reads_list.append(code)
        input_reads_code = "\n  ".join(input_reads_list)
        func_call = f"let result = {self.functionName}(" + ", ".join(
            [field["name"] for field in self.inputFields]
        ) + ");"
        return f"""use std::io;

##USER_CODE_HERE##

fn main() {{
    {input_reads_code}
    {func_call}
    println!("{{}}", result);
}}
"""

    def generate_java(self) -> str:
        # Чтение из стандартного ввода с помощью Scanner
        input_reads_list = []
        for field in self.inputFields:
            if field["type"].startswith("list<"):
                java_type = self.map_type_to_java(field["type"])
                code = (
                    f"int size_{field['name']} = Integer.parseInt(scanner.nextLine().trim());\n"
                    f"{java_type} {field['name']} = new ArrayList<>();\n"
                    f"if(size_{field['name']} > 0) {{\n"
                    f"    String[] parts = scanner.nextLine().trim().split(\"\\\\s+\");\n"
                    f"    for (String part : parts) {{\n"
                    f"        {field['name']}.add(Integer.parseInt(part));\n"
                    f"    }}\n"
                    f"}}"
                )
            else:
                java_type = self.map_type_to_java(field["type"])
                if java_type == "int":
                    code = f"int {field['name']} = Integer.parseInt(scanner.nextLine().trim());"
                else:
                    code = f"{java_type} {field['name']} = {java_type}.valueOf(scanner.nextLine().trim());"
            input_reads_list.append(code)
        input_reads_code = "\n        ".join(input_reads_list)
        func_call = f"{self.map_type_to_java(self.outputFields[0]['type'])} result = {self.functionName}(" + ", ".join(
            [field["name"] for field in self.inputFields]
        ) + ");"
        return f"""import java.util.*;

public class Main {{

    ##USER_CODE_HERE##

    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        {input_reads_code}
        {func_call}
        System.out.println(result);
        scanner.close();
    }}
}}
"""


def problem_generator(metadata):
    # Пример метаданных
    #     metadata = {
    #     "task_name": "Two sum",
    #     "difficulty": "Easy",
    #     "description": "шоитк аутшоау аоутоащцву уцащв уцщтвуцц ",
    #     "function_name": "two_sum",
    #     "inputs": [
    #         {
    #             "name": "num1",
    #             "type": "int"
    #         },
    #         {
    #             "name": "number2",
    #             "type": "int"
    #         }
    #     ],
    #     "outputs": [
    #         {
    #             "name": "result",
    #             "type": "int"
    #         }
    #     ]
    # }

    parser = ProblemDefinitionParser(metadata)
    full_parser = FullProblemDefinitionParser(metadata)

    boilerplate_codes = {
        "cppTemplate": parser.generate_cpp(),
        "jsTemplate": parser.generate_js(),
        "rustTemplate": parser.generate_rust(),
        "javaTemplate": parser.generate_java(),
        "fullCpp": full_parser.generate_cpp(),
        "fullJs": full_parser.generate_js(),
        "fullRust": full_parser.generate_rust(),
        "fullJava": full_parser.generate_java()
    }

    return boilerplate_codes