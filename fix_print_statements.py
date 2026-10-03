#!/usr/bin/env python3

def fix_print_statements(content):
    lines = content.splitlines()
    i = 0
    fixed_lines = []
    while i < len(lines):
        line = lines[i]
        # Check if this line starts a print statement (after stripping leading spaces)
        stripped = line.lstrip()
        if stripped.startswith('print(') and not stripped.rstrip().endswith(')'):
            # Start of a multi-line print statement
            # Collect lines until we find a line that contains ')'
            print_lines = [line]
            j = i + 1
            while j < len(lines):
                print_lines.append(lines[j])
                if ')' in lines[j]:
                    break
                j += 1
            # Now we have the print statement from i to j (inclusive)
            # We want to convert it to a single line.
            # Join the lines, then remove the newline and extra spaces.
            # We'll keep the indentation of the first line.
            indent = len(line) - len(line.lstrip())
            # Join the lines with a space, then strip extra spaces.
            combined = ' '.join([l.strip() for l in print_lines])
            # Now we need to ensure that the parentheses are balanced? We'll trust the original.
            # But note: the combined string might have extra spaces.
            # We'll just use the combined string as the new line.
            # Now, check if the line after j has a noqa comment for T201
            noqa_line = None
            if j + 1 < len(lines):
                next_line = lines[j + 1]
                if '# noqa: T201' in next_line:
                    noqa_line = next_line
                    # We will skip this line in the output
                    j += 1  # skip the noqa line
            # If we found a noqa line, append it to the combined line
            if noqa_line:
                # Extract the noqa comment (we assume it's the only thing on the line or at the end)
                # We'll just append a space and the noqa comment
                combined += ' ' + noqa_line.strip()
            else:
                # If no noqa line, add the noqa comment
                combined += '  # noqa: T201'
            fixed_lines.append(' ' * indent + combined)
            i = j + 1
        else:
            fixed_lines.append(line)
            i += 1

    return '\n'.join(fixed_lines) + '\n'

def main():
    filename = r'D:\Mi unidad\Proyectos\Dorama Studio AI\apply_patch_fixed.py'
    with open(filename) as f:
        content = f.read()
    fixed_content = fix_print_statements(content)
    with open(filename, 'w') as f:
        f.write(fixed_content)

if __name__ == '__main__':
    main()
