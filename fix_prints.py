
def fix_print_statements(content):
    # Pattern to match multi-line print statements that end with a line containing ')  # noqa: T201'
    # We'll look for lines that start with whitespace and 'print(' and then capture until the line that has ')  # noqa: T201'
    # This is a bit complex, so we'll do a simpler approach: replace the pattern of a print that spans multiple lines.
    # We'll look for: print(\n    ...\n)  # noqa: T201
    # and replace with: print(...)  # noqa: T201
    # But note: the inner content may have multiple lines.

    # We'll use a regex that matches from 'print(' to the next line that ends with ')  # noqa: T201'
    # and then replace the entire block with a single line.

    # However, note that there might be nested parentheses.

    # Instead, we can split the content by lines and then rebuild.

    lines = content.splitlines()
    i = 0
    fixed_lines = []
    while i < len(lines):
        line = lines[i]
        # Check if this line starts a print statement that is multi-line
        if line.rstrip().startswith('print(') and not line.rstrip().endswith(')'):
            # Start of a multi-line print
            # Collect lines until we find a line that ends with ')  # noqa: T201'
            print_lines = [line]
            j = i + 1
            while j < len(lines):
                print_lines.append(lines[j])
                if lines[j].rstrip().endswith(')  # noqa: T201'):
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
